from pprint import pprint
import yaml

from django.contrib.auth.models import User


class YamlUser(yaml.YAMLObject):
    yaml_tag = u'!username'

    def __init__(self, user):
        self.user = user

    def __str__(self):
        return f"!YAML-{self.id}-{str(self.user)}"

    @classmethod
    def from_yaml(cls, loader, node):
        user_scalar = loader.construct_scalar(node)
        user_list = user_scalar.split('-')
        id = user_list[0]
        user = User.objects.get(id=id)
        return YamlUser(user)

    @classmethod
    def to_yaml(cls, dumper, data):
        scalar = f"{data.user.id}-{data.user.username}"
        node = dumper.represent_scalar(cls.yaml_tag, scalar)
        return node
