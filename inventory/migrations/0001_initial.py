# Generated by Django 4.0.4 on 2022-06-04 18:20

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BatchNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_number', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('item_description', models.CharField(max_length=100)),
                ('barcode', models.IntegerField(unique=True)),
                ('image', models.ImageField(blank=True, default='ecom_product6_b.png', null=True, upload_to='items/')),
                ('cost_price_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('cost_price', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='MWK', max_digits=14)),
                ('total_cost_price_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('total_cost_price', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='MWK', max_digits=14)),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='MWK', max_digits=14)),
                ('discount_price_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('discount_price', djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='MWK', max_digits=14, null=True)),
                ('quantity_at_hand', models.IntegerField(default=0)),
                ('reorder_level', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('slug', models.SlugField()),
            ],
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=50)),
                ('category_description', models.CharField(max_length=100)),
                ('category_colour', models.CharField(choices=[('Black', 'dark'), ('Orange', 'warning'), ('Red', 'danger'), ('Blue', 'primary'), ('Light Black', 'light'), ('Light Blue', 'info'), ('Green', 'success')], default='Blue', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('address', models.CharField(max_length=120)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('description', models.CharField(max_length=70)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_short_name', models.CharField(max_length=10)),
                ('unit_description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered_price_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('ordered_price', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='MWK', max_digits=14)),
                ('previous_quantity', models.IntegerField(default=0)),
                ('stock_in', models.IntegerField(default=0)),
                ('new_quantity', models.IntegerField(default=0)),
                ('unit_quantity', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('total_cost_of_items_currency', djmoney.models.fields.CurrencyField(choices=[('MWK', 'Malawian Kwacha')], default='MWK', editable=False, max_length=3)),
                ('total_cost_of_items', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='MWK', max_digits=14)),
                ('batch', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.batchnumber')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item')),
                ('supplier_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.supplier')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.itemcategory'),
        ),
        migrations.AddField(
            model_name='item',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.unit'),
        ),
    ]
