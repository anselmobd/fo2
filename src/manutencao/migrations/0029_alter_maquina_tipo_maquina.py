# Generated by Django 3.2.16 on 2023-06-27 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manutencao', '0028_maquina_subtipo_maquina'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquina',
            name='tipo_maquina',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='manutencao.tipomaquina', verbose_name='Tipo de máquina'),
        ),
    ]
