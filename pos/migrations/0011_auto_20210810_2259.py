# Generated by Django 3.0.9 on 2021-08-10 22:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0010_auto_20210810_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paid_amount',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pos.Payment'),
        ),
    ]
