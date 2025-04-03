# Generated by Django 5.1.3 on 2025-03-10 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_01', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='status',
            field=models.CharField(choices=[('available', 'Trống'), ('occupied', 'Đang sử dụng'), ('reserved', 'Đã đặt trước')], default='available', max_length=10),
        ),
    ]
