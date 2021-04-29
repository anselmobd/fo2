import servico.models


def get_num_doc(tipo):
    tipo_obj = servico.models.TipoDocumento.objects.get(slug=tipo)
    num_doc = servico.models.Documento(tipo=tipo_obj)
    num_doc.save()
    return num_doc.id
