from pprint import pprint

import comercial.models

from cd.queries.novo_modulo import refs_de_modelo

__all__ = ['get_refs', 'get_filtra_ref']


def get_refs(
    cursor,
    ref=None,
    modelo=None,
    com_op=None,
    com_ped=None,
    com_pac=False,
):
    refs_modelo = set()
    if modelo:
        refs_modelo = refs_de_modelo.to_set(
            cursor,
            modelo,
            com_op=com_op,
            com_ped=com_ped,
        )

        if com_pac:
            refs_pac_data = comercial.models.MetaModeloReferencia.objects.filter(
                modelo=modelo,
                incl_excl='i',
            ).values('referencia')
            if refs_pac_data:
                refs_pac = set(
                    row['referencia']
                    for row in refs_pac_data
                )
                refs_modelo = refs_modelo & refs_pac

    refs_ref = set()
    if ref:
        if isinstance(ref, (tuple, list)):
            refs_ref = set(ref)
        else:
            refs_ref = {ref, }

    if modelo and ref:
        refs = refs_ref & refs_modelo
    else:
        refs = refs_ref | refs_modelo
    return list(refs)


def get_filtra_ref(
    cursor,
    field,
    ref=None,
    modelo=None,
    com_op=None,
    com_ped=None,
    com_pac=None,
):
    refs_list = get_refs(
        cursor,
        ref=ref,
        modelo=modelo,
        com_op=com_op,
        com_ped=com_ped,
        com_pac=com_pac,
    )

    if refs_list:
        ref_virgulas = ', '.join([f"'{r}'" for r in refs_list])
        filtra_ref = f"""--
            AND {field} in ({ref_virgulas})
        """
    else:
        filtra_ref = 'AND 1=2' if modelo or ref else ''
    return filtra_ref
