# Generated by Django 2.1.15 on 2022-01-10 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_requisicaoauto_colaborador'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagem',
            name='caminho',
            field=models.CharField(default='', max_length=255),
        ),
    ]