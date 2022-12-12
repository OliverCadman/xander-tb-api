# Generated by Django 3.2.16 on 2022-12-11 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FullOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=30, unique=True)),
                ('toothbrush_type', models.CharField(max_length=20)),
                ('order_date', models.DateTimeField()),
                ('customer_age', models.IntegerField()),
                ('order_quantity', models.IntegerField()),
                ('delivery_postcode', models.CharField(max_length=20)),
                ('billing_postcode', models.CharField(max_length=20)),
                ('is_first', models.BooleanField()),
                ('dispatch_status', models.CharField(max_length=30)),
                ('dispatch_date', models.DateTimeField()),
                ('delivery_status', models.CharField(max_length=30)),
                ('delivery_date', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NullOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=30, unique=True)),
                ('toothbrush_type', models.CharField(max_length=20)),
                ('order_date', models.DateTimeField()),
                ('customer_age', models.IntegerField()),
                ('order_quantity', models.IntegerField()),
                ('delivery_postcode', models.CharField(max_length=20)),
                ('billing_postcode', models.CharField(max_length=20)),
                ('is_first', models.BooleanField()),
                ('dispatch_status', models.CharField(blank=True, max_length=30, null=True)),
                ('dispatch_date', models.DateTimeField(blank=True, null=True)),
                ('delivery_status', models.CharField(blank=True, max_length=30, null=True)),
                ('delivery_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TodaysOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=30, unique=True)),
                ('toothbrush_type', models.CharField(max_length=20)),
                ('order_date', models.DateTimeField()),
                ('customer_age', models.IntegerField()),
                ('order_quantity', models.IntegerField()),
                ('delivery_postcode', models.CharField(max_length=20)),
                ('billing_postcode', models.CharField(max_length=20)),
                ('is_first', models.BooleanField()),
                ('dispatch_status', models.CharField(max_length=30)),
                ('dispatch_date', models.DateTimeField()),
                ('delivery_status', models.CharField(max_length=30)),
                ('delivery_date', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]