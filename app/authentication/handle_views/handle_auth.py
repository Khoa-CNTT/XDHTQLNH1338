from core.__Include_Library import *
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.mixins import AuthenticationPermissionMixin
from rest_framework import status
from authentication.serializers import UserLoginSerializer
from django.contrib.auth.hashers import make_password
import jwt
from drf_yasg.utils import swagger_auto_schema
from web_01.models import Customer, Session, Table,Invoice


class LoginView(APIView):
    parser_classes = (JSONParser, MultiPartParser)

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: "Successful login, returns access token and session info.",
            404: "Table not found.",
            401: "Invalid credentials.",
        },
    )
    def post(self, request):
        """
        Logs in a user and creates a session for the table.

        Args:
            username (str): The username.
            first_name (str): The first name.
            last_name (str): The last name.

        Returns:
            - 200: On successful login, returns access token and session info.
            - 404: If table not found.
            - 401: If credentials are invalid.
        """
        # 🛡 Validate input
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        first_name = serializer.validated_data["first_name"]
        last_name = serializer.validated_data["last_name"]
        password = '123123'  # Mật khẩu mặc định nếu tạo tài khoản mới

        # 🗂 Lấy table_number từ URL query parameter
        table_number = request.data.get('table_number')
        if not table_number:
            return Response({"error": "Thiếu tên bàn (table_number)!"}, status=status.HTTP_400_BAD_REQUEST)

        # 🗂 Kiểm tra bàn theo table_number
        try:
            table = Table.objects.get(table_number=table_number)
        except Table.DoesNotExist:
            return Response({"error": "Bàn không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)

        if table.status != 'available':
            return Response({"error": "Bàn không có sẵn!"}, status=status.HTTP_400_BAD_REQUEST)

        table.status = 'occupied'
        table.save()
        # 🗂 Kiểm tra hoặc tạo tài khoản User
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                'password': make_password(password),
                'first_name': first_name,
                'last_name': last_name
            }
        )

        # 🗂 Kiểm tra hoặc tạo Customer
        customer, customer_created = Customer.objects.get_or_create(
            user=user,
            defaults={'loyalty_points': 0}
        )

        # 🗂 Kiểm tra Session đã tồn tại chưa
        active_session = Session.objects.filter(customer=customer, table=table, status='active').first()
        if active_session:
            session = active_session
        else:
            # 🗂 Tạo mới Session nếu chưa có
            session = Session.objects.create(customer=customer, table=table)

        # 🛡 Tạo JWT token
        expiration_time = datetime.utcnow() + timedelta(days=30)
        payload = {
            "id": user.id,
            "username": user.username,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "session_id": session.id,
            "session_status": session.status,
            "table_number": session.table.table_number,
            "exp": expiration_time,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # 🛡 Set cookie và trả về response
        response = Response()
        response.set_cookie(
            key="rms_access_token",
            value=token,
            httponly=True,
            max_age=30 * 24 * 60 * 60
        )
        response.data = {
            "rms_access_token": token,
            "message": "Đăng nhập thành công",
            "session": {
                "session_id": session.id,
                "table_number": session.table.table_number,
                "status": session.status,
                "started_at": session.started_at,
            }
        }
        response.status_code = status.HTTP_200_OK

        return response


class SessionView(AuthenticationPermissionMixin, APIView):
    parser_classes = (JSONParser, MultiPartParser)

    def get(self, request):
        customer = request.user.customer
        session = Session.objects.filter(customer=customer).order_by('-started_at').first()
        response = Response()
        response.data = {
            "message": "Thông tin session",
            "session": {
                "session_id": session.id,
                "table_number": session.table.table_number,
                "status": session.status,
                "started_at": session.started_at,
            }
        }
        response.status_code = status.HTTP_200_OK
        return response



class EndSessionView(AuthenticationPermissionMixin, APIView):
    parser_classes = (JSONParser, MultiPartParser)

    def get(self, request):
        customer = request.user.customer
        response = Response()
        session = Session.objects.filter(customer=customer).order_by('-started_at').first()
        session.table.status = 'available'
        session.ended_at = timezone.now()
        session.status = 'closed'
        session.save()
        session.table.save()
        response.status_code = status.HTTP_200_OK

        response.delete_cookie('rms_access_token')
        return response
    


