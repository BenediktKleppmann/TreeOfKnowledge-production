# Generated by Django 2.0.8 on 2019-09-23 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0075_simulation_model_correct_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploaded_dataset',
            name='upload_only_matched_entities',
            field=models.TextField(default='False'),
            preserve_default=False,
        ),
    ]
