# Generated by Django 2.1.15 on 2021-09-28 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ti', '0030_ostype'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='use',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Uso'),
        ),
    ]
