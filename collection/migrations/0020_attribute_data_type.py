# Generated by Django 2.0.8 on 2019-02-15 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0019_auto_20190215_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='data_type',
            field=models.TextField(default='string'),
            preserve_default=False,
        ),
    ]
