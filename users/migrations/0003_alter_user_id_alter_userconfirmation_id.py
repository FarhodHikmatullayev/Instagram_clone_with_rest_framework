# Generated by Django 4.2.4 on 2023-08-12 09:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_id_alter_userconfirmation_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('a9367433-2242-4842-85fe-893c011474c7'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='userconfirmation',
            name='id',
            field=models.UUIDField(default=uuid.UUID('a9367433-2242-4842-85fe-893c011474c7'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]