# Generated by Django 2.1.15 on 2022-02-03 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0049_notafiscal_quantidade'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='tipo',
            field=models.CharField(choices=[('a', 'Atacado'), ('v', 'Varejo'), ('o', '')], default='o', max_length=1),
        ),
    ]
