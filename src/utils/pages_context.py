from pprint import pprint


def alter_context_processor(request):
    """
    This context processor will add a alter_db to the request.

    Add this to your Django context processors, for example:

    TEMPLATES[0]['OPTIONS']['context_processors'] +=[
        'utils.pages_context.alter_context_processor']
    """
    if hasattr(request, 'alter_db'):
        return {'alter_db': request.alter_db}
    else:
        return {'alter_db': False}
