from pyramid.view import view_config
import model.news

@view_config(route_name='item.add', renderer='json')
def add(request):
    if not (request.params.has_key('title') and request.params.has_key('content')):
        raise Exception('missing keys')

    title = request.params['title']
    content = request.params['content']

    id = model.news.add(title, content)

    return {'id': str(id)}

@view_config(route_name='item.get', renderer='json')
def get(request):
    id = request.matchdict['item']

    item =  model.news.get(id)

    return {'date': str(item['date']), 'title': item['title'], 'content': item['content'], 'id': str(item['_id'])}
