from django.core.management.base import BaseCommand, CommandError

import lotes.views


class Command(BaseCommand):
    help = 'Calculating all meta de giro.'

    def handle(self, *args, **options):
        try:
            cont = lotes.views.calculaMetaGiroTodas()
            self.stdout.write('Qtd. metas: {}'.format(cont), ending='\n')

        except Exception as e:
            raise CommandError('Error calculating all meta de giro'.format(e))
