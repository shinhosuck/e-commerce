# Generated by Django 3.2 on 2023-10-19 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellers', '0005_alter_sellersignup_member_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellersignup',
            name='province',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='sellersignup',
            name='state',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]