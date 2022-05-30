# Generated by Django 2.1.15 on 2022-05-30 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0093_inventariolote_diferenca'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField(verbose_name='início')),
            ],
            options={
                'verbose_name': 'Inventário',
                'db_table': 'fo2_inventario',
            },
        ),
    ]
