# Generated by Django 3.2 on 2023-11-05 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_alter_checkoutreceipt_saving'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutreceipt',
            name='checkout_summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]
