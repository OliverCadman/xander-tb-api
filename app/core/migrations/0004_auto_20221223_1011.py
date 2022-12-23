# Generated by Django 3.2.16 on 2022-12-23 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_postcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingPostcode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('postcode', models.CharField(max_length=20)),
                ('full_order', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.fullorder')),
                ('null_order', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.nullorder')),
                ('todays_order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.todaysorder')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryPostcode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('postcode', models.CharField(max_length=20)),
                ('full_order', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.fullorder')),
                ('null_order', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.nullorder')),
                ('todays_order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.todaysorder')),
            ],
        ),
        migrations.DeleteModel(
            name='Postcode',
        ),
    ]
