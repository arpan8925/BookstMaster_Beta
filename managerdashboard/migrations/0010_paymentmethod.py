# Generated by Django 5.1 on 2024-11-10 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managerdashboard', '0009_transaction_fee_transaction_payment_method_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('manual', 'Manual'), ('automatic', 'Automatic')], max_length=20)),
                ('min_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('max_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fee_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount'), ('both', 'Both')], max_length=20)),
                ('fee_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('fee_fixed', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('client_id', models.CharField(blank=True, max_length=255, null=True)),
                ('client_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('test_mode', models.BooleanField(default=False)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='payment_icons/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]