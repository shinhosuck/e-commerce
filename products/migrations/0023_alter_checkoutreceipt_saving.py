# Generated by Django 3.2 on 2023-10-13 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0022_alter_checkoutreceipt_saving'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutreceipt',
            name='saving',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
