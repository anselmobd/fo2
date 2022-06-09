from collections import namedtuple


class Relations():

    def __init__(self) -> None:
        self.F = namedtuple('F', 'field')
        self.FF = namedtuple('FF', 'format fields')

        # para class Select
        self.AliasField = namedtuple('AliasField', 'alias field')
        self.MakeField = namedtuple('MakeField', 'table field alias')
        self.ValueAlias = namedtuple('ValueAlias', 'value alias')
        self.TableAlias = namedtuple('TableAlias', 'table alias')
        self.JoinRules = namedtuple('JoinRules', 'from_alias rules')
        self.JoinAlias = namedtuple('JoinAlias', 'table alias conditions')
        self.Condition = namedtuple('Condition', 'left test right')
        self.TestValue = namedtuple('TestValue', 'test value')
        self.TemplateFields = namedtuple('TemplateFields', 'template fields')
        self.Template = namedtuple('Template', 'template')
