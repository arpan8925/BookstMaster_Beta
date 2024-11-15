# Generated by Django 5.1 on 2024-11-09 18:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managerdashboard', '0003_remove_provider_currency'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Service Categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_id', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=100)),
                ('rate', models.DecimalField(decimal_places=4, max_digits=10)),
                ('min_order', models.IntegerField()),
                ('max_order', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('deactive', 'Deactive')], default='active', max_length=20)),
                ('is_drip_feed', models.BooleanField(default=False)),
                ('drip_feed_rules', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='managerdashboard.provider')),
            ],
            options={
                'ordering': ['category', 'name'],
                'unique_together': {('provider', 'service_id')},
            },
        ),
        migrations.CreateModel(
            name='ServiceUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_rate', models.DecimalField(decimal_places=4, max_digits=10)),
                ('new_rate', models.DecimalField(decimal_places=4, max_digits=10)),
                ('old_min', models.IntegerField()),
                ('new_min', models.IntegerField()),
                ('old_max', models.IntegerField()),
                ('new_max', models.IntegerField()),
                ('old_status', models.CharField(max_length=20)),
                ('new_status', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='managerdashboard.service')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
