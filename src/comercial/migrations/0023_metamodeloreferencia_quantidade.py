# Generated by Django 2.1.15 on 2022-08-03 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0022_comercial_protect'),
    ]

    operations = [
        migrations.AddField(
            model_name='metamodeloreferencia',
            name='quantidade',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
