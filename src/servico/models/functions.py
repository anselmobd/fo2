from pprint import pprint

from django.db import IntegrityError
from django.db.models import Q

from o2.functions import csrf_used

import servico.models


def get_eventos_possiveis(
        logged_user, documento, ult_interacao_equipe__id, ult_interacao_status_id):
    try:
        usuario_funcao = servico.models.UsuarioFuncao.objects.get(
            usuario=logged_user,
            funcao__independente=False,
            equipe=ult_interacao_equipe__id
        )
        nivel_op = usuario_funcao.funcao.nivel_operacional
    except servico.models.UsuarioFuncao.DoesNotExist:
        nivel_op = 0

    acesso = logged_user == documento.user
    if not acesso:
        try:
            usuario_funcao = servico.models.UsuarioFuncao.objects.get(
                usuario=logged_user,
                funcao__independente=True,
            )
            acesso = True
        except servico.models.UsuarioFuncao.DoesNotExist:
            pass

    tipos_eventos = servico.models.Evento.objects.filter(
        statusevento__status_pre=ult_interacao_status_id
    )
    if nivel_op > 0 and acesso:
        tipos_eventos = tipos_eventos.filter(
            Q(nivel_op_minimo__gt=0, nivel_op_minimo__lte=nivel_op)
            |
            Q(nivel_op_minimo=0)
        )
    elif nivel_op > 0:
        tipos_eventos = tipos_eventos.filter(
            nivel_op_minimo__gt=0, nivel_op_minimo__lte=nivel_op
        )
    elif acesso:
        tipos_eventos = tipos_eventos.filter(
            nivel_op_minimo=0
        )
    else:
        # força não encontrar nada
        tipos_eventos = tipos_eventos.filter(
            id=-1
        )
    return tipos_eventos.order_by('ordem')


def salva_interacao(
        msg, request, tipo_documento="os", evento_cod=None,
        doc_id=None, classificacao=None, equipe=None, descricao=None):
    """Salva uma interação de serviço
    Recebe:
        msg: deve ser iniciado com {} e recebe mensagens de erro
        request: importante para controle por csrf
        tipo_documento: Por ora apenas "os", ordem de serviço
        evento_cod: passa None quando for evento de criação ou codigo de um evento
        doc_id: None para criar um novo (evento de criação) ou id de um documento
        classificacao: classificacao ou None
        equipe: equipe ou None
        descrição: descrição ou None
    Retorna:
        o documento que recebeu interação (criado ou não)
    Joga exceção caso não consegua salvar algo
    """
    try:
        try:
            tipo = servico.models.TipoDocumento.objects.get(slug=tipo_documento)
        except servico.models.TipoDocumento.DoesNotExist as e:
            msg.update({
                'erro': 'Tipo de documento inválido.',
            })
            raise e

        if evento_cod is None:
            try:
                evento = servico.models.Evento.objects.get(
                    statusevento__status_pre=None)
            except servico.models.Evento.DoesNotExist as e:
                msg.update({
                    'erro': 'Evento de criação não encontrado.',
                })
                raise e
        else:
            try:
                evento = servico.models.Evento.objects.get(
                    codigo=evento_cod)
            except servico.models.Evento.DoesNotExist as e:
                msg.update({
                    'erro': f'Evento "{evento_cod}" não encontrado.',
                })
                raise e

        if doc_id is None:
            try:
                doc = servico.models.Documento(tipo=tipo)
                doc.save()
            except Exception as e:
                msg.update({
                    'erro': 'Não foi possível gerar um número de documento.',
                })
                raise e
            last_classificacao=None
            last_equipe=None
            last_descricao=None

            status_pos = servico.models.StatusEvento.objects.get(status_pre=None).status_pos

        else:
            try:
                doc = servico.models.Documento.objects.get(id=doc_id)
            except Exception as e:
                msg.update({
                    'erro': f'Não foi possível encontrar o documento "{doc_id}".',
                })
                raise e

            try:
                last_interacao = servico.models.Interacao.objects.filter(
                    documento=doc).order_by('create_at').last()
            except Exception as e:
                msg.update({
                    'erro': f'Não foi possível pegar última interação.',
                })
                raise e
            last_classificacao=last_interacao.classificacao
            last_equipe=last_interacao.equipe
            last_descricao=last_interacao.descricao

            try:
                status_evento = servico.models.StatusEvento.objects.get(
                    status_pre=last_interacao.status,
                    evento=evento)
            except Exception as e:
                msg.update({
                    'erro': f'Não foi possível encontrar StatusEvento "{last_interacao.status}"">--"{evento}".',
                })
                raise e
            status_pos = status_evento.status_pos if status_evento.status_pos else status_evento.status_pre

        try:
            evento = servico.models.Interacao(
                documento=doc,
                evento=evento,
                status=status_pos,
                classificacao=last_classificacao if classificacao is None else classificacao,
                equipe=last_equipe if equipe is None else equipe,
                descricao=last_descricao if descricao is None else descricao,
            )
            evento.save()
        except Exception as e:
            msg.update({
                'erro': 'Não foi possível gerar a Interacao.',
            })
            raise e

        if doc_id is None:
            doc.ativo = True
            doc.save()

    except Exception as e:
        raise e

    else:
        # se não houve exceptions, tem que tentar salvar o csrf
        if csrf_used(request):
            msg.update({
                'erro': 'Formulário já gravado.',
            })
            raise IntegrityError

    return doc
