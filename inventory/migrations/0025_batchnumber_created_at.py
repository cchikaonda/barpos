# Generated by Django 3.2 on 2022-05-18 07:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_batchnumber_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchnumber',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
