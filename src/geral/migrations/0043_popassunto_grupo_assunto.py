# Generated by Django 2.1.15 on 2022-05-10 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0042_popgrupoassunto_loaddata'),
    ]

    operations = [
        migrations.AddField(
            model_name='popassunto',
            name='grupo_assunto',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='geral.PopGrupoAssunto'),
        ),
    ]
