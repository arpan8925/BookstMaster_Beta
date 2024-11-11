from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('user_dashboard', '0001_initial'),  # Replace with your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ] 