"""
Things to work on:

1. Sessions
2. Authentication
3. Authorisation
4. Configuration
5. Views and templates in same space
6. SQL schema updates and command-line actions
7. Re-integrate mongodb, redis

"""

import os
import logging
import pymongo
import lib.db as db
import lib.session as session
import sys

from pyramid.config import Configurator

from paste.httpserver import serve

logging.basicConfig()
log = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))


def main():
    # configuration settings
    settings = dict()
    settings['reload_all'] = True
    # settings['debug_all'] = True
    settings['debug_authorization'] = False
    settings['debug_notfound'] = True

    settings['mako.directories'] = os.path.join(here, 'views')

#    settings['mongo_connection'] = pymongo.Connection('mongodb://localhost/')
    settings['mongo_db_name'] = 'news33'

    settings['session.name'] = 'session'
    settings['session.domain'] = 'localhost'
    settings['session.path'] = '/'
    settings['session.timeout'] = 10*60
    settings['session.secure_only'] = False
    settings['session.mongodb_url'] = 'mongodb://localhost/'
    settings['session.mongodb_db'] = 'session'

    settings['sqlalchemy.url'] = 'postgres://richard:test@localhost/test1'

#    db.init(settings)
#    session.init(settings)

    config = Configurator(settings=settings)

#    config.add_subscriber('pyrapp.lib.session.on_request', 'pyramid.events.NewRequest')
#    config.add_subscriber('pyrapp.lib.session.on_response', 'pyramid.events.NewResponse')

    config.include('pyramid_tm')
    # configuration setup
    config.add_route('session_test','/session_test')
    config.add_route('index','/')
    config.add_route('item.add','/news/add')
    config.add_route('item.get','/news/{item}')

    config.add_route('favicon','/favicon.ico')

    config.add_static_view('image', os.path.join(here, 'image'))
    config.add_static_view('css', os.path.join(here, 'css'))
    config.add_static_view('js', os.path.join(here, 'js'))

    config.scan(package='pyrapp.views')

    # serve app
    app = config.make_wsgi_app()
    serve(app, host='127.0.0.1')
    
if __name__ == '__main__':
    main(sys.argv)

