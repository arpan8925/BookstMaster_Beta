from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('user_dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ] 