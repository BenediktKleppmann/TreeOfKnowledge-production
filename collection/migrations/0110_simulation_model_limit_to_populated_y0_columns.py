# Generated by Django 2.0.8 on 2020-08-15 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0109_simulation_model_simulation_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulation_model',
            name='limit_to_populated_y0_columns',
            field=models.BooleanField(default=False),
        ),
    ]