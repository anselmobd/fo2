# Generated by Django 2.1.15 on 2021-07-16 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0044_nfentrada_volumes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nfentrada',
            name='cadastro',
            field=models.CharField(default='', max_length=20, verbose_name='CNPJ/CPF'),
        ),
    ]
