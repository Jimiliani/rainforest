# Generated by Django 3.1.5 on 2021-07-20 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_backends', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='balance',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
