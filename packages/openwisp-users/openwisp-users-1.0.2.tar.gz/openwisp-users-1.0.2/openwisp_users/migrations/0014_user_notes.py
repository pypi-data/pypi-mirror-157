# Generated by Django 3.1.6 on 2021-02-15 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openwisp_users', '0013_user_birth_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notes',
            field=models.TextField(
                blank=True,
                help_text='notes for internal usage',
                verbose_name='notes',
            ),
        ),
    ]
