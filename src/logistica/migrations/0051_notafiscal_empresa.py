# Generated by Django 3.2.16 on 2023-07-24 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0050_notafiscal_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='empresa',
            field=models.SmallIntegerField(db_index=True, default=1),
        ),
    ]
