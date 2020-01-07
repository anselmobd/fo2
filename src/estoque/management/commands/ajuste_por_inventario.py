from pprint import pprint, pformat
import datetime

from django.core.management.base import BaseCommand, CommandError

from estoque.views import ajuste_por_inventario


class Command(BaseCommand):
    help = 'Ajuste por inventário no Systêxtil'

    def my_println(self, text=''):
        self.my_print(text, ending='\n')

    def my_print(self, text='', ending=''):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()

    def add_arguments(self, parser):
        parser.add_argument('dep', help='101, 102 ou 231')
        parser.add_argument('ref', help='5 caracteres')
        parser.add_argument('cor', help='6 caracteres')
        parser.add_argument('tam', help='1 a 3 caracteres')
        parser.add_argument('qtd', type=int, help='quantidade inventariada')
        parser.add_argument('data', help='data do inventário (AAAA-MM-DD)')
        parser.add_argument('hora', help='hora do inventário (HHhMM)')

    def handle(self, *args, **options):
        self.my_println('---')
        self.my_println('{}'.format(datetime.datetime.now()))

        dep = options['dep']
        ref = options['ref']
        cor = options['cor']
        tam = options['tam']
        qtd = options['qtd']
        data = options['data']
        hora = options['hora']

        self.my_println(
            '{} {} {} {} {} {} {}'.format(dep, ref, cor, tam, qtd, data, hora))

        try:
            sucesso, mensagem, infos = ajuste_por_inventario(
                dep,
                ref,
                tam,
                cor,
                qtd,
                data,
                hora,
            )
        except Exception as e:
            sucesso = False
            mensagem = '{}'.format(e)
            infos = []

        if not sucesso:
            info_string = ''
            if len(infos) != 0:
                info_string = '\n{}'.format(pformat(infos))
            raise CommandError(
                'Erro inserindo transação de inventário no '
                'Systêxtil [{}]{}'.format(mensagem, info_string))
        self.my_println(
            'Sucesso inserindo transação de inventário no '
            'Systêxtil [{}]'.format(mensagem))

        self.my_println(pformat(infos))

        self.my_println(format(datetime.datetime.now(), '%H:%M:%S.%f'))
