# Generated by Django 2.0.8 on 2018-11-15 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0006_auto_20181113_2138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulation_model',
            name='id',
        ),
        migrations.RemoveField(
            model_name='simulation_model',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='uploaded_dataset',
            name='id',
        ),
        migrations.AddField(
            model_name='simulation_model',
            name='modelid',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploaded_dataset',
            name='uploadid',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]