# Generated by Django 2.0.8 on 2019-04-03 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0033_simulation_model_object_timelines'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulation_model',
            name='number_of_additional_object_facts',
            field=models.IntegerField(default=2),
            preserve_default=False,
        ),
    ]
