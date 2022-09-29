# Generated by Django 2.1.15 on 2022-09-28 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cd', '0004_permissions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cdpermissions',
            options={'managed': False, 'permissions': (('can_admin_pallet', 'Pode administrar paletes'), ('can_view_grades_estoque', 'Pode visualizar grades do estoque'), ('can_del_lote_de_palete', 'Pode retirar lote de palete'), ('pode_finalizar_empenho_op_finalizada', 'Pode finalizar empenho de OP finalizada'), ('imprime_etq_palete', 'Imprime etiqueta de palete')), 'verbose_name': 'Permissões do CD'},
        ),
    ]