# Generated by Django 3.2.16 on 2023-07-24 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0060_alter_notafiscal_comprovante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notafiscal',
            name='comprovante',
            field=models.BooleanField(default=False, verbose_name='comprovante'),
        ),
    ]
