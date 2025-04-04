# Generated by Django 5.1.3 on 2025-03-13 13:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_01', '0003_remove_ingredient_quantity_alter_ingredient_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bestsellingproduct',
            name='report_date',
            field=models.DateTimeField(),
        ),
        migrations.CreateModel(
            name='TableReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('many_person', models.IntegerField()),
                ('date', models.DateTimeField()),
                ('status', models.CharField(choices=[('pending', 'Chờ xác nhận'), ('confirmed', 'Đã xác nhận'), ('cancelled', 'Đã hủy')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web_01.table')),
            ],
            options={
                'db_table': 'table_reservation',
            },
        ),
    ]
