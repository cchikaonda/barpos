# Generated by Django 3.0.9 on 2021-08-10 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0013_auto_20210810_2316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paid_amount',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='pos.Payment'),
        ),
    ]
