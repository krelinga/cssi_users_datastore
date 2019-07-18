import os

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def root_parent():
    '''A single key to be used as the ancestor for all dog entries.

    Allows for strong consistency at the cost of scalability.'''
    return ndb.Key('Parent', 'default_parent')

class Thing(ndb.Model):
    user = ndb.UserProperty()
    text = ndb.StringProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = JINJA_ENVIRONMENT.get_template('templates/main.html')
        template_date = {
            'login_url': users.create_login_url('/'),
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'stuff': Thing.query(Thing.user == user, ancestor=root_parent()).fetch()
        }
        self.response.write(template.render(template_date))

    def post(self):
        user = users.get_current_user()
        if not user:
            self.response.status_int = 401
            return
        thing = Thing(parent=root_parent())
        thing.text = self.request.get('thing_text')
        thing.user = user
        thing.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
