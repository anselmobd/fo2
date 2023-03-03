# Generated by Django 3.2.16 on 2023-03-03 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0035_delete_imagemtag'),
        ('lotes', '0136_alter_opcomcorte_cortada_colab'),
    ]

    operations = [
        migrations.AddField(
            model_name='opcomcorte',
            name='pedido_fm_colab',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, related_name='op_pedido_fm_colab', to='base.colaborador', verbose_name='Pedido-FM colaborador'),
            preserve_default=False,
        ),
    ]
