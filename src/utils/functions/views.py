from pprint import pprint


def cleanned_fields_to_context(self):
    '''
        Assume que há self.context['form'] e cria um
        self.context['field'] para cada field no form
    '''
    for field in self.context['form'].fields:
        self.context[field] = self.context['form'].cleaned_data[field]
