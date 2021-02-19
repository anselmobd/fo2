from django.db import models


class dis_dup(models.Model):
    d_dupnum = models.CharField(db_index=True, max_length=7)
    d_fatnum = models.IntegerField()
    d_cgc = models.CharField(max_length=14)
    d_pednum = models.IntegerField()
    d_valor = models.DecimalField(max_digits=9, decimal_places=2)
    d_dvenc = models.DateField()
    d_dfat = models.DateField()
    d_dcanc = models.DateField()
    d_dpago = models.DateField()
    d_vpago = models.DecimalField(max_digits=9, decimal_places=2)
    d_icm = models.IntegerField()
    d_stat = models.CharField(max_length=1)
    d_statori = models.CharField(max_length=1)
    d_op = models.CharField(max_length=2)
    d_banco = models.CharField(max_length=3)
    d_desconto = models.CharField(max_length=1)
    d_cpag = models.CharField(max_length=1)
    d_cond = models.IntegerField()
    d_qtd = models.IntegerField()
    d_qtdfat = models.IntegerField()
    d_caixas = models.IntegerField()
    d_pesbru = models.DecimalField(max_digits=7, decimal_places=2)
    d_juros = models.DecimalField(max_digits=5, decimal_places=2)
    d_desc = models.DecimalField(max_digits=4, decimal_places=2)
    d_descf1 = models.DecimalField(max_digits=4, decimal_places=2)
    d_descf2 = models.DecimalField(max_digits=4, decimal_places=2)
    d_tipdescf = models.CharField(max_length=1)
    d_repr = models.CharField(max_length=4)
    d_comi = models.DecimalField(max_digits=3, decimal_places=1)
    d_codfis = models.CharField(max_length=4)
    d_transp = models.CharField(max_length=2)
    d_pc = models.DecimalField(max_digits=10, decimal_places=4)
    d_protest = models.CharField(max_length=1)
    d_especial = models.CharField(max_length=1)
    d_777 = models.DecimalField(max_digits=9, decimal_places=2)
    d_qtd777 = models.IntegerField()
    d_obs = models.CharField(max_length=14)
    d_aux = models.CharField(max_length=1)
    d_978 = models.DecimalField(max_digits=9, decimal_places=2)
    d_qtd978 = models.IntegerField()
    rec_ver = models.IntegerField()
    d_tipocanc = models.IntegerField()
    d_prortip = models.CharField(max_length=1)
    calc_cgc = models.CharField(max_length=8)
    d_modfrete = models.CharField(max_length=1)
    f_f1 = models.CharField(max_length=1)
    d_repr2 = models.CharField(max_length=3)
    d_dentr = models.DateField()
    d_dsaida = models.DateField()
    d_snagenda = models.CharField(max_length=1)
    d_snentreg = models.CharField(max_length=1)
    d_dxmlsent = models.DateField()
    d_dtrem = models.DateField()
    d_arqrem = models.CharField(max_length=8)
    d_dvencori = models.DateField()
    d_dvencrem = models.DateField()
    d_dxmlsend = models.DateField()
    d_xmlenvia = models.CharField(max_length=1)
    d_obsentr = models.CharField(max_length=80)
    d_descfat = models.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        db_table = "tussor_dis_dup"


class dis_cli(models.Model):
    c_cgc = models.CharField(db_index=True, max_length=14)
    c_rsoc = models.CharField(max_length=40)
    c_end = models.CharField(max_length=40)
    c_bairro = models.CharField(max_length=25)
    c_munic = models.CharField(max_length=25)
    c_telex = models.CharField(max_length=25)
    c_ddd = models.CharField(max_length=4)
    c_tel = models.CharField(max_length=20)
    c_uf = models.CharField(max_length=2)
    c_cep = models.CharField(max_length=9)
    c_inest = models.CharField(max_length=18)
    c_lc = models.CharField(max_length=1)
    c_repr = models.CharField(max_length=3)
    c_desde = models.DateField()
    c_sufr = models.CharField(max_length=15)
    c_banco = models.CharField(max_length=3)
    c_obs = models.CharField(max_length=60)
    c_obs2 = models.CharField(max_length=60)
    c_obs3 = models.CharField(max_length=60)
    c_display = models.IntegerField()
    c_disdata = models.DateField()
    cc_cgc = models.CharField(max_length=14)
    cc_rsoc = models.CharField(max_length=40)
    cc_end = models.CharField(max_length=40)
    cc_bairro = models.CharField(max_length=25)
    cc_munic = models.CharField(max_length=25)
    cc_telex = models.CharField(max_length=25)
    cc_inest = models.CharField(max_length=18)
    cc_tel = models.CharField(max_length=20)
    cc_ddd = models.CharField(max_length=4)
    cc_uf = models.CharField(max_length=2)
    cc_cep = models.CharField(max_length=9)
    rec_ver = models.IntegerField()
    c_isento = models.CharField(max_length=1)
    c_le = models.CharField(max_length=10)
    ce_cgc = models.CharField(max_length=14)
    ce_inest = models.CharField(max_length=18)
    ce_rsoc = models.CharField(max_length=40)
    ce_cep = models.CharField(max_length=9)
    ce_end = models.CharField(max_length=40)
    ce_bairro = models.CharField(max_length=25)
    ce_munic = models.CharField(max_length=25)
    ce_uf = models.CharField(max_length=2)
    c_endok = models.CharField(max_length=1)
    malaok = models.CharField(max_length=1)
    c_transp = models.CharField(max_length=2)
    origem = models.CharField(max_length=1)
    c_email = models.CharField(max_length=100)
    c_email2 = models.CharField(max_length=100)
    dadosok = models.CharField(max_length=1)
    seleciona = models.CharField(max_length=1)
    f_f1 = models.CharField(max_length=1)
    c_repr2 = models.CharField(max_length=3)
    calc_cgc = models.CharField(max_length=8)
    c_piscof = models.CharField(max_length=1)
    c_tipo = models.CharField(max_length=1)
    c_cmun = models.CharField(max_length=7)
    ce_cmun = models.CharField(max_length=7)
    cc_cmun = models.CharField(max_length=7)

    class Meta:
        db_table = "tussor_dis_cli"
