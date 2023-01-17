from pprint import pprint

__all__ = ['TableDefs', 'TableDefsHpS']



class TableDefs(object):
    '''Classe para auxiliar a montagem do dicionário com definições necessarias
    para gerar, nos templates, um "HTML table" que apresenta o conteúdo de um
    "dictlist" de dados.

    O dicionário gerado terá as seguintes chaves:
        headers
        fields
        style
        decimals (opcional)

    Para isso trabalha em uma estrutura que deve estar no parâmetro
    self.definition desta classe.

    self.definition é um dicionário cujas chaves são os nomes dos campos de um
    "dictlist" de dados, e cujos valores são dicionários com pares chave/valor
    das configurações de apresentação do campo.

    As possíveis chave das configurações do campo são:
        - header
        - style
        - decimals

    Por exemplo:
    {
        'field': {
            'header': 'Header',
            'style': 'text-align: right;',
            'decimals': 2,
        },
    }
    '''

    def __init__(self, definition, keys=None, **kwargs):
        ''' Inicializa classe
        Recebe:
            definition:
                - um dicionário já no formato do self.definition; ou
                - um formato intermediário, que a inicialização irá converter
                  no formato do self.definition

                Formato intermediário:
                    - um dicionário cujas chaves são os nomes dos campos e
                    cujos valores são:
                        - uma lista; ou
                        - um valor, que será convertido em uma lista com esse
                          valor

                Caso seja utilizado o formato intermediário, será necessário
                receber neste método também o parâmetro "keys"
                
                 com as chaves das configurações referentes à cada
                posição na lista.

            keys
                lista com as chaves das configurações de campo.

                Cada valor na lista do formato intermediário será atribuido
                à chave no na mesma posição da lista "keys"

        Exemplo:
            Se keys for uma lista de chaves como ['header', 'style'],
            definition deverá estar no formato intermediário, como abaixo:
            {'field': ['Header', 'text-align: right;'], ...}

            Isso gerará a seguinte saida da classe:
            {
                'headers': ['Header'],
                'fields': ['field'],
                'style': {
                    1: 'text-align: right;';
                },
            }

        Caso especial de keys:
            Quando um valor da lista de chaves iniciar com '+', em kwargs deve
            haver um dicionário com o nome dessa chave.

            O valor da chave na lista do definition será uma chave desse
            dicionário e deve ser traduzida para o valor ali encontrado.
        '''
        super(TableDefs, self).__init__()
        self.kwargs = kwargs
        self.default_kwargs()

        self.cols_list = []

        definition = self.un_multiple_cols(definition)
        if keys is None:
            self.definition = definition
        else:
            self.definition = self.convert(definition, keys)

    def default_kwargs(self):
        if 'style' in self.kwargs:
            style = {}
            for key in self.kwargs['style']:
                if key == '_':
                    if self.kwargs['style'][key] == 'text-align':
                        style.update({
                            'l': 'text-align: left;',
                            'c': 'text-align: center;',
                            'r': 'text-align: right;',
                        })
                else:
                    style[key] = self.kwargs['style'][key]
            self.kwargs['style'] = style

    def un_multiple_cols(self, definition):
        new_def = {}
        for key in definition:
            for sub_key in key.split():
                new_def[sub_key] = definition[key]
        return new_def

    def convert(self, definition, keys):
        result = {}
        for col in definition:
            def_col = {}
            for i, key in enumerate(keys):
                if i < len(definition[col]):
                    if key.startswith('+'):
                        key = key[1:]
                        def_col[key] = self.kwargs[key][definition[col][i]]
                    else:
                        def_col[key] = definition[col][i]
            result[col] = def_col
        return result

    def cols(self, *cols):
        if cols:
            self.cols_list = cols
        else:
            self.cols_list = self.definition.keys()

    def add(self, pos, *cols):
        if isinstance(pos, int):
            self.cols_list = self.cols_list[:pos] + cols + self.cols_list[pos:]
        else:
            self.cols_list += (pos,) + cols

    def dele(self, key):
        if not self.cols_list:
            self.cols()
        self.cols_list = tuple(
            col
            for col in self.cols_list
            if col != key
        )

    def bitmap_match(self, col, bitmap):
        col_bitmap = self.definition[col].get('flags_bitmap', 0)
        if isinstance(col_bitmap, int) and col_bitmap:
            return (bitmap & col_bitmap)
        return True

    def defs(self, *cols, bitmap=None):
        if len(cols) == 0:
            if len(self.cols_list) == 0:
                cols = self.definition.keys()
            else:
                cols = self.cols_list

        if isinstance(bitmap, int):
            cols = [
                col
                for col in cols
                if self.bitmap_match(col, bitmap)
            ]

        self.headers = []
        self.fields = []
        self.style = {}
        self.decimals = {}
        for idx, col in enumerate(cols, 1):
            if col not in self.definition:
                continue
            self.headers.append(
                self.definition[col].get('header', '') or col.capitalize())
            self.fields.append(col)
            if 'style' in self.definition[col]:
                self.style[idx] = self.definition[col]['style']
            if 'decimals' in self.definition[col]:
                self.decimals[idx] = self.definition[col]['decimals']

    def hfs(self, *cols, bitmap=None, decimals=False):
        self.defs(*cols, bitmap=bitmap)
        result = [self.headers, self.fields, self.style]
        if decimals:
            result.append(self.decimals)
        return tuple(result)

    def hfs_dict(self, *cols, bitmap=None, context=None, sufixo='', decimals=False):
        self.defs(*cols, bitmap=bitmap)
        config = {
            f'{sufixo}headers': self.headers,
            f'{sufixo}fields': self.fields,
            f'{sufixo}style': self.style,
        }
        if decimals:
            config[f'{sufixo}decimals'] = self.decimals
        if context:
            context.update(config)
        else:
            return config

    def hfsd(self, *cols, bitmap=None):
        return self.hfs(*cols, bitmap=bitmap, decimals=True)

    def hfsd_dict(self, *cols, bitmap=None, context=None, sufixo=''):
        return self.hfs_dict(*cols, bitmap=bitmap, context=context, sufixo=sufixo, decimals=True)


class TableDefsH(TableDefs):

    def __init__(self, definition):
        super(TableDefsH, self).__init__(
            definition,
            ['header'],
        )


class TableDefsHpS(TableDefs):

    def __init__(self, definition):
        super(TableDefsHpS, self).__init__(
            definition,
            ['header', '+style'],
            style = {'_': 'text-align'},
        )


class TableDefsHpSD(TableDefs):

    def __init__(self, definition):
        super(TableDefsHpSD, self).__init__(
            definition,
            ['header', '+style', 'decimals'],
            style = {'_': 'text-align'},
        )
