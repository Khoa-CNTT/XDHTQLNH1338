from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from web_01.models import Employee
import requests
from cloudinary.uploader import upload

TAI_AVATAR_URL = 'https://scontent.fsgn2-4.fna.fbcdn.net/v/t39.30808-1/458748272_1540524726671861_2443305916562459873_n.jpg?stp=dst-jpg_s480x480_tt6&_nc_cat=101&ccb=1-7&_nc_sid=e99d92&_nc_ohc=7Ljk6R_BYL4Q7kNvwFdCvt2&_nc_oc=Adnn-c5jF5IKAwmwzkKz848G4DdF_bWbj1A2oPjEX5soJ3Jx433-2v-bA-HkAIA4n-8&_nc_zt=24&_nc_ht=scontent.fsgn2-4.fna&_nc_gid=FFZMFg7ewG0hKGFXD37_1g&oh=00_AfGVNdkRE2rtNw5wk2kZBa3EZhHycxTGXV6BgZdWeqY2TA&oe=6813A9FC'

AN_AVATAR_URL = 'https://scontent.fsgn2-7.fna.fbcdn.net/v/t39.30808-1/485041904_1341502240492379_2276124344218298642_n.jpg?stp=dst-jpg_s480x480_tt6&_nc_cat=100&ccb=1-7&_nc_sid=e99d92&_nc_ohc=Uyr9BBNzl4IQ7kNvwFGdkj2&_nc_oc=AdnxFHaMHNSb7GjY0Q3VelOwrbnU6XM_nG9IV9NFtDI-20AHFZgCHnopvtp8XyyHPu8&_nc_zt=24&_nc_ht=scontent.fsgn2-7.fna&_nc_gid=1W_mTnK59_VyeY6Bt0GvVA&oh=00_AfGsEp6nFsRKddLatBzq2awOZkeU7PN5D-crxOhK9Z0vkg&oe=68138DD8'

HOANG_AVATAR_URL = 'https://scontent.fsgn2-9.fna.fbcdn.net/v/t39.30808-1/449391289_1627235181402546_3351840801085214001_n.jpg?stp=dst-jpg_s480x480_tt6&_nc_cat=106&ccb=1-7&_nc_sid=e99d92&_nc_ohc=4btIuBgxoO8Q7kNvwGMgqnT&_nc_oc=AdmDLNDOOz_NeDcxBEv7i_ijL4wyVAW0Vb6xromlNeqRpXpr8ebXt5R6lnTfXCwF130&_nc_zt=24&_nc_ht=scontent.fsgn2-9.fna&_nc_gid=REgGhsLmD_dOdHTEyIG6JQ&oh=00_AfGKR9TNLTp7muDWCU0_TVffyHjVkhNIZ0BQ3o4Q7f44tw&oe=6813856C'

PHU_AVATAR_URL = 'https://scontent.fsgn2-7.fna.fbcdn.net/v/t39.30808-1/480446481_1826814718144328_6165040751702083067_n.jpg?stp=dst-jpg_s480x480_tt6&_nc_cat=108&ccb=1-7&_nc_sid=e99d92&_nc_ohc=82YNLN9YMNsQ7kNvwHQpBAM&_nc_oc=Adk6o-yYwgd3ZxakTJOvK1VomckCLYgRf3u8pq2jx5oAgDuZQa30ZjeQuSKecrzty8c&_nc_zt=24&_nc_ht=scontent.fsgn2-7.fna&_nc_gid=84SWIRKk2kSBEBS8TGSNRQ&oh=00_AfEpzNNfnwn9hVLEA_ZqWN8w5SQTJK4DqaRDTiZ4FrMuKw&oe=6813B128'

ANH_AVATAR_URL = 'https://scontent.fsgn2-8.fna.fbcdn.net/v/t1.6435-9/82778178_776614262838528_2241883679091589120_n.jpg?_nc_cat=102&ccb=1-7&_nc_sid=a5f93a&_nc_ohc=ECowa4YMPDoQ7kNvwEjNIbY&_nc_oc=AdnN1-l5QBm1uEwDXvb1FLu9XrCcvNhD_IeKArSn59PvWSE3el6Z7WXdeeaDDt1NZns&_nc_zt=23&_nc_ht=scontent.fsgn2-8.fna&_nc_gid=AjUMF7j1V85PceRzi9mrdw&oh=00_AfFiSNh3cd62Rs_6DvYla8vo3kJE6Q0512_avl1dEygqHg&oe=68352C18'

ADMIN_AVATAR_URL = 'https://taimienphi.vn/tmp/cf/aut/anh-avatar-viet-nam-cute-ngau-tuyet-dep-1.jpg'

def upload_avatar_and_update_employee(user, avatar_url):
    # Bước 1: Download ảnh từ avatar_url cũ
    response = requests.get(avatar_url)
    if response.status_code == 200:
        image_bytes = response.content
        
        # Bước 2: Upload lên Cloudinary
        result = upload(image_bytes, public_id=f"user_avatar_{user.username}")
        cloudinary_url = result['url']
        
        # Bước 3: Tạo hoặc update Employee
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'salary': 10000000,
                'avartar_url': cloudinary_url,
            }
        )
        
        if not created:
            employee.avartar_url = cloudinary_url
            employee.save()
        
        print(f"✅ Avatar uploaded and updated for {user.username}")
    else:
        print(f"❌ Failed to download avatar from {avatar_url}")

class Command(BaseCommand):
    help = "Tạo tài khoản admin và member mặc định + thêm Employee"

    ADMIN_ACCOUNTS = [
        ("viettai", "123456", 'Viết', 'Tài', TAI_AVATAR_URL),
        ("an", "123456", 'Trường', 'Ân', AN_AVATAR_URL),
        ("hoang", "123456", 'Quốc', 'Hoàng', HOANG_AVATAR_URL),
        ("phu", "123456", 'Châu', 'Phú', PHU_AVATAR_URL),
        ("anh", "123456", 'Công', 'Anh', ANH_AVATAR_URL),
        ("admin", "123456", '', 'Admin', ADMIN_AVATAR_URL),
    ]

    def handle(self, *args, **kwargs):
        created_count = 0

        # Đảm bảo Group 'Member' tồn tại
        member_group, _ = Group.objects.get_or_create(name="Member")

        for username, password, last_name, first_name, avatar_url in self.ADMIN_ACCOUNTS:
            user = User.objects.filter(username=username).first()
            if not user:
                if username == "admin":
                    # Tạo superuser
                    user = User.objects.create_superuser(
                        username=username,
                        last_name=last_name,
                        first_name=first_name,
                        password=password,
                        email=f"{username}@rms.com"
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Đã tạo superuser: {username}"))
                else:
                    # Tạo member
                    user = User.objects.create_user(
                        username=username,
                        last_name=last_name,
                        first_name=first_name,
                        password=password,
                        email=f"{username}@rms.com"
                    )
                    user.is_staff = True
                    user.save()
                    user.groups.add(member_group)

                    upload_avatar_and_update_employee(user, avatar_url)
                    
                    self.stdout.write(self.style.SUCCESS(f"✅ Đã tạo member: {username}"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Tài khoản '{username}' đã tồn tại."))

            

        self.stdout.write(self.style.SUCCESS(f"🎉 Đã xử lý xong {len(self.ADMIN_ACCOUNTS)} tài khoản!"))
