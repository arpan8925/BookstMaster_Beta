# Generated by Django 5.1 on 2024-11-10 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_remove_user_created_at_remove_user_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='api_key',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='timezone',
            field=models.CharField(default='UTC', max_length=50),
        ),
    ]
