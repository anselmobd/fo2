import sys
import android
import os
import json
import urllib.request


print('\n'*10)
print('='*30)
print(' Tussor')
print(' Coletor de códigos de barras')
print('='*30)

droid = android.Android()

print('\nCelular: "{}"'.format(os.environ['QPY_USERNO']))

choice = ' '
while choice == ' ':
    print('')
    print('='*30)
    print(' "Enter" para bipar um código')
    print(' Para sair: qq tecla + "Enter"')
    print('='*30)
    c = input('')
    if c != '':
        sys.exit()

    code = droid.scanBarcode()

    if code.result is None:
        print('Nenhum código bipado!')
    else:
        barcode = code.result['extras']['SCAN_RESULT']
        print('Código de barras: "{}"\n'.format(barcode))

        data = {}
        url = 'http://intranet.tussor.com.br:88/insumo/rolo/{}/{}/'.format(
            barcode, os.environ['QPY_USERNO'])
        webURL = urllib.request.urlopen(url)

        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        rolo = json.loads(data.decode(encoding))
        if rolo == {}:
            print('Rolo não encontrado!')
        else:
            print('      Rolo: {:09}'.format(rolo['ROLO']))
            print('Referência: {}'.format(rolo['REF']))
            print('       Cor: {}'.format(rolo['COR']))
            print('   Tamanho: {}'.format(rolo['TAM']))
