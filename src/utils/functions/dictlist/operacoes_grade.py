import copy
from pprint import pprint

import systextil.models


class OperacoesGrade():

    def __init__(self) -> None:
        self._s_tamanhos = None

    def get_celula(self, grd, tam, cor):
        result = 0
        sortimento_field = grd['fields'][0]
        for linha in grd['data'][:-1]:
            if linha[sortimento_field] == cor:
                if tam in linha:
                    result = linha[tam]
                else:
                    result = 0
                break
        return result


    def soma_grades(self, g1, g2):
        return self.opera_grades(g1, g2, '+')


    def subtrai_grades(self, g1, g2):
        return self.opera_grades(g1, g2, '-')


    def zera_grade(self, g1):
        return self.opera_grades(g1, g1, '-')


    def inverte_sinal_grade(self, g1):
        return self.opera_grade(g1, lambda x: -x)


    def opera_grades(self, g1, g2, operacao):
        tamanhos1 = set(g1['headers'][1:-1])
        tamanhos2 = set(g2['headers'][1:-1])
        tamanhos = list(tamanhos1.union(tamanhos2))
        s_tamanhos = systextil.models.Tamanho.objects.all().values()
        tamanhos = sorted(
            tamanhos,
            key=lambda tam: [
                s_tam['ordem_tamanho']
                for s_tam in s_tamanhos
                if s_tam['tamanho_ref'] == tam
            ])

        sortimento_field1 = g1['fields'][0]
        sortimento_field2 = g2['fields'][0]
        cores1 = set([
            linha[sortimento_field1]
            for linha in g1['data'][:-1]
        ])
        cores2 = set([
            linha[sortimento_field2]
            for linha in g2['data'][:-1]
        ])
        cores = list(cores1.union(cores2))
        cores = sorted(cores)

        grade = {}
        grade['fields'] = [sortimento_field1, *tamanhos, 'total']
        grade['headers'] = ['Cor/Tamanho', *tamanhos, 'Total']
        grade['style'] = {
            i+2: 'text-align: right;'
            for i, _ in enumerate(tamanhos)
        }
        grade['style'][len(tamanhos)+2] = 'text-align: right; font-weight: bold;'
        grade['data'] = []
        linha_zerada = {
            tam: 0
            for tam in tamanhos
        }
        linha_zerada.update({
            'total': 0,
        })
        totais = linha_zerada.copy()

        for cor in cores:
            linha = linha_zerada.copy()
            linha[sortimento_field1] = cor
            total_linha = 0
            for tam in tamanhos:
                valor1 = self.get_celula(g1, tam, cor)
                valor2 = self.get_celula(g2, tam, cor)
                if operacao == '+':
                    valor = valor1 + valor2
                else:
                    valor = valor1 - valor2
                linha[tam] = valor
                totais[tam] += valor
                total_linha += valor
            linha['total'] = total_linha
            totais['total'] += total_linha
            grade['data'].append(linha)

        totais[sortimento_field1] = 'Total'
        totais['|STYLE'] = 'font-weight: bold;'
        grade['data'].append(totais)
        grade['total'] = totais['total']
        return grade


    def grade_filtra_linhas_zeradas(self, grd):
        grade = copy.deepcopy(grd)
        for linha in grade['data'][:-1]:
            if linha['Total'] == 0:
                grade['data'].remove(linha)
        return grade


    def opera_grade(self, grd, func):
        grade = copy.deepcopy(grd)
        lin_tot = grade['data'][-1]
        col_tot = grade['fields'][-1]
        for linha in grade['data'][:-1]:
            for col in grade['fields'][1:-1]:
                ori = linha[col]
                linha[col] = func(linha[col])
                lin_tot[col] += (linha[col] - ori)
                linha[col_tot] += (linha[col] - ori)
                lin_tot[col_tot] += (linha[col] - ori)
        grade['total'] = lin_tot[col_tot]
        return grade


    def update_gzerada(self, gzerada, gme):
        gzerada_aux = self.zera_grade(gme)
        if gzerada is None:
            return gzerada_aux
        else:
            return self.soma_grades(gzerada, gzerada_aux)

def get_celula(grd, tam, cor):
    result = 0
    sortimento_field = grd['fields'][0]
    for linha in grd['data'][:-1]:
        if linha[sortimento_field] == cor:
            if tam in linha:
                result = linha[tam]
            else:
                result = 0
            break
    return result


def soma_grades(g1, g2):
    return opera_grades(g1, g2, '+')


def subtrai_grades(g1, g2):
    return opera_grades(g1, g2, '-')


def zera_grade(g1):
    return opera_grades(g1, g1, '-')


def inverte_sinal_grade(g1):
    return opera_grade(g1, lambda x: -x)


def opera_grades(g1, g2, operacao):
    tamanhos1 = set(g1['headers'][1:-1])
    tamanhos2 = set(g2['headers'][1:-1])
    tamanhos = list(tamanhos1.union(tamanhos2))
    s_tamanhos = systextil.models.Tamanho.objects.all().values()
    tamanhos = sorted(
        tamanhos,
        key=lambda tam: [
            s_tam['ordem_tamanho']
            for s_tam in s_tamanhos
            if s_tam['tamanho_ref'] == tam
        ])

    sortimento_field1 = g1['fields'][0]
    sortimento_field2 = g2['fields'][0]
    cores1 = set([
        linha[sortimento_field1]
        for linha in g1['data'][:-1]
    ])
    cores2 = set([
        linha[sortimento_field2]
        for linha in g2['data'][:-1]
    ])
    cores = list(cores1.union(cores2))
    cores = sorted(cores)

    grade = {}
    grade['fields'] = [sortimento_field1, *tamanhos, 'total']
    grade['headers'] = ['Cor/Tamanho', *tamanhos, 'Total']
    grade['style'] = {
        i+2: 'text-align: right;'
        for i, _ in enumerate(tamanhos)
    }
    grade['style'][len(tamanhos)+2] = 'text-align: right; font-weight: bold;'
    grade['data'] = []
    linha_zerada = {
        tam: 0
        for tam in tamanhos
    }
    linha_zerada.update({
        'total': 0,
    })
    totais = linha_zerada.copy()

    for cor in cores:
        linha = linha_zerada.copy()
        linha[sortimento_field1] = cor
        total_linha = 0
        for tam in tamanhos:
            valor1 = get_celula(g1, tam, cor)
            valor2 = get_celula(g2, tam, cor)
            if operacao == '+':
                valor = valor1 + valor2
            else:
                valor = valor1 - valor2
            linha[tam] = valor
            totais[tam] += valor
            total_linha += valor
        linha['total'] = total_linha
        totais['total'] += total_linha
        grade['data'].append(linha)

    totais[sortimento_field1] = 'Total'
    totais['|STYLE'] = 'font-weight: bold;'
    grade['data'].append(totais)
    grade['total'] = totais['total']
    return grade


def grade_filtra_linhas_zeradas(grd):
    grade = copy.deepcopy(grd)
    for linha in grade['data'][:-1]:
        if linha['Total'] == 0:
            grade['data'].remove(linha)
    return grade


def opera_grade(grd, func):
    grade = copy.deepcopy(grd)
    lin_tot = grade['data'][-1]
    col_tot = grade['fields'][-1]
    for linha in grade['data'][:-1]:
        for col in grade['fields'][1:-1]:
            ori = linha[col]
            linha[col] = func(linha[col])
            lin_tot[col] += (linha[col] - ori)
            linha[col_tot] += (linha[col] - ori)
            lin_tot[col_tot] += (linha[col] - ori)
    grade['total'] = lin_tot[col_tot]
    return grade


def update_gzerada(gzerada, gme):
    gzerada_aux = zera_grade(gme)
    if gzerada is None:
        return gzerada_aux
    else:
        return soma_grades(gzerada, gzerada_aux)
