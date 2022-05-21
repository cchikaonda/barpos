# Generated by Django 3.2 on 2022-05-18 11:18

from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0004_auto_20220518_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='amount_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='expense',
            name='payment_mode',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Mpamba', 'Mpamba'), ('Airtel Money', 'Airtel Money'), ('Bank', 'Bank')], default='Cash', max_length=15),
        ),
        migrations.RemoveField(
            model_name='expense',
            name='amount',
        ),
        migrations.AddField(
            model_name='expense',
            name='amount',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='MWK', max_digits=14, null=True),
        ),
        migrations.DeleteModel(
            name='ExpensePayment',
        ),
    ]
