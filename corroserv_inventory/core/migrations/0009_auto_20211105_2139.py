# Generated by Django 3.1.13 on 2021-11-05 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20211105_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singleopeninventory',
            name='inventory_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='open_inventory_item', to='core.inventory'),
        ),
    ]
