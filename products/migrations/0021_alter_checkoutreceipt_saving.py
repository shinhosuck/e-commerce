# Generated by Django 3.2 on 2023-10-12 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_alter_checkoutreceipt_saving'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutreceipt',
            name='saving',
            field=models.CharField(default='None', max_length=100),
        ),
    ]