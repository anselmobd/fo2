# Generated by Django 2.1.15 on 2022-05-10 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0046_geral_protect'),
    ]

    operations = [
        migrations.AddField(
            model_name='pop',
            name='topico',
            field=models.CharField(blank=True, max_length=255, verbose_name='tópico'),
        ),
    ]
