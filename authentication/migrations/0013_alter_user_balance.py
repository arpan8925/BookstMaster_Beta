# Generated by Django 5.0.9 on 2025-02-26 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_alter_user_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='balance',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=5),
        ),
    ]
