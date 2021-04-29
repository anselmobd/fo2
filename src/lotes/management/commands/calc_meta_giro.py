from django.core.management.base import BaseCommand, CommandError

from fo2.connections import db_cursor_so

from lotes.models.functions.meta import calculaMetaGiroTodas


class Command(BaseCommand):
    help = 'Calculating all meta de giro.'

    def handle(self, *args, **options):
        try:
            cursor = db_cursor_so()
            cont = calculaMetaGiroTodas(cursor)
            self.stdout.write('Qtd. metas: {}'.format(cont), ending='\n')

        except Exception as e:
            raise CommandError('Error calculating all meta de giro'.format(e))
