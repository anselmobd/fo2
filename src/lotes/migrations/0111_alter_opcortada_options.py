# Generated by Django 3.2.16 on 2023-02-06 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0110_opcortada_colaborador'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='opcortada',
            options={'permissions': (('pode_marcar_op_como_cortada', 'Pode marcar OP como cortada'),), 'verbose_name': 'OP cortada', 'verbose_name_plural': 'OPs cortadas'},
        ),
    ]