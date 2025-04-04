from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Tạo 5 tài khoản admin mặc định"

    ADMIN_ACCOUNTS = [
        ("viettai", "1"),
        ("an", "1"),
        ("hoang", "1"),
        ("phu", "1"),
        ("anh", "1"),
        ("admin", "1"),
    ]

    def handle(self, *args, **kwargs):
        created_count = 0

        for username, password in self.ADMIN_ACCOUNTS:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, password=password, email=f"{username}@example.com")
                self.stdout.write(self.style.SUCCESS(f"✅ Đã tạo admin: {username}"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Tài khoản '{username}' đã tồn tại."))

        self.stdout.write(self.style.SUCCESS(f"🎉 Đã tạo {created_count} tài khoản admin mới!"))
