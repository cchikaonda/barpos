# Generated by Django 3.0.9 on 2022-04-13 21:10

from decimal import Decimal
from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0018_auto_20220413_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paid_amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='order',
            name='payments',
            field=models.ManyToManyField(to='pos.Payment'),
        ),
        migrations.AlterField(
            model_name='order',
            name='paid_amount',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14),
        ),
    ]
