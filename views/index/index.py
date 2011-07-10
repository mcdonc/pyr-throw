from pyramid.view import view_config

@view_config(route_name='index', renderer='index/index.mako')
def index(request):
    return {'hi': 'hi'}

@view_config(route_name='favicon', renderer='string')
def favicon(request):
    return ''