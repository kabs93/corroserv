# Generated by Django 3.1.13 on 2021-11-05 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20211105_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singleopeninventory',
            name='inventory_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='open_inventory_items', to='core.inventory'),
        ),
    ]
