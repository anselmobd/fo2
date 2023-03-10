# importado aqui apenas para executar os registers de template
import utils.template


# importado aqui apenas para executar os path converters
import utils.converters


from django.urls import register_converter
register_converter(utils.converters.DateConverter, 'date')


from django.contrib import admin

# Register your models here.
