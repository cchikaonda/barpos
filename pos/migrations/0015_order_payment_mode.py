# Generated by Django 3.0.9 on 2021-12-09 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0014_auto_20211209_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_mode',
            field=models.CharField(default='Cash', max_length=50, null=True),
        ),
    ]
