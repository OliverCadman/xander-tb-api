# Generated by Django 3.2.16 on 2022-12-13 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todaysorder',
            name='delivery_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='todaysorder',
            name='delivery_status',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='todaysorder',
            name='dispatch_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='todaysorder',
            name='dispatch_status',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
