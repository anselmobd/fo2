# Generated by Django 3.2.16 on 2023-02-06 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lotes', '0116_auto_20230206_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opcortada',
            name='origin_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='origin_user_table_heap1', to=settings.AUTH_USER_MODEL, verbose_name='usuário de origem'),
        ),
    ]