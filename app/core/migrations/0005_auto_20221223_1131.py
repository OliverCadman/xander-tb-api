# Generated by Django 3.2.16 on 2022-12-23 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20221223_1011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fullorder',
            name='billing_postcode',
        ),
        migrations.RemoveField(
            model_name='fullorder',
            name='delivery_postcode',
        ),
        migrations.RemoveField(
            model_name='nullorder',
            name='billing_postcode',
        ),
        migrations.RemoveField(
            model_name='nullorder',
            name='delivery_postcode',
        ),
        migrations.RemoveField(
            model_name='todaysorder',
            name='billing_postcode',
        ),
        migrations.RemoveField(
            model_name='todaysorder',
            name='delivery_postcode',
        ),
    ]
