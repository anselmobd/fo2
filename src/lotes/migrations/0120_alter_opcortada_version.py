# Generated by Django 3.2.16 on 2023-02-06 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0119_remove_opcortada_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opcortada',
            name='version',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='versão'),
        ),
    ]