# Generated by Django 3.2.16 on 2023-03-03 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0131_opcomcorte_cortado_quando'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opcomcorte',
            name='pedido_filial',
        ),
        migrations.AddField(
            model_name='opcomcorte',
            name='pedido_fm_num',
            field=models.IntegerField(blank=True, null=True, verbose_name='Pedido-FM número'),
        ),
    ]