# Generated by Django 2.1.15 on 2021-09-30 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Nome')),
                ('slug', models.SlugField(unique=True, verbose_name='Nome-chave')),
            ],
            options={
                'verbose_name': 'Empresa',
                'db_table': 'fo2_itat_company',
            },
        ),
        migrations.CreateModel(
            name='DhcpConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nome')),
                ('slug', models.SlugField()),
                ('primary_template', models.CharField(blank=True, max_length=65535, null=True, verbose_name='Gabarito para o servidor primário (ou único)')),
                ('secondary_template', models.CharField(blank=True, max_length=65535, null=True, verbose_name='Gabarito para o servidor secundário')),
            ],
            options={
                'verbose_name': 'Configuração DHCP',
                'verbose_name_plural': 'Configurações DHCP',
                'db_table': 'fo2_itat_dhcp_config',
            },
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nome')),
                ('slug', models.SlugField(unique=True, verbose_name='Nome-chave')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='Descrição')),
                ('application', models.CharField(blank=True, max_length=200, null=True, verbose_name='Uso')),
                ('users', models.CharField(blank=True, max_length=100, null=True, verbose_name='Usuário(s)')),
                ('primary_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Principal')),
            ],
            options={
                'verbose_name': 'Equipamento',
                'db_table': 'fo2_itat_equipment',
            },
        ),
        migrations.CreateModel(
            name='EquipmentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Nome')),
                ('slug', models.SlugField()),
            ],
            options={
                'verbose_name': 'Tipo de equipamento',
                'verbose_name_plural': 'Tipos de equipamentos',
                'db_table': 'fo2_itat_equipment_type',
            },
        ),
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nome')),
                ('slug', models.SlugField()),
                ('mac_adress', models.CharField(blank=True, max_length=17, null=True, verbose_name='Endereço MAC')),
                ('fixed_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')),
                ('dhcp_config', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='itat.DhcpConfig', verbose_name='Configuração de DHCP')),
                ('equipment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='itat.Equipment', verbose_name='Equipamento')),
            ],
            options={
                'db_table': 'fo2_itat_interface',
            },
        ),
        migrations.CreateModel(
            name='InterfaceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Nome')),
                ('slug', models.SlugField()),
            ],
            options={
                'verbose_name': 'Tipo de interface',
                'verbose_name_plural': 'Tipos de interfaces',
                'db_table': 'fo2_itat_interface_type',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Nome')),
                ('slug', models.SlugField(unique=True, verbose_name='Nome-chave')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='itat.Company')),
            ],
            options={
                'verbose_name': 'Local em empresa',
                'db_table': 'fo2_itat_location',
            },
        ),
        migrations.CreateModel(
            name='OS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='Nome')),
                ('version', models.CharField(max_length=60, verbose_name='Versão')),
                ('bits', models.IntegerField(blank=True, null=True)),
                ('slug', models.SlugField(unique=True, verbose_name='Nome-chave')),
            ],
            options={
                'verbose_name': 'SO',
                'verbose_name_plural': 'SO',
                'db_table': 'fo2_itat_os',
            },
        ),
        migrations.CreateModel(
            name='OSType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='Nome')),
                ('slug', models.SlugField(unique=True, verbose_name='Nome-chave')),
            ],
            options={
                'verbose_name': 'Tipo de SO',
                'verbose_name_plural': 'Tipos de SO',
                'db_table': 'fo2_itat_os_type',
            },
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Nome')),
                ('path', models.CharField(max_length=200, verbose_name='Caminho')),
                ('read_only', models.BooleanField(default=False, verbose_name='Somente leitura')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='itat.Equipment', verbose_name='Servidor')),
            ],
            options={
                'verbose_name': 'Compartilhamento',
                'db_table': 'fo2_itat_share',
            },
        ),
        migrations.AddField(
            model_name='os',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='itat.OSType', verbose_name='Tipo'),
        ),
        migrations.AddField(
            model_name='interface',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='itat.InterfaceType', verbose_name='Tipo'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='itat.EquipmentType', verbose_name='Tipo'),
        ),
        migrations.AddField(
            model_name='dhcpconfig',
            name='primary_equipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='primary_dhcp', to='itat.Equipment', verbose_name='Equipamento primário'),
        ),
        migrations.AddField(
            model_name='dhcpconfig',
            name='secondary_equipment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='secondary_dhcp', to='itat.Equipment', verbose_name='Equipamento secundário'),
        ),
    ]