#!/usr/bin/env python

from PIL import Image, ImageDraw
import base64
import io

# im = Image.new('RGBA', (200, 100),  color='black')
im = Image.open(
    '/home/anselmo/Documentos/AssinaturaMailDUOMO/duomo.jpg', mode='r')

buffer = io.BytesIO()
# im.save(buffer, format='PNG')
im.save(buffer, format='JPEG')
buffer.seek(0)

data_uri = base64.b64encode(buffer.read()).decode('ascii')

html = '<html><head></head><body>'
# html += '<img src="data:image/png;base64,{0}">'.format(data_uri)
html += '<img src="data:image/jpeg;base64,{0}">'.format(data_uri)
html += '</body></html>'

print(html)
