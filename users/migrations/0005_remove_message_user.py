# Generated by Django 3.2 on 2023-10-23 01:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_message_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
    ]
