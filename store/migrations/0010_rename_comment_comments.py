# Generated by Django 3.2.3 on 2022-04-14 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_comment_post'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Comment',
            new_name='Comments',
        ),
    ]
