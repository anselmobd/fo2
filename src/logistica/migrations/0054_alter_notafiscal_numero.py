# Generated by Django 3.2.16 on 2023-07-24 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0053_alter_notafiscal_trail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notafiscal',
            name='numero',
            field=models.IntegerField(db_index=True, verbose_name='número'),
        ),
    ]
