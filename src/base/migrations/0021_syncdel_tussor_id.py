# Generated by Django 2.1.15 on 2021-07-29 20:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_empresa_numero_unique'),
    ]

    operations = [
        migrations.RenameField(
            model_name='syncdel',
            old_name='sync_id',
            new_name='tussor_id',
        ),
    ]
