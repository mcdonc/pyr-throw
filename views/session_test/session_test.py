from pyramid.view import view_config

@view_config(route_name='session_test', renderer='json')
def session_test(request):
    request.session['number'] = request.session.get('number',0) + 1

    return {'id': request.session['number']}

