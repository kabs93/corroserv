# Generated by Django 3.1.13 on 2021-11-19 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20211117_0624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singleopeninventory',
            name='remaining',
            field=models.FloatField(),
        ),
    ]
