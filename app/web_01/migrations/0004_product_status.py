# Generated by Django 5.1.3 on 2025-05-07 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_01', '0003_order_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('active', 'Hoạt động'), ('inactive', 'Ngưng hoạt động')], default='active', max_length=10),
        ),
    ]
