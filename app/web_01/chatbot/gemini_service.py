import google.generativeai as genai
from django.conf import settings
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
import json
import re
from web_01.models import Order, Product, Ingredient, Invoice, OrderDetail, InventoryLog
from django.utils.timezone import is_aware, make_aware
def safe_make_aware(dt):
    if settings.USE_TZ and not is_aware(dt):
        return make_aware(dt)
    return dt

class GeminiChatbot:
    def __init__(self):
        # Cấu hình Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Thiết lập system prompt
        self.system_prompt = """
        Bạn là trợ lý AI của nhà hàng, có khả năng truy vấn và phân tích dữ liệu từ hệ thống quản lý.
        Bạn có thể trả lời các câu hỏi về:
        1. Thống kê doanh thu (theo ngày, tuần, tháng)
        2. Thống kê tồn kho và cảnh báo nguyên liệu sắp hết
        3. Thống kê món ăn bán chạy
        4. Thông tin về đơn hàng và bàn
        
        Hãy trả lời ngắn gọn, chính xác và thân thiện.
        
        QUAN TRỌNG: Khi trả lời, hãy sử dụng Markdown để định dạng câu trả lời:
        - Sử dụng **text** cho văn bản in đậm
        - Sử dụng *text* cho văn bản in nghiêng
        - Sử dụng # Heading cho tiêu đề lớn
        - Sử dụng ## Heading cho tiêu đề nhỏ hơn
        - Sử dụng - hoặc * cho danh sách không thứ tự
        - Sử dụng 1. 2. 3. cho danh sách có thứ tự
        - Sử dụng ```json cho khối mã JSON
        - Sử dụng | Cột 1 | Cột 2 | cho bảng
        
        Khi hiển thị dữ liệu số, hãy định dạng rõ ràng và dễ đọc.
        Khi hiển thị dữ liệu thống kê, hãy tổ chức thành bảng hoặc danh sách có cấu trúc.
        """
        
        # Khởi tạo chat history
        self.chat = self.model.start_chat(history=[])
        
    def get_inventory_stats(self):
        """Lấy thống kê tồn kho"""
        ingredients = Ingredient.objects.all()
        
        # Tìm các nguyên liệu sắp hết
        low_stock = []
        for ingredient in ingredients:
            if hasattr(ingredient, 'min_stock') and ingredient.quantity_in_stock <= ingredient.min_stock:
                low_stock.append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity_in_stock,
                    'unit': ingredient.unit
                })
            elif ingredient.quantity_in_stock <= 50:  # Ngưỡng mặc định nếu không có min_stock
                low_stock.append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity_in_stock,
                    'unit': ingredient.unit
                })
        
        # Thống kê nhập xuất kho gần đây
        recent_logs = InventoryLog.objects.all().order_by('-last_updated')[:10]
        recent_activities = []
        for log in recent_logs:
            action = "nhập" if log.change > 0 else "xuất"
            recent_activities.append({
                'ingredient': log.ingredient.name,
                'action': action,
                'quantity': abs(log.change),
                'date': log.last_updated.strftime('%d/%m/%Y %H:%M')
            })
        
        # Tổng hợp theo danh mục
        category_stats = {}
        for ingredient in ingredients:
            category = "Chưa phân loại"
            if hasattr(ingredient, 'category') and ingredient.category:
                category = ingredient.category.name
                
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_value': 0
                }
            
            category_stats[category]['count'] += 1
            if hasattr(ingredient, 'price'):
                category_stats[category]['total_value'] += ingredient.price * ingredient.quantity_in_stock
        
        return {
            'total_ingredients': ingredients.count(),
            'low_stock': low_stock,
            'recent_activities': recent_activities,
            'category_stats': category_stats
        }
    
    def get_sales_stats(self, period='today'):
        """Lấy thống kê doanh thu"""
        today = timezone.now().date()
        
        if period == 'today':
            start_date = today
            period_name = "hôm nay"
        elif period == 'yesterday':
            start_date = today - timedelta(days=1)
            period_name = "hôm qua"
        elif period == 'week':
            start_date = today - timedelta(days=7)
            period_name = "7 ngày qua"
        elif period == 'month':
            start_date = today.replace(day=1)
            period_name = "tháng này"
        else:
            start_date = today
            period_name = "hôm nay"
        
        # Doanh thu
        revenue = Invoice.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Số đơn hàng
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        )
        order_count = orders.count()
        
        # Doanh thu trung bình mỗi đơn
        avg_order_value = revenue / order_count if order_count > 0 else 0
        
        # Món bán chạy
        best_selling = OrderDetail.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        ).values('product__name').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-total_sold')[:5]
        
        # Thống kê theo trạng thái đơn hàng
        order_status = orders.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Thống kê theo giờ trong ngày (nếu là today)
        hourly_stats = []
        if period == 'today':
            for hour in range(24):
                hour_start = safe_make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()) + timedelta(hours=hour))
                hour_end = hour_start + timedelta(hours=1)
                
                hour_revenue = Invoice.objects.filter(
                    created_at__gte=hour_start,
                    created_at__lt=hour_end,
                    is_deleted=False
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                
                hour_orders = Order.objects.filter(
                    created_at__gte=hour_start,
                    created_at__lt=hour_end,
                    is_deleted=False
                ).count()
                
                hourly_stats.append({
                    'hour': f"{hour:02d}:00",
                    'revenue': hour_revenue,
                    'orders': hour_orders
                })
        
        return {
            'period': period_name,
            'revenue': revenue,
            'order_count': order_count,
            'avg_order_value': avg_order_value,
            'best_selling': list(best_selling),
            'order_status': list(order_status),
            'hourly_stats': hourly_stats
        }
    
    def get_table_stats(self):
        """Lấy thống kê về bàn"""
        from web_01.models import Table, Session
        
        # Tổng số bàn
        tables = Table.objects.all()
        total_tables = tables.count()
        
        # Số bàn theo trạng thái
        table_status = tables.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Các phiên đang hoạt động
        active_sessions = Session.objects.filter(status='active')
        active_session_count = active_sessions.count()
        
        # Thời gian trung bình của phiên
        avg_session_duration = 0
        completed_sessions = Session.objects.filter(
            status='closed', 
            ended_at__isnull=False
        )
        
        if completed_sessions.exists():
            total_duration = 0
            for session in completed_sessions:
                duration = (session.ended_at - session.started_at).total_seconds() / 60  # Phút
                total_duration += duration
            
            avg_session_duration = total_duration / completed_sessions.count()
        
        return {
            'total_tables': total_tables,
            'table_status': list(table_status),
            'active_sessions': active_session_count,
            'avg_session_duration': avg_session_duration
        }
    
    def format_data_for_display(self, data_type, data):
        """Định dạng dữ liệu để hiển thị đẹp hơn"""
        if data_type == 'inventory':
            # Định dạng dữ liệu tồn kho thành bảng markdown
            low_stock_table = "| Nguyên liệu | Số lượng tồn |\n| --- | --- |\n"
            for item in data['low_stock']:
                low_stock_table += f"| {item['name']} | {item['quantity']} {item['unit']} |\n"
            
            recent_activities_list = ""
            for item in data['recent_activities'][:5]:
                recent_activities_list += f"- {item['date']}: {item['action']} {item['quantity']} {item['ingredient']}\n"
            
            return {
                'summary': f"**Tổng số nguyên liệu:** {data['total_ingredients']}\n**Nguyên liệu sắp hết:** {len(data['low_stock'])} loại",
                'low_stock_table': low_stock_table,
                'recent_activities': recent_activities_list
            }
            
        elif data_type == 'sales':
            # Định dạng dữ liệu doanh thu
            best_selling_table = "| Sản phẩm | Số lượng | Doanh thu |\n| --- | --- | --- |\n"
            for item in data['best_selling']:
                best_selling_table += f"| {item['product__name']} | {item['total_sold']} | {item['revenue']:,}đ |\n"
            
            order_status_list = ""
            for status in data['order_status']:
                status_name = status['status']
                if status_name == 'pending': status_name = 'Chờ xử lý'
                elif status_name == 'in_progress': status_name = 'Đang làm'
                elif status_name == 'completed': status_name = 'Hoàn thành'
                elif status_name == 'cancelled': status_name = 'Đã hủy'
                
                order_status_list += f"- {status_name}: {status['count']} đơn\n"
            
            hourly_data = ""
            if data['hourly_stats']:
                hourly_data = "| Giờ | Doanh thu | Số đơn |\n| --- | --- | --- |\n"
                for hour in data['hourly_stats']:
                    if hour['orders'] > 0:
                        hourly_data += f"| {hour['hour']} | {hour['revenue']:,}đ | {hour['orders']} |\n"
            
            return {
                'summary': f"**Doanh thu {data['period']}:** {data['revenue']:,}đ\n**Số đơn hàng:** {data['order_count']}\n**Giá trị trung bình/đơn:** {data['avg_order_value']:,.0f}đ",
                'best_selling_table': best_selling_table,
                'order_status': order_status_list,
                'hourly_data': hourly_data
            }
            
        elif data_type == 'table':
            # Định dạng dữ liệu bàn
            table_status_list = ""
            for status in data['table_status']:
                status_name = status['status']
                if status_name == 'available': status_name = 'Trống'
                elif status_name == 'occupied': status_name = 'Đang sử dụng'
                elif status_name == 'reserved': status_name = 'Đã đặt'
                
                table_status_list += f"- {status_name}: {status['count']} bàn\n"
            
            return {
                'summary': f"**Tổng số bàn:** {data['total_tables']}\n**Phiên đang hoạt động:** {data['active_sessions']}\n**Thời gian trung bình/phiên:** {data['avg_session_duration']:.1f} phút",
                'table_status': table_status_list
            }
        
        return {}
    
    def process_query(self, user_message):
        """Xử lý câu hỏi của người dùng"""
        user_message_lower = user_message.lower()
        
        # Phân tích ý định của người dùng
        if "tồn kho" in user_message_lower or "nguyên liệu" in user_message_lower:
            # Truy vấn dữ liệu tồn kho
            inventory_data = self.get_inventory_stats()
            formatted_data = self.format_data_for_display('inventory', inventory_data)
            
            # Tạo context cho Gemini
            context = f"""
            # Thông tin tồn kho
            
            {formatted_data['summary']}
            
            ## Nguyên liệu sắp hết
            {formatted_data['low_stock_table']}
            
            ## Hoạt động nhập xuất gần đây
            {formatted_data['recent_activities']}
            """
            
        elif "doanh thu" in user_message_lower or "bán hàng" in user_message_lower:
            # Xác định khoảng thời gian
            period = 'today'
            if "hôm qua" in user_message_lower:
                period = 'yesterday'
            elif "tuần" in user_message_lower:
                period = 'week'
            elif "tháng" in user_message_lower:
                period = 'month'
            
            # Truy vấn dữ liệu doanh thu
            sales_data = self.get_sales_stats(period)
            formatted_data = self.format_data_for_display('sales', sales_data)
            
            # Tạo context cho Gemini
            context = f"""
            # Thống kê doanh thu {sales_data['period']}
            
            {formatted_data['summary']}
            
            ## Món bán chạy
            {formatted_data['best_selling_table']}
            
            ## Trạng thái đơn hàng
            {formatted_data['order_status']}
            """
            
            if formatted_data['hourly_data']:
                context += f"""
                ## Doanh thu theo giờ
                {formatted_data['hourly_data']}
                """
            
        elif "bàn" in user_message_lower or "phiên" in user_message_lower:
            # Truy vấn dữ liệu bàn
            table_data = self.get_table_stats()
            formatted_data = self.format_data_for_display('table', table_data)
            
            # Tạo context cho Gemini
            context = f"""
            # Thống kê bàn
            
            {formatted_data['summary']}
            
            ## Trạng thái bàn
            {formatted_data['table_status']}
            """
            
        else:
            # Trường hợp không xác định được ý định cụ thể
            context = """
            # Trợ giúp
            
            Tôi có thể giúp bạn với các thông tin sau:
            
            - **Tồn kho**: Kiểm tra tồn kho nguyên liệu, cảnh báo hết hàng
            - **Doanh thu**: Xem doanh thu theo ngày, tuần, tháng
            - **Bàn**: Kiểm tra trạng thái bàn, phiên hoạt động
            
            Hãy hỏi tôi về một trong các chủ đề trên!
            """
        
        # Gửi câu hỏi và context đến Gemini
        response = self.chat.send_message(
            f"System: {self.system_prompt}\n\nContext: {context}\n\nUser: {user_message}"
        )
        
        # Đảm bảo phản hồi được định dạng đúng
        reply = response.text
        
        # Thêm định dạng cho các bảng nếu cần
        reply = self.enhance_markdown_tables(reply)
        
        return reply
    
    def enhance_markdown_tables(self, text):
        """Cải thiện định dạng bảng Markdown"""
        # Tìm các bảng Markdown
        table_pattern = r"(\|.+?\|(?:\n\|.+?\|)+)"
        
        def format_table(match):
            table = match.group(1)
            # Thêm class cho bảng để styling
            return f"\n{table}\n"
        
        enhanced_text = re.sub(table_pattern, format_table, text)
        return enhanced_text

    def save_chat_history(self, user_message, bot_reply):
        """Lưu lịch sử chat vào database"""
        from web_01.models import ChatHistory
        
        ChatHistory.objects.create(
            user_message=user_message,
            bot_reply=bot_reply
        )
