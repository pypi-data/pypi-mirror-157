# Generated by Django 3.1 on 2020-08-23 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('openwisp_users', '0010_allow_admins_change_organization')]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(
                blank=True, max_length=150, verbose_name='first name'
            ),
        )
    ]
