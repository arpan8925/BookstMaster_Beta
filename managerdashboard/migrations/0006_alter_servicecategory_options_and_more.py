# Generated by Django 5.1 on 2024-11-09 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managerdashboard', '0005_alter_service_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicecategory',
            options={'ordering': ['name'], 'verbose_name_plural': 'Service Categories'},
        ),
        migrations.RemoveField(
            model_name='servicecategory',
            name='order',
        ),
    ]