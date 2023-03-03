# Generated by Django 3.2.16 on 2023-03-03 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0035_delete_imagemtag'),
        ('lotes', '0139_alter_opcomcorte_pedido_fm_quando'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opcomcorte',
            name='pedido_fm_colab',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='op_pedido_fm_colab', to='base.colaborador', verbose_name='Pedido-FM colaborador'),
        ),
    ]
