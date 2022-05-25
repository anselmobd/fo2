from pprint import pprint


class TableDefs(object):
    '''
        formato do self.definition:
        {
            'field': {
                'header': 'Header',
                'style': 'text-align: right;',
                'decimals': 
            },
            ...
        }
    '''

    def __init__(self, definition, keys=None, **kwargs):
        '''
            se keys for uma lista de chaves como ['header', 'style'],
            a definition recebida estará no formato
            {
                'field': ['Header', 'text-align: right;'],
                ...
            }
            e deverá ser convertida para o formato do self.definition

            se uma key na lista de chaves iniciar com '+' como ['header', '+style'],
            valor do key será uma chave para um dicionário com esse nome
            passado no kwargs
        '''
        super(TableDefs, self).__init__()
        self.kwargs = kwargs
        self.cols_list = []

        definition = self.un_multiple_cols(definition)
        if keys is None:
            self.definition = definition
        else:
            self.definition = self.convert(definition, keys)

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
        self.cols_list = cols

    def add(self, pos, *cols):
        if isinstance(pos, int):
            self.cols_list = self.cols_list[:pos] + cols + self.cols_list[pos:]
        else:
            self.cols_list += (pos,) + cols

    def defs(self, *cols):
        if len(cols) == 0:
            if len(self.cols_list) == 0:
                cols = self.definition.keys()
            else:
                cols = self.cols_list
        self.headers = []
        self.fields = []
        self.style = {}
        self.decimals = {}
        for idx, col in enumerate(cols, 1):
            if col in self.definition:
                self.headers.append(
                    self.definition[col].get('header', '') or col.capitalize())
                self.fields.append(col)
                if 'style' in self.definition[col]:
                    self.style[idx] = self.definition[col]['style']
                if 'decimals' in self.definition[col]:
                    self.decimals[idx] = self.definition[col]['decimals']

    def hfs(self, *cols):
        self.defs(*cols)
        return self.headers, self.fields, self.style

    def hfs_dict(self, *cols, sufixo=''):
        self.defs(*cols)
        return {
            f'{sufixo}headers': self.headers,
            f'{sufixo}fields': self.fields,
            f'{sufixo}style': self.style,
        }

    def hfsd(self, *cols):
        self.defs(*cols)
        return self.headers, self.fields, self.style, self.decimals

    def hfsd_dict(self, *cols, sufixo=''):
        self.defs(*cols)
        return {
            f'{sufixo}headers': self.headers,
            f'{sufixo}fields': self.fields,
            f'{sufixo}style': self.style,
            f'{sufixo}decimals': self.decimals,
        }
