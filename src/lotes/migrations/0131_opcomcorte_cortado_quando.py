# Generated by Django 3.2.16 on 2023-03-03 16:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0130_opcomcorte_cortado_colab'),
    ]

    operations = [
        migrations.AddField(
            model_name='opcomcorte',
            name='cortado_quando',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Cortado quando'),
        ),
    ]
