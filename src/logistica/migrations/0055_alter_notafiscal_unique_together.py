# Generated by Django 3.2.16 on 2023-07-24 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0054_alter_notafiscal_numero'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notafiscal',
            unique_together={('empresa', 'numero')},
        ),
    ]