# Generated by Django 3.0.9 on 2022-05-03 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0031_auto_20220429_1513'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='refundpayment',
            name='reference',
        ),
        migrations.AddField(
            model_name='refundorder',
            name='reason_for_refund',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
