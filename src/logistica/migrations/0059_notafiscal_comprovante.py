# Generated by Django 3.2.16 on 2023-07-24 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0058_alter_notafiscal_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='comprovante',
            field=models.BooleanField(default=None, null=True, verbose_name='Com comprovante'),
        ),
    ]
