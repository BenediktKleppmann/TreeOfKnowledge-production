# Generated by Django 2.0.8 on 2020-10-07 11:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0130_delete_execution_order_score'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Simulation_result',
            new_name='Monte_carlo_result',
        ),
    ]