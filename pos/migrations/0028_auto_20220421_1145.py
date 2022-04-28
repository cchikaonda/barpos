# Generated by Django 3.0.9 on 2022-04-21 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0027_auto_20220421_1140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='refundpayment',
            old_name='paid_amount',
            new_name='refund_amount',
        ),
        migrations.RenameField(
            model_name='refundpayment',
            old_name='paid_amount_currency',
            new_name='refund_amount_currency',
        ),
        migrations.RemoveField(
            model_name='refundpayment',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='refundpayment',
            name='order_type',
        ),
    ]
