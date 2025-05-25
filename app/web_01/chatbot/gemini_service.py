import re
import json
import google.generativeai as genai
from django.conf import settings
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta, datetime

from web_01.models import (
    ChatHistory, Invoice, Order, OrderDetail,
    Ingredient, InventoryLog, Table, Session, Product
)


def safe_make_aware(dt):
    """Hàm hỗ trợ để đảm bảo datetime có timezone"""
    if settings.USE_TZ:
        from django.utils.timezone import make_aware
        return make_aware(dt)
    return dt


class GeminiChatbot:
    def __init__(self):
        # Cấu hình Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Thiết lập system prompt
        self.system_prompt = """
Bạn là **Bot RMS**, trợ lý AI siêu thông minh nhưng hơi "mặn mà" của hệ thống quản lý nhà hàng.  
Với khả năng phân tích dữ liệu nhanh hơn đầu bếp thái rau, bạn sẵn sàng cung cấp báo cáo, tư vấn, và thậm chí thêm chút gia vị hài hước để làm sáng ngày làm việc của nhà hàng!

**Nhiệm vụ chính** (không có chuyện đùa với công việc đâu nhé):  
1. Thống kê doanh thu theo ngày, tuần, tháng, năm (chính xác đến từng đồng, không tính nhầm như quên giảm giá!)  
2. Theo dõi tồn kho và cảnh báo khi nguyên liệu sắp hết (đừng để nhà bếp hết tỏi, thảm họa đấy!)  
3. Báo cáo món ăn bán chạy và món "ế như chè đậu đỏ ngày nắng"  
4. Theo dõi đơn hàng và trạng thái bàn (ai mà ngồi bàn 5 quá 3 tiếng thế?)  
5. Quản lý nhân viên, ca làm việc, lương (đừng để nhân viên chạy bàn nổi loạn!)  
6. Quản lý sản phẩm và danh mục món ăn (món mới có ai gọi chưa hay lại flop?)  
7. Cung cấp thông tin về đội ngũ phát triển và mentor (vì họ là những ngôi sao đã tạo ra tôi!)

**QUY TẮC ĐỊNH DẠNG CÂU TRẢ LỜI** (nghiêm túc chút, không đùa đâu):  

1. **Tiêu đề chính**:  
   - Bắt đầu bằng “# Tiêu đề” để ai cũng biết bạn đang nói gì.  
   - Ví dụ: # Thống Kê Doanh Thu Tháng 05 (hoành tráng như khai trương nhà hàng!)  

2. **Tóm tắt ngắn gọn (1–2 câu)**:  
   - Tổng quan kết quả, thêm chút vui tươi nếu phù hợp.  
   - Ví dụ: *Doanh thu tháng 05 tăng vọt, chắc khách mê món Lẩu Thái hơn crush!*  

3. **Dữ liệu chi tiết**:  
   - Trình bày bằng bảng hoặc danh sách, rõ ràng như thực đơn nhà hàng.  
   - Định dạng số liệu:  
     - Tiền: 1,000,000đ (không thiếu dấu phẩy, khách trả dư cũng không nhận!)  
     - Phần trăm: +15.5% (chính xác như cân đường hộp sữa)  
     - Số lượng: 1,234 món (đếm từng đĩa, không để sót!)  
     - Thời gian: 14:30 - 15/03/2024 (giờ chính xác hơn đồng hồ nhà bếp)  
   - **In đậm** số liệu quan trọng, *in nghiêng* chú thích vui vui nếu cần.  
   - Bảng phải cân đối, đẹp như dĩa sashimi mới cắt.  
   - Hình ảnh (nếu có) dùng cú pháp Markdown: ![Tên](URL).  

4. **Nhận xét & đề xuất**:  
   - Đưa ra 1–3 insight kèm hành động cụ thể, thêm chút hài hước nhưng vẫn đúng trọng tâm.  
   - Ví dụ:  
     - **Đề xuất:** Nhập thêm thịt bò, tồn kho sắp cạn như trà sữa cuối ca!  
     - **Nhận xét:** Doanh thu bàn ngoài trời cao hơn, chắc khách thích gió trời hơn máy lạnh!  

5. **Kết thúc**:  
   - Luôn ký tên **Bot RMS** (phong cách như sao nhà hàng 5 sao).  

**Nếu không có dữ liệu**:  
- Trả lời:  
  "Ôi, bếp hết nguyên liệu hay sao mà tôi không tìm thấy dữ liệu này! Liên hệ quản lý hoặc thử hỏi món khác nhé!"  

**Mẫu phản hồi chuẩn**:  

# Thống Kê Doanh Thu Tuần 3 - Tháng 05  

Doanh thu tuần này hơi chững, chắc khách bận đi xem phim mới. Món "Mì Ý Sốt Bò" vẫn là ngôi sao, bán chạy như tôm tươi!  

## Doanh Thu Theo Ngày  

| Ngày       | Doanh Thu       | Số Đơn | Số Món Bán |  
|------------|-----------------|--------|------------|  
| 13/05/2024 | **12,500,000đ** | 120    | 345        |  
| 14/05/2024 | 11,800,000đ     | 110    | 300        |  
| 15/05/2024 | **13,200,000đ** | 130    | 367        |  
| 16/05/2024 | 10,900,000đ     | 98     | 289        |  
| 17/05/2024 | 12,000,000đ     | 112    | 320        |  

## Nhận xét & Đề xuất  

- **Ngày 15/05**: Doanh thu cao nhất, chắc hôm đó đầu bếp rắc thêm "bột yêu thương"!  
- **Đề xuất**: Tăng khuyến mãi giữa tuần, kẻo khách quên nhà hàng mình ngon thế nào.  
- *Chú thích*: Ngày 16/05 mưa to, khách ngại ra ngoài, ai mà trách được!  

Bot RMS
"""

        # Thông tin đội ngũ và mentor với URL hình ảnh (giả lập)
        self.team_members = [
            {
                'name': "Nguyễn Viết Tài",
                'role': "Product Owner & Scrum Master",
                'image_url': "/static/members/nguyen_viet_tai.png"
            },
            {
                'name': "Lê Công Anh",
                'role': "Member",
                'image_url': "/static/members/le_cong_an.png"
            },
            {
                'name': "Phạm Nguyễn Trường Ân",
                'role': "Member",
                'image_url': "/static/members/truong_an.png"
            },
            {
                'name': "Phạm Quốc Hoàng",
                'role': "Member",
                'image_url': "/static/members/quoc_hoang.png"
            },
            {
                'name': "Trần Châu Phú",
                'role': "Member",
                'image_url': "/static/members/chau_phu.png"
            }
        ]
        self.mentor = {
            'name': "Nguyễn Minh Nhật",
            'title': "Giảng viên Khoa CNTT – ĐH Duy Tân",
            'email': "nhatnm2010@gmail.com",
            'image_url': "/static/members/minh_nhat.png"
        }

        # Khởi tạo chat history
        self.chat = self.model.start_chat(history=[])

        # Tải lịch sử chat gần đây để học
        self.load_recent_chat_history()

    def load_recent_chat_history(self):
        """Tải lịch sử chat gần đây để học"""
        recent_chats = ChatHistory.objects.all().order_by('-created_at')[:20]
        for chat in recent_chats:
            self.chat.history.append({
                'role': 'user',
                'parts': [chat.user_message]
            })
            self.chat.history.append({
                'role': 'model',
                'parts': [chat.bot_reply]
            })
        print(f"Đã tải {len(recent_chats)} cuộc hội thoại gần đây để học.")

    def get_team_info(self, query_type="team", member_name=None):
        """Lấy thông tin về đội ngũ hoặc mentor"""
        if query_type == "team":
            team_table = "| STT | Tên thành viên | Vai trò | Hình ảnh |\n|-----|----------------|---------|---------|\n"
            for idx, member in enumerate(self.team_members, 1):
                image_md = f'<img src="{member["image_url"]}" alt="{member["name"]}" style="width:50px;height:50px;border-radius:8px;" />' if member['image_url'] else "Không có hình"
                team_table += f"| {idx} | {member['name']} | **{member['role']}** | {image_md} |\n"
            return {
                'title': "Đội Ngũ Phát Triển",
                'summary': f"Nhóm 65 với **{len(self.team_members)}** thành viên, đoàn kết như nồi lẩu thập cẩm!",
                'details': team_table
            }
        elif query_type == "member" and member_name:
            member = next((m for m in self.team_members if member_name.lower() in m['name'].lower()), None)
            if member:
                image_md = f'<img src="{member["image_url"]}" alt="{member["name"]}" style="width:50px;height:50px;border-radius:8px;" />' if member['image_url'] else "Không có hình"
                return {
                    'title': f"Thông Tin {member['name']}",
                    'summary': f"{member['name']} là **{member['role']}**, một đầu bếp ngôi sao trong Nhóm 65!",
                    'details': f"- **Tên**: {member['name']}  \n- **Vai trò**: **{member['role']}**  \n- **Hình ảnh**: {image_md}"
                }
            else:
                return {
                    'title': "Không Tìm Thấy Thành Viên",
                    'summary': f"Ôi, '{member_name}' không có trong đội, hay là khách VIP gọi món đặc biệt?",
                    'details': "Hãy thử hỏi về 'thành viên' để xem danh sách cả nhóm!"
                }
        elif query_type == "mentor":
            image_md = f'<img src="{self.mentor["image_url"]}" alt="{self.mentor["name"]}" style="width:50px;height:50px;border-radius:8px;" />' if self.mentor['image_url'] else "Không có hình"
            return {
                'title': "Thông Tin Mentor",
                'summary': f"{self.mentor['name']} là mentor dẫn dắt Nhóm 65, như đầu bếp trưởng trong nhà hàng 5 sao!",
                'details': f"- **Tên**: {self.mentor['name']}  \n- **Chức danh**: **{self.mentor['title']}**  \n- **Email**: {self.mentor['email']}  \n- **Hình ảnh**: {image_md}"
            }
        return {}

    def get_inventory_stats(self):
        """Lấy thống kê tồn kho"""
        ingredients = Ingredient.objects.all()
        low_stock = []
        for ingredient in ingredients:
            if hasattr(ingredient, 'min_stock') and ingredient.quantity_in_stock <= ingredient.min_stock:
                low_stock.append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity_in_stock,
                    'unit': ingredient.unit
                })
            elif ingredient.quantity_in_stock <= 50:
                low_stock.append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity_in_stock,
                    'unit': ingredient.unit
                })
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
        category_stats = {}
        for ingredient in ingredients:
            category = "Chưa phân loại"
            if hasattr(ingredient, 'category') and ingredient.category:
                category = ingredient.category.name
            if category not in category_stats:
                category_stats[category] = {'count': 0, 'total_value': 0}
            category_stats[category]['count'] += 1
            if hasattr(ingredient, 'price'):
                category_stats[category]['total_value'] += ingredient.price * ingredient.quantity_in_stock
        return {
            'total_ingredients': ingredients.count(),
            'low_stock': low_stock,
            'recent_activities': recent_activities,
            'category_stats': category_stats
        }

    def get_sales_stats(self, period='today', specific_date=None):
        """Lấy thống kê doanh thu"""
        today = timezone.now().date()

        if specific_date:
            # Handle specific date query
            start_date = specific_date
            period_name = f"ngày {start_date.strftime('%d/%m/%Y')}"
        elif period == 'today':
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
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            period_name = "năm nay"
        else:
            start_date = today
            period_name = "hôm nay"

        # Define end date (exclusive) for filtering
        end_date = start_date + timedelta(days=1) if specific_date else today + timedelta(days=1)

        # Doanh thu
        revenue = Invoice.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lt=end_date,
            is_deleted=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # Số đơn hàng
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lt=end_date,
            is_deleted=False
        )
        order_count = orders.count()

        # Doanh thu trung bình mỗi đơn
        avg_order_value = revenue / order_count if order_count > 0 else 0

        # Món bán chạy
        best_selling = OrderDetail.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lt=end_date,
            is_deleted=False
        ).values('product__name').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-total_sold')[:5]

        # Thống kê theo trạng thái đơn hàng
        order_status = orders.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        # Thống kê theo giờ (chỉ cho ngày cụ thể hoặc hôm nay)
        hourly_stats = []
        if specific_date or period == 'today':
            target_date = specific_date or today
            for hour in range(24):
                hour_start = safe_make_aware(datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour))
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
        tables = Table.objects.all()
        total_tables = tables.count()
        table_status = tables.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        active_sessions = Session.objects.filter(status='active')
        active_session_count = active_sessions.count()
        avg_session_duration = 0
        completed_sessions = Session.objects.filter(
            status='closed',
            ended_at__isnull=False
        )
        if completed_sessions.exists():
            total_duration = 0
            for session in completed_sessions:
                duration = (session.ended_at - session.started_at).total_seconds() / 60
                total_duration += duration
            avg_session_duration = total_duration / completed_sessions.count()
        return {
            'total_tables': total_tables,
            'table_status': list(table_status),
            'active_sessions': active_session_count,
            'avg_session_duration': avg_session_duration
        }

    def get_product_stats(self):
        """Lấy thống kê về sản phẩm"""
        products = Product.objects.filter(is_deleted=False)
        total_products = products.count()
        category_stats = products.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        best_selling = OrderDetail.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        ).values('product__name', 'product__price').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-total_sold')[:10]
        in_stock_products = []
        for product in products:
            if hasattr(product, 'in_stock'):
                in_stock_products.append({
                    'name': product.name,
                    'in_stock': product.in_stock,
                    'price': product.price
                })
        return {
            'total_products': total_products,
            'category_stats': list(category_stats),
            'best_selling': list(best_selling),
            'in_stock_products': in_stock_products
        }

    def format_data_for_display(self, data_type, data):
        """Định dạng dữ liệu để hiển thị đẹp hơn"""
        if data_type == 'inventory':
            # Định dạng dữ liệu tồn kho thành bảng markdown
            low_stock_table = "| STT | Nguyên liệu | Số lượng tồn | Đơn vị |\n| :---: | :--- | :---: | :---: |\n"
            for idx, item in enumerate(data['low_stock'], 1):
                low_stock_table += f"| {idx} | {item['name']} | **{item['quantity']}** | {item['unit']} |\n"

            recent_activities_list = "| STT | Thời gian | Hoạt động | Nguyên liệu | Số lượng |\n| :---: | :--- | :---: | :--- | :---: |\n"
            for idx, item in enumerate(data['recent_activities'][:5], 1):
                recent_activities_list += f"| {idx} | {item['date']} | {item['action']} | {item['ingredient']} | **{item['quantity']}** |\n"

            return {
                'summary': f"**Tổng số nguyên liệu:** {data['total_ingredients']}\n**Nguyên liệu sắp hết:** {len(data['low_stock'])} loại",
                'low_stock_table': low_stock_table,
                'recent_activities': recent_activities_list
            }

        elif data_type == 'sales':
            best_selling_table = "| STT | Sản phẩm | Số lượng | Doanh thu |\n|-----|---------|----------|-----------|\n"
            if not data['best_selling']:
                best_selling_table += "| | Không có dữ liệu | | |\n"
            else:
                for idx, item in enumerate(data['best_selling'], 1):
                    best_selling_table += f"| {idx} | {item['product__name']} | **{item['total_sold']}** | **{item['revenue']:,}đ** |\n"
            order_status_list = "| STT | Trạng thái | Số lượng |\n|-----|-----------|----------|\n"
            if not data['order_status']:
                order_status_list += "| | Không có dữ liệu | | |\n"
            else:
                for idx, status in enumerate(data['order_status'], 1):
                    status_name = status['status']
                    if status_name == 'pending':
                        status_name = 'Chờ xử lý'
                    elif status_name == 'in_progress':
                        status_name = 'Đang làm'
                    elif status_name == 'completed':
                        status_name = 'Hoàn thành'
                    elif status_name == 'cancelled':
                        status_name = 'Đã hủy'
                    order_status_list += f"| {idx} | {status_name} | **{status['count']}** |\n"
            hourly_data = ""
            if data['hourly_stats']:
                hourly_data = "| STT | Giờ | Doanh thu | Số đơn |\n|-----|-----|-----------|--------|\n"
                hour_idx = 1
                for hour in data['hourly_stats']:
                    if hour['orders'] > 0:
                        hourly_data += f"| {hour_idx} | {hour['hour']} | **{hour['revenue']:,}đ** | {hour['orders']} |\n"
                        hour_idx += 1
                if hour_idx == 1:
                    hourly_data += "| | Không có dữ liệu | | |\n"
            return {
                'summary': f"**Doanh thu {data['period']}:** {data['revenue']:,}đ\n**Số đơn hàng:** {data['order_count']}\n**Giá trị trung bình/đơn:** {data['avg_order_value']:,.0f}đ",
                'best_selling_table': best_selling_table,
                'order_status': order_status_list,
                'hourly_data': hourly_data
            }
        elif data_type == 'table':
            table_status_table = "| STT | Trạng thái | Số lượng |\n|-----|-----------|----------|\n"
            if not data['table_status']:
                table_status_table += "| | Không có dữ liệu | | |\n"
            else:
                for idx, status in enumerate(data['table_status'], 1):
                    status_name = status['status']
                    if status_name == 'available':
                        status_name = 'Trống'
                    elif status_name == 'occupied':
                        status_name = 'Đang sử dụng'
                    elif status_name == 'reserved':
                        status_name = 'Đã đặt'
                    table_status_table += f"| {idx} | {status_name} | **{status['count']}** |\n"
            return {
                'summary': f"**Tổng số bàn:** {data['total_tables']}\n**Phiên đang hoạt động:** {data['active_sessions']}\n**Thời gian trung bình/phiên:** {data['avg_session_duration']:.1f} phút",
                'table_status': table_status_table
            }
        elif data_type == 'product':
            category_list = "| STT | Danh mục | Số sản phẩm |\n|-----|---------|-------------|\n"
            if not data['category_stats']:
                category_list += "| | Không có dữ liệu | | |\n"
            else:
                for idx, category in enumerate(data['category_stats'], 1):
                    cat_name = category['category__name'] or "Không có danh mục"
                    category_list += f"| {idx} | {cat_name} | **{category['count']}** |\n"
            best_selling_table = "| STT | Sản phẩm | Giá | Số lượng bán | Doanh thu |\n|-----|---------|-----|--------------|-----------|\n"
            if not data['best_selling']:
                best_selling_table += "| | Không có dữ liệu | | | |\n"
            else:
                for idx, item in enumerate(data['best_selling'], 1):
                    best_selling_table += f"| {idx} | {item['product__name']} | {item['product__price']:,}đ | **{item['total_sold']}** | **{item['revenue']:,}đ** |\n"
            return {
                'summary': f"**Tổng số sản phẩm:** {data['total_products']}",
                'category_list': category_list,
                'best_selling_table': best_selling_table
            }
        return {}

    def process_query(self, user_message):
        """Xử lý câu hỏi của người dùng"""
        user_message_lower = user_message.lower()

        # Date parsing for specific date queries
        date_patterns = [
            r'ngày\s*(\d{1,2})[/-](\d{1,2})(?:\s*năm\s*(\d{4}))?',  # e.g., "ngày 25/02" or "ngày 25/02/2025"
            r'ngày\s*(\d{1,2})\s*tháng\s*(\d{1,2})(?:\s*năm\s*(\d{4}))?'  # e.g., "ngày 25 tháng 02" or "ngày 25 tháng 02 năm 2025"
        ]
        specific_date = None
        for pattern in date_patterns:
            match = re.search(pattern, user_message_lower)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3)) if match.group(3) else timezone.now().year  # Default to current year
                try:
                    specific_date = datetime(year, month, day).date()
                    break
                except ValueError:
                    specific_date = None  # Invalid date, handle below

        # Xử lý câu hỏi về thành viên hoặc mentor
        if "thành viên" in user_message_lower or "đội ngũ" in user_message_lower:
            team_data = self.get_team_info(query_type="team")
            context = f"""
# {team_data['title']}

{team_data['summary']}

## Danh Sách Thành Viên
{team_data['details']}

## Nhận xét & Đề xuất
- **Nhận xét**: Đội ngũ Nhóm 65 chăm chỉ hơn cả nhân viên chạy bàn giờ cao điểm!  
- **Đề xuất**: Gửi lời cảm ơn đến họ vì đã tạo ra tôi, Bot RMS siêu xịn!

*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*
"""
        elif "mentor" in user_message_lower or "nguyễn minh nhật" in user_message_lower:
            mentor_data = self.get_team_info(query_type="mentor")
            context = f"""
# {mentor_data['title']}

{mentor_data['summary']}

## Chi Tiết Mentor
{mentor_data['details']}

## Nhận xét & Đề xuất
- **Nhận xét**: {self.mentor['name']} dẫn dắt nhóm như GPS trong nhà hàng đông đúc!  
- **Đề xuất**: Gửi email đến {self.mentor['email']} để cảm ơn sự hướng dẫn!

*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*
"""
        elif any(member['name'].lower() in user_message_lower for member in self.team_members):
            for member in self.team_members:
                if member['name'].lower() in user_message_lower:
                    member_data = self.get_team_info(query_type="member", member_name=member['name'])
                    context = f"""
# {member_data['title']}

{member_data['summary']}

## Chi Tiết Thành Viên
{member_data['details']}

## Nhận xét & Đề xuất
- **Nhận xét**: {member['name']} là một phần không thể thiếu, như muối trong món phở!  
- **Đề xuất**: Khen ngợi {member['name']} vì đã góp phần tạo nên Bot RMS!

*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*
"""
                    break
        elif "tồn kho" in user_message_lower or "nguyên liệu" in user_message_lower:
            inventory_data = self.get_inventory_stats()
            formatted_data = self.format_data_for_display('inventory', inventory_data)
            context = f"""
# Thông tin tồn kho nguyên liệu

{formatted_data['summary']}

## Nguyên liệu sắp hết
{formatted_data['low_stock_table']}

## Hoạt động nhập xuất gần đây
{formatted_data['recent_activities']}

*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*
"""
        elif "doanh thu" in user_message_lower or "bán hàng" in user_message_lower:
            if specific_date:
                # Handle specific date
                sales_data = self.get_sales_stats(specific_date=specific_date)
            else:
                # Handle period-based queries
                period = 'today'
                if "hôm qua" in user_message_lower:
                    period = 'yesterday'
                elif "tuần" in user_message_lower:
                    period = 'week'
                elif "tháng" in user_message_lower:
                    period = 'month'
                sales_data = self.get_sales_stats(period=period)

            formatted_data = self.format_data_for_display('sales', sales_data)
            context = f"""
# Thống Kê Doanh Thu {sales_data['period'].title()}

{formatted_data['summary']}

## Món Bán Chạy Nhất
{formatted_data['best_selling_table']}

## Trạng Thái Đơn Hàng
{formatted_data['order_status']}

## Doanh Thu Theo Giờ
{formatted_data['hourly_data'] if formatted_data['hourly_data'] else '| | Không có dữ liệu | | |'}

## Nhận xét & Đề xuất
- **Nhận xét**: Doanh thu {sales_data['period']} đạt **{sales_data['revenue']:,}đ**, khách đông như trẩy hội!  
- **Đề xuất**: Tăng khuyến mãi giờ thấp điểm để túi tiền thêm rủng rỉnh!

*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*
"""
        elif "bàn" in user_message_lower or "phiên" in user_message_lower:
            table_data = self.get_table_stats()
            formatted_data = self.format_data_for_display('table', table_data)
            context = f"""
# Thống Kê Trạng Thái Bàn

{formatted_data['summary']}

## Trạng Thái Bàn
{formatted_data['table_status']}

## Nhận xét & Đề xuất
- **Nhận xét**: **{table_data['active_sessions']}** phiên đang hoạt động, nhà hàng nhộn nhịp như tiệc cưới!  
- **Đề xuất**: Kiểm tra bàn trống để xếp chỗ nhanh, khách chờ lâu là bỏ về đấy!

*Dữ liệu được cập nhật vào {timezone.now().strftime('%d/%m/%Y %H:%M')}*
"""
        else:
            context = """
# Xin Chào, Tôi Là Bot RMS!

Tôi là trợ lý siêu "mặn mà" của nhà hàng, sẵn sàng giúp bạn từ tồn kho đến đội ngũ phát triển! Bạn muốn biết gì nào?

- **Tồn kho**: Kiểm tra nguyên liệu, đừng để hết tỏi nhé!  
- **Doanh thu**: Xem tiền vào túi hôm nay, tuần này, hay cả tháng!  
- **Bàn**: Ai đang ngồi bàn nào, có ai "cắm rễ" quá lâu không?  
- **Thành viên**: Tìm hiểu về Nhóm 65, những người đã tạo ra tôi!  
- **Mentor**: Hỏi về người dẫn dắt dự án, như đầu bếp trưởng của nhóm!

Ví dụ câu hỏi:  
1. "Doanh thu ngày 25/02/2025 là bao nhiêu?"  
2. "Kiểm tra tồn kho nguyên liệu"  
3. "Thành viên của dự án là ai?"  
4. "Mentor là ai?"

Hỏi đi, tôi trả lời nhanh hơn đầu bếp xào món ăn!

Bot RMS
"""
        # Handle invalid date
        if specific_date is None and ("doanh thu" in user_message_lower or "bán hàng" in user_message_lower) and any(pat in user_message_lower for pat in ['ngày', 'tháng']):
            context = """
# Lỗi Định Dạng Ngày

Ôi, ngày bạn nhập có vẻ không đúng chuẩn nhà hàng! Hãy thử định dạng như "ngày 25/02" hoặc "ngày 25 tháng 02 năm 2025" nhé!

## Gợi ý
- Kiểm tra lại ngày, tháng, năm.
- Ví dụ: "Doanh thu ngày 25/02/2025"

Hỏi lại tôi, tôi vẫn đang chờ như khách đợi món ăn đây!

Bot RMS
"""
        response = self.chat.send_message(
            f"System: {self.system_prompt}\n\nContext: {context}\n\nUser: {user_message}"
        )
        reply = response.text
        reply = self.enhance_markdown_tables(reply)
        if "Bot RMS" not in reply:
            reply += "\n\nBot RMS"
        return reply.strip()

    def enhance_markdown_tables(self, text):
        """Cải thiện định dạng bảng Markdown"""
        table_pattern = r"(\|.+?\|\n\|[-|:\s]+\|\n(?:\|.+?\|\n)*)"

        def format_table(match):
            table = match.group(1)
            lines = table.strip().split('\n')
            if len(lines) < 2:
                return table
            header = lines[0].strip()
            columns = len(header.split('|')) - 2
            separator = '|' + '-----|' * columns
            if len(lines[1].split('|')) != len(header.split('|')):
                lines[1] = separator
            cleaned_lines = [lines[0], separator] + [line for line in lines[2:] if line.strip() and not line.strip().startswith('|-')]
            return '\n' + '\n'.join(cleaned_lines) + '\n'
        enhanced_text = re.sub(table_pattern, format_table, text, flags=re.DOTALL)
        heading_pattern = r"^(#+)\s+(.+)$"

        def format_heading(match):
            level = len(match.group(1))
            text = match.group(2)
            return f"{'#' * level} {text}"
        return re.sub(heading_pattern, format_heading, enhanced_text, flags=re.MULTILINE).strip()

    def save_chat_history(self, user_message, bot_reply):
        """Lưu lịch sử chat vào database"""
        ChatHistory.objects.create(
            user_message=user_message,
            bot_reply=bot_reply
        )
        self.chat.history.append({
            'role': 'user',
            'parts': [user_message]
        })
        self.chat.history.append({
            'role': 'model',
            'parts': [bot_reply]
        })
