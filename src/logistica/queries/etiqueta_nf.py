from django.db import connections

from utils.functions.format import format_cnpj
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all_ = ['get_dados_nf']


def get_dados_nf(cursor, nf, empresa):
    sql = f"""
        SELECT
          f.NUM_NOTA_FISCAL nf_num
        , f.SERIE_NOTA_FISC nf_ser
        , f.CODIGO_EMPRESA
        , f.QTDE_EMBALAGENS vols
        , f.PESO_BRUTO peso_tot
        , f.PEDIDO_VENDA ped
        , f.CGC_9 cli_cnpj9
        , f.CGC_4 cli_cnpj4
        , f.CGC_2 cli_cnpj2
        , f.TRANSPOR_FORNE9 transp_cnpj9
        , f.TRANSPOR_FORNE4 transp_cnpj4
        , f.TRANSPOR_FORNE2 transp_cnpj2
        , COALESCE(ped.COD_PED_CLIENTE, ' ') ped_cli
        , c.NOME_CLIENTE cli_nome
        , c.FANTASIA_CLIENTE cli_fant
        , c.ENDERECO_CLIENTE ende
        , c.NUMERO_IMOVEL end_num
        , c.COMPLEMENTO end_compl
        , c.BAIRRO end_bairro
        , cid.CIDADE end_cid
        , cid.ESTADO end_uf
        , c.CEP_CLIENTE end_cep
        , t.NOME_FORNECEDOR transp_nome
        , e.NOME_EMPRESA remet_nome
        , e.CGC_9 remet_cnpj9
        , e.CGC_4 remet_cnpj4
        , e.CGC_2 remet_cnpj2
        FROM FATU_050 f -- capa de nota fiscal de saída
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada 
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = f.PEDIDO_VENDA
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
         AND c.CGC_2 = f.CGC_2
        LEFT JOIN SUPR_010 t
          ON t.TIPO_FORNECEDOR = 31 -- transportadora
         AND t.FORNECEDOR9 = f.TRANSPOR_FORNE9
         AND t.FORNECEDOR4 = f.TRANSPOR_FORNE4
         AND t.FORNECEDOR2 = f.TRANSPOR_FORNE2
        LEFT JOIN FATU_500 e -- empresa
          ON e.CODIGO_EMPRESA = f.CODIGO_EMPRESA
        LEFT JOIN BASI_160 cid -- cidades
          ON cid.COD_CIDADE = c.COD_CIDADE
        WHERE 1=1
          AND f.CODIGO_EMPRESA = {empresa} -- empresa 1 Tussor ou 4 Gavi
          AND f.NUM_NOTA_FISCAL = {nf}
          AND f.NUMERO_CAIXA_ECF = 0 -- não é nota especial
          AND f.SITUACAO_NFISC IN (1, 4) -- ativa
          AND f.COD_STATUS = 100 -- foi aceita pela receita
          AND fe.SITUACAO_ENTRADA IS NULL -- devolução não existente
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['empresa'] = "Tussor" if row['codigo_empresa'] == 1 else "Gavi"
        row['nf'] = f"{row['nf_num']}-{row['nf_ser']}"
        row['peso_vol'] = row['peso_tot'] / row['vols']
        row['cli_cnpj_num'] = format_cnpj(row, sep=False, contain='cli')
        row['cli_cnpj'] = format_cnpj(row, contain='cli')
        row['cli_cnpj_nome'] = f"{row['cli_cnpj']} {row['cli_nome']}"
        row['cli_cep'] = f"{row['end_cep']//1000:05d}-{row['end_cep']%1000}"
        row['transp_cnpj_num'] = format_cnpj(row, sep=False, contain='transp')
        row['transp_cnpj'] = format_cnpj(row, contain='transp')
        row['transp_cnpj_nome'] = f"{row['transp_cnpj']} {row['transp_nome']}"
        row['remet_cnpj_num'] = format_cnpj(row, sep=False, contain='remet')
        row['remet_cnpj'] = format_cnpj(row, contain='remet')
    return data
