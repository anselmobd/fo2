from pprint import pprint
import yaml

from django.contrib.auth.models import User


class YamlBaseObject(yaml.YAMLObject):

    def __init__(self, object_instance):
        self.object_instance = object_instance

    def __str__(self):
        return f"!YAML-{self.object_instance.id}-{str(self.object_instance)}"

    @classmethod
    def from_yaml(cls, loader, node):
        user_scalar = loader.construct_scalar(node)
        user_list = user_scalar.split('-')
        id = user_list[0]
        object_instance = cls.object_class.objects.get(id=id)
        return YamlUser(object_instance)

    @classmethod
    def to_yaml(cls, dumper, data):
        scalar = f"{data.object_instance.id}-{str(data.object_instance)}"
        node = dumper.represent_scalar(cls.yaml_tag, scalar)
        return node


class YamlUser(YamlBaseObject):
    yaml_tag = u'!username'
    object_class = User
