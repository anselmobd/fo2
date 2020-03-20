from pprint import pprint


def cleanned_fields_to_context(self):
    for field in self.context['form'].fields:
        self.context[field] = self.context['form'].cleaned_data[field]
