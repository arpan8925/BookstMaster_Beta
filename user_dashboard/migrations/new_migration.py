from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('user_dashboard', '0001_initial'),  # Replace with your last migration
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='payment_details',
            new_name='description',
        ),
    ] 