# Generated by Django 2.1.15 on 2022-02-02 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0048_nfentrada_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='quantidade',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
