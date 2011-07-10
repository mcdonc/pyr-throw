"""

Session management

This session implementation utilises a MongoDB backend to provide the following:

1. Authenticity
    All session data is stored server-side, clients receive a 256bit randomly generated token using the URL-safe
    Base64 encoding alphabet as their session ID.

2. Revocation
    Sessions can be revoked (expired) on an individual basis via .expire(), or as a group via .expire_set() in
    order to kill all sessions relating to a particular user.

3. Upgrades
    When a session crosses a permissions boundary (Login, Administration, HTTPS), the .rotate() method can be called to
    expire the old session ID and move the data into a new one.

4. Idle detection
    When a session has been idle for session.timeout seconds it is expired automatically.

Configuration

session.domain      Domain name to limit session to
session.path        Path to limit session to
session.timeout     Session idle timeout (Recommend no more than 20 minutes, probably 10)
session.secure_only True if you want HTTPS only
session.mongodb_url MongoDB url
session.mongodb_db  MongoDB database

"""
from datetime import datetime
import logging
import pymongo
from lib.token import create_token, valid_token

config = {}
mongodb = None

log = logging.getLogger(__file__)

class Session(dict):
    id = None # Session ID
    modified = None # Has the session data been modified?
    new = None # Is the session new?
    expired = None # Is the session expired?
    _store = None

    def __init__(self, request):
        dict.__init__(self)

        self.request = request
        self.modified = False
        self.expired = False

        self._store = mongodb[config['mongodb_db']].session
        
        self.id = request.str_cookies.get(config['name'], None)

        # Did we find a session ID in the cookie?
        if not self.id:
            log.debug("No session token found in cookie")
            self.reset()
            return

        # Is the token valid?
        if not valid_token(self.id):
            log.warn("Invalid session token found in cookie")
            self.reset()
            return

        doc = self._store.find_one({'session_id': self.id})

        # Did we find the session ID in the store?
        if not doc:
            log.debug("No session matches provided token in store")
            self.reset()
            return

        # Has this session been forcibly expired?
        self.last_update = doc['last_update']
        if doc['expired']:
            log.warn("Attempt to use expired session")
            self.reset()
            return

        # Is this session idle too long?
        age = datetime.now() - self.last_update
        age_seconds = age.days * (24*60*60) + age.seconds
        if age_seconds > config['timeout']:
            log.debug("Session idle too long")
            self.expire()
            self.reset()
            return

        # Map the data into the dictionary
        for k in doc['data'].keys():
            self[k] = doc[k]

        self.modified = False

    def reset(self):
        """
        Reset the session. Creates a new token, wipes any existing data.

        This does NOT expire the previous session ID (if there was one). To do this, call expire() first.
        """
        self.id = create_token()
        log.debug("Generating new session %s" % self.id)
        
        self.modified = True
        self.last_update = datetime.now()
        self.clear()

    def __setitem__(self, k, value):
        self.modified = True
        return dict.__setitem__(self, k, value)

    def __delitem__(self, k):
        self.modified = True
        return dict.__delitem__(self, k)

    def expire(self):
        """
        Expires the session. The data is retained within the session object however no new requests will
        be able to retrieve it.
        """
        log.debug("Expiring session %s" % self.id)
        self._store.update({'session_id': self.id}, {'$set': {'expired': True}})
        self.expired = True

    def expire_set(self, match):
        """
        Expires a set of matching settings. For example,

        session.expire_set({'data.user_id': 55})
        """
        self._store.update(match, {'$set': {'expired': True}})
        self.expired = True

    def rotate(self):
        """
        Rotate the session. Expires the existing session ID then creates a new one, while retaining the existing
        data.

        New session is not saved until the end of the request.
        """
        log.debug("Rotating session %s out" % self.id)

        # Expire current session
        self.expire()

        # Create new session ID
        self.session_id = create_token()
        self.modified = True
        self.expired = False

    def save(self):
        """
        Save the current session information to store. Done automatically when the request completes.
        """
        if self.expired:
            log.debug("Not saving session %s - expired" % self.id)
            return
        
        log.debug("Saving session %s to store" % self.id)
        self.last_update = datetime.now()
        self._store.save({
            'last_update': self.last_update,
            'session_id': self.id,
            'data': dict(self)
            })

def on_request(event):
    """
    Decorate request with session
    @param event:
    @return:
    """
    event.request.session = Session(event.request)

def on_response(event):
    """

    @param event:
    @return:
    """
    event.request.session.save()

    event.response.set_cookie(config['name'],
                              value=event.request.session.id,
                              path=config['path'],
                              domain=config['domain'],
                              secure=config['secure_only'],
                              httponly=True,
                              overwrite=True)

def init(settings):
    """
    Initialise session subsystem

    @param settings:dict Session configuration settings (see module docs)
    @return:
    """
    global mongodb

    config['domain'] = settings.get('session.domain', None)
    config['path'] = settings.get('session.path')
    config['name'] = settings.get('session.name')
    config['timeout'] = settings.get('session.timeout')
    config['secure_only'] = settings.get('session.secure_only')

    mongodb = pymongo.Connection(settings.get('session.mongodb_url'))
    config['mongodb_db'] = settings.get('session.mongodb_db')
