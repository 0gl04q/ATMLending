# Generated by Django 4.2.3 on 2023-09-17 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lending', '0003_info_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='company',
            field=models.CharField(default='', max_length=100),
        ),
    ]