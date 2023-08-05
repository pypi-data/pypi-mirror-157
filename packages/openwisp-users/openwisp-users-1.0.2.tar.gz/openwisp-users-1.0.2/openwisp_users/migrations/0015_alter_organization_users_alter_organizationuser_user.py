# Generated by Django 4.0rc1 on 2021-11-23 15:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openwisp_users', '0014_user_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='users',
            field=models.ManyToManyField(
                related_name='%(app_label)s_%(class)s',
                through='openwisp_users.OrganizationUser',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='organizationuser',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(app_label)s_%(class)s',
                to='openwisp_users.user',
            ),
        ),
    ]
