# Generated migration to fix updated_at field name

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='otpverify',
            old_name='update_at',
            new_name='updated_at',
        ),
    ]
