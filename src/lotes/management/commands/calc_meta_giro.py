from django.core.management.base import BaseCommand, CommandError

from fo2.connections import db_cursor_so

import lotes.views


class Command(BaseCommand):
    help = 'Calculating all meta de giro.'

    def handle(self, *args, **options):
        try:
            cursor = db_cursor_so()
            cont = lotes.views.calculaMetaGiroTodas(cursor)
            self.stdout.write('Qtd. metas: {}'.format(cont), ending='\n')

        except Exception as e:
            raise CommandError('Error calculating all meta de giro'.format(e))
