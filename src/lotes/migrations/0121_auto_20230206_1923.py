# Generated by Django 3.2.16 on 2023-02-06 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0120_alter_opcortada_version'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opcortada',
            name='origin_id',
        ),
        migrations.AddField(
            model_name='opcortada',
            name='log',
            field=models.IntegerField(default=0, verbose_name='log'),
        ),
    ]
