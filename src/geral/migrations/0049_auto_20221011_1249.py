# Generated by Django 3.0.14 on 2022-10-11 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0048_proxyuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informacaomodulo',
            name='habilitado',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='painel',
            name='habilitado',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='painelmodulo',
            name='habilitado',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='parametro',
            name='habilitado',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='parametro',
            name='usuario',
            field=models.BooleanField(default=True, verbose_name='usuário'),
        ),
        migrations.AlterField(
            model_name='pop',
            name='habilitado',
            field=models.BooleanField(default=True),
        ),
    ]
