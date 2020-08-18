from pprint import pprint

import produto.queries


class CustoItem:
    def __init__(self, cursor, nivel, ref, tam, cor, alt, consumo=1):
        self.data = []
        self.cursor = cursor
        self.nivel = nivel
        self.ref = ref
        self.tam = tam
        self.cor = cor
        self.alt = alt
        self.consumo = consumo

    def componentes_e_custo(
            self, cursor, estrut_nivel, nivel, ref, tam, cor, alt,
            consumo, consumo_pai):
        if estrut_nivel == 0:
            narrativa = produto.queries.item_narrativa(
                cursor, nivel, ref, tam, cor)
            if not narrativa:
                return []
            componentes = [{
                'ESTRUT_NIVEL': 0, 'SEQ': '',
                'NIVEL': nivel, 'REF': ref, 'TAM': tam, 'COR': cor,
                'DESCR': narrativa[0]['NARRATIVA'],
                'ALT': alt, 'CONSUMO': consumo, 'PRECO': '', 'CUSTO': '',
                'TCALC': 0, 'RBANHO': 0, 'TEMALT': 0,
                }]
        else:
            componentes = produto.queries.item_comps_custo(
                cursor, nivel, ref, tam, cor, alt)

        total_custo = 0
        if componentes and self.data:
            self.data[-1]['TEMALT'] = 1
        for comp in componentes:
            self.data.append(comp)
            comp['TEMALT'] = 0
            comp['ESTRUT_NIVEL'] = estrut_nivel
            if comp['NIVEL'] != 9:
                sub_custo = self.componentes_e_custo(
                    cursor, estrut_nivel+1,
                    comp['NIVEL'], comp['REF'],
                    comp['TAM'], comp['COR'], comp['ALT'],
                    comp['CONSUMO'], consumo)
                if sub_custo > 0:
                    comp['PRECO'] = sub_custo
            if comp['TCALC'] == 2:  # g/l
                comp['CONSUMO'] *= comp['RBANHO']
            comp['CUSTO'] = comp['CONSUMO'] * comp['PRECO']
            total_custo += comp['CUSTO']
        return total_custo

    def get_data(self):
        self.componentes_e_custo(
            self.cursor, 0,
            self.nivel, self.ref, self.tam, self.cor, self.alt,
            self.consumo, 1)
        return self.data
