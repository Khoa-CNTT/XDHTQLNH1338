# 📌 Django Models cho hệ thống Quản lý Nhà hàng (Cập nhật)

from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.functional import cached_property
# 🔄 Model Category (Loại sản phẩm)
from cloudinary.uploader import upload
import qrcode
from io import BytesIO
from django.conf import settings

from web_01.utils.model_consts import CATEGORY_STATUS_CHOICES


class BaseModel(models.Model):
    # Trường kiểu DateTimeField, tự động thêm thời gian tạo khi tạo instance mới.
    # Tham số null=True cho phép trường này nhận giá trị NULL trong cơ sở dữ liệu.
    created_at = models.DateTimeField(verbose_name='created_at', null=True, auto_now_add=True)

    # Trường kiểu DateTimeField, tự động cập nhật thời gian khi instance được lưu.
    # Tham số null=True cho phép trường này nhận giá trị NULL trong cơ sở dữ liệu.
    updated_at = models.DateTimeField(verbose_name='updated_at', null=True, auto_now=True)

    # Trường kiểu BooleanField để biểu diễn trạng thái xóa (soft delete) của instance.
    # Mặc định không xóa (False).
    is_deleted = models.BooleanField(verbose_name='is_deleted', default=False)

    class Meta:
        # Khai báo class này là một abstract base class.
        # Các trường của nó sẽ được thêm vào các model kế thừa từ class này,
        # nhưng chính nó sẽ không tạo một bảng riêng trong cơ sở dữ liệu.
        abstract = True

    @cached_property
    def formatted_created_at(self) -> str:
        return self.created_at.strftime('%d/%m/%Y')  # Định dạng ngày/tháng/năm


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=CATEGORY_STATUS_CHOICES, default='active')

# 🔄 Model Product (Sản phẩm)
    class Meta:
        # Khai báo class này là một abstract base class.
        # Các trường của nó sẽ được thêm vào các model kế thừa từ class này,
        # nhưng chính nó sẽ không tạo một bảng riêng trong cơ sở dữ liệu.
        db_table = 'category'

    def __str__(self) -> str:
        return f'{self.name}'


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kg'),
        ('g', 'Gram'),
        ('ml', 'Milliliter'),
        ('chai', 'Chai'),
        ('gói', 'Gói'),
        ('hộp', 'Hộp'),
        ('lon', 'Lon'),
    ]

    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES)
    quantity_in_stock = models.IntegerField(default=0)  # 🔄 Số lượng tồn kho

    class Meta:
        db_table = 'ingredient'

    def __str__(self) -> str:
        return f'{self.name}'

    def update_stock(self):
        """Cập nhật số lượng tồn kho từ InventoryLog."""
        total = self.inventorylog_set.aggregate(total=models.Sum('change'))['total']
        self.quantity_in_stock = total if total else 0
        self.save()

# 🔄 Lịch sử nhập xuất kho


class InventoryLog(models.Model):
    TYPE_CHOICES = [
        ('import', 'Nhập kho'),
        ('export', 'Xuất kho'),
        ('adjustment', 'Điều chỉnh'),
    ]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    change = models.IntegerField()  # (+ nhập, - xuất)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    note = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_log'

    def save(self, *args, **kwargs):
        """Cập nhật tồn kho khi có thay đổi."""
        super().save(*args, **kwargs)
        self.ingredient.update_stock()

# 🔄 Sản phẩm


class Product(BaseModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    image = CloudinaryField('image', null=True, blank=True)
    ingredients = models.ManyToManyField(Ingredient, through='IngredientProduct', blank=True, null=True)

    class Meta:
        db_table = 'product'
        ordering = ['-created_at']

    @cached_property
    def in_stock(self):
        """
        Tính số lượng sản phẩm có thể làm được dựa vào nguyên liệu tồn kho.
        Nếu không đủ nguyên liệu để làm ít nhất 1 sản phẩm, trả về 0.
        """
        ingredient_products = self.ingredientproduct_set.all()
        stock_counts = []

        for item in ingredient_products:
            if item.quantity_required == 0:  # Tránh lỗi chia cho 0
                continue

            available_count = item.ingredient.quantity_in_stock // item.quantity_required
            stock_counts.append(available_count)

        return min(stock_counts) if stock_counts else 0  # Trả về số lượng nhỏ nhất có thể làm được


class IngredientProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.IntegerField()

    class Meta:
        db_table = 'ingredient_product'


class Customer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    loyalty_points = models.IntegerField()

# 🔄 Model Employee
    class Meta:
        db_table = 'customer'


class Employee(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    salary = models.IntegerField()

    class Meta:
        db_table = 'employee'


class WorkShift(models.Model):
    SHIFT_TYPE_CHOICES = [
        ('morning', 'Sáng'),
        ('afternoon', 'Chiều'),
        ('evening', 'Tối')
    ]
    STATUS_CHOICES = [
        ('worked', 'Đã làm'),
        ('off', 'Nghỉ')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="workshifts")
    date = models.DateField()
    shift_type = models.CharField(max_length=10, choices=SHIFT_TYPE_CHOICES)
    duration = models.DecimalField(max_digits=4, decimal_places=2, default=4.0)  # Mặc định mỗi ca 4 giờ
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='worked')

    class Meta:
        db_table = 'work_shift'
        unique_together = ['employee', 'date', 'shift_type']  # Một ca/ngày/nhân viên

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.shift_type} ({self.duration} giờ)"


# 🔄 Model Table


class Table(models.Model):
    table_number = models.IntegerField(unique=True)
    status = models.CharField(max_length=10, choices=[('available', 'Trống'), ('occupied', 'Sử dụng'), ('reserved', 'Đã đặt')], default='available')
    qr_image = CloudinaryField('image')

    class Meta:
        db_table = 'table'
    # 🔄 Model Ingredient
    # 🔄 Override phương thức save()

    def save(self, *args, **kwargs):
        # Tạo URL dựa trên table_number
        url = f"{settings.FRONT_END_URL}login-menu/?table_number={self.table_number}"
        # Tạo mã QR
        qr = qrcode.make(url)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, format='PNG')
        qr_bytes.seek(0)

        # Upload ảnh lên Cloudinary nếu chưa có hoặc cần cập nhật
        if not self.qr_image or kwargs.get('force_update_qr', False):
            result = upload(qr_bytes, public_id=f"table_{self.table_number}_qr")
            self.qr_image = result['url']

        # Gọi phương thức save() gốc để lưu vào DB
        super().save(*args, **kwargs)


class Session(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} - {self.customer} - {self.table} ({self.status})"

    class Meta:
        db_table = 'session'


class Invoice(BaseModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=15, choices=[('cash', 'Tiền mặt'), ('bank_transfer', 'Chuyển khoản'), ('card', 'Thẻ')], null=True, blank=True)
    total_amount = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)

    class Meta:
        db_table = 'invoice'
# 🔄 Model Order


class Order(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    total = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=[
        ('pending', 'Chờ'),
        ('in_progress', 'Đang làm'),
        ('completed', 'Xong'),
        ('cancelled', 'Hủy')
    ], default='pending')

    class Meta:
        db_table = 'order'

    @cached_property
    def formatted_price(self) -> str:
        return f'{self.total:,}đ'.replace(',', '.')


class OrderDetail(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()  # Giá của từng sản phẩm
    total = models.IntegerField()  # Tổng tiền của từng dòng sản phẩm (quantity * price)
    status = models.CharField(max_length=15, choices=[
        ('pending', 'Chờ'),
        ('in_progress', 'Đang làm'),
        ('completed', 'Xong'),
        ('cancelled', 'Hủy')
    ], default='pending')  # Trạng thái của từng món

    class Meta:
        db_table = 'order_detail'


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'cart_item'

# 🔄 Model Notification


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    type = models.CharField(max_length=15, choices=[('order_status', 'Order Status'), ('promotion', 'Promotion'), ('reminder', 'Reminder')])
    status = models.CharField(max_length=10, choices=[('read', 'Read'), ('unread', 'Unread')], default='unread')

    class Meta:
        db_table = 'notification'
# ✅ Models hoàn tất!


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'comment'


class Rating(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.IntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)], null=True, blank=True)

    class Meta:
        db_table = 'rating'


class BestSellingProduct(models.Model):
    """
    🔍 Các trường:
        product (ForeignKey):
            Liên kết đến bảng Product.
            Xác định sản phẩm cụ thể.
        sold_quantity (IntegerField):

        Số lượng sản phẩm đã bán.
            report_date (DateField):

        Ngày tạo báo cáo (có thể là ngày, tuần, tháng hoặc năm).

    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sold_quantity = models.IntegerField()
    report_date = models.DateTimeField()

    class Meta:

        db_table = 'best_selling_product'


class TableReservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Đã hoàn thành'),
    ]

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    many_person = models.IntegerField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')

    date = models.DateField(null=False)  # Ngày đặt bàn
    hour = models.TimeField(null=False)  # Giờ đặt bàn

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Bàn {self.table.table_number} ({self.date} {self.hour})"

    class Meta:
        db_table = 'table_reservation'
