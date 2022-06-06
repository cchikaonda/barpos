# Generated by Django 4.0.4 on 2022-06-04 18:20

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('address', models.TextField(null=True)),
                ('total_orders', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='0000', max_length=50, null=True)),
                ('order_type', models.CharField(choices=[('Cash', 'Cash'), ('Lay By', 'Lay By')], default='Cash', max_length=15)),
                ('ordered', models.BooleanField(default=False)),
                ('order_total_cost_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('order_total_cost', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14)),
                ('vat_p', models.FloatField(default=16.5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment_reference', models.CharField(max_length=50, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.customer')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(default='', max_length=30)),
                ('ordered', models.BooleanField(default=False)),
                ('quantity', models.IntegerField(default=0)),
                ('ordered_item_price_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('ordered_item_price', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14)),
                ('ordered_items_total_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('ordered_items_total', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14)),
                ('ordered_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pos.customer')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RefundPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_mode', models.CharField(choices=[('Cash', 'Cash'), ('Mpamba', 'Mpamba'), ('Airtel Money', 'Airtel Money'), ('Bank', 'Bank')], default='Cash', max_length=15)),
                ('order_id', models.CharField(max_length=20, null=True)),
                ('refund_amount_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('refund_amount', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='MWK', max_digits=14, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RefundOrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(default='', max_length=30)),
                ('return_quantity', models.IntegerField(default=0)),
                ('initial_quantity', models.IntegerField(default=0)),
                ('return_items_total_cost_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('return_items_total_cost', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14)),
                ('returned_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('restock_to_inventory', models.BooleanField(default=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.orderitem')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RefundOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='0000', max_length=50, null=True)),
                ('refunded', models.BooleanField(default=False)),
                ('ordered_total_cost_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('ordered_total_cost', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reason_for_refund', models.CharField(max_length=100, null=True)),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.order')),
                ('payments', models.ManyToManyField(to='pos.refundpayment')),
                ('refunded_items', models.ManyToManyField(to='pos.refundorderitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_mode', models.CharField(choices=[('Cash', 'Cash'), ('Mpamba', 'Mpamba'), ('Airtel Money', 'Airtel Money'), ('Bank', 'Bank')], default='Cash', max_length=15)),
                ('order_id', models.CharField(max_length=20, null=True)),
                ('order_type', models.CharField(max_length=20, null=True)),
                ('service_fee_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('service_fee', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14)),
                ('paid_amount_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('paid_amount', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pos.customer')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(to='pos.orderitem'),
        ),
        migrations.AddField(
            model_name='order',
            name='payments',
            field=models.ManyToManyField(to='pos.payment'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='LayByOrders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sum_paid_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('sum_paid', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='MWK', max_digits=14)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.order')),
                ('payments', models.ManyToManyField(to='pos.payment')),
            ],
        ),
    ]
