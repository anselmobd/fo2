# Generated by Django 2.1.15 on 2022-09-14 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0024_remove_metamodeloreferencia_incl_excl'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='metamodeloreferencia',
            options={'verbose_name': 'Pacote de modelo para meta', 'verbose_name_plural': 'Pacotes de modelos para meta'},
        ),
        migrations.AlterField(
            model_name='metamodeloreferencia',
            name='referencia',
            field=models.CharField(max_length=5, verbose_name='Pacote'),
        ),
    ]
