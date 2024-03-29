# Generated by Django 3.1.13 on 2021-11-22 00:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20211121_1138'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transfertask',
            old_name='to_location',
            new_name='from_location',
        ),
        migrations.AlterField(
            model_name='convertmaterial',
            name='convert_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='core.converttask'),
        ),
    ]
