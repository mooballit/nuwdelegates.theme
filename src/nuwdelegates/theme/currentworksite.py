from AccessControl import getSecurityManager
from five import grok
from nuw.types.authentication import get_user_worksite
from nuw.types.member import User, Person
from nuw.types.group import Group, GroupType, get_groups_by_type
from plone.app.layout.viewlets.interfaces import IPortalHeader
from Products.CMFCore.utils import getToolByName
from z3c.saconfig import named_scoped_session
from zope import schema
from zope.interface import Interface
import json
from user_agents import parse
from pprint import pprint
import logging

logger = logging.getLogger(__name__)

grok.templatedir( 'browser' )

Session = named_scoped_session('nuw.types')

class CurrentWorksite( grok.Viewlet ):
    grok.viewletmanager( IPortalHeader )
    grok.context( Interface )

    def update( self ):
        self.worksite = get_user_worksite( self.context )

    def has_access( self ):
        return getSecurityManager().checkPermission( 'nuw.types: Access all worksites', self.context )

    def isMobile(self):
        """ Conditionally render only for non-mobile devices """
        ua = parse(self.request.environ["HTTP_USER_AGENT"])
        if ua.is_tablet or ua.is_mobile:
            return True
        else:
            return False

class MobileHeader( grok.Viewlet ):
    grok.viewletmanager( IPortalHeader )
    grok.context( Interface )

    def update( self ):
        self.worksite = get_user_worksite( self.context )

    def has_access( self ):
        return getSecurityManager().checkPermission( 'nuw.types: Access all worksites', self.context )

    def isMobile(self):
        """ Conditionally render only for mobile devices """
        ua = parse(self.request.environ["HTTP_USER_AGENT"])
        if ua.is_tablet or ua.is_mobile:
            return True
        else:
            return False

class SearchWorksites( grok.View ):
    grok.context( Interface )
    grok.name( 'searchworksites.json' )

    def render( self ):
        self.request.response.setHeader( 'Content-type', 'application/json' )

        ret = []

        if 'term' in self.request.form:
            for grp in get_groups_by_type( 'Union Site', self.request.form['term'] )[:20]:
                ret.append( { 'label': grp.long_name, 'value': grp.groupid } )

        return json.dumps( ret )

class CrossSiteAuthViewlet(grok.Viewlet):
    grok.viewletmanager(IPortalHeader)
    grok.context(Interface)

    def update(self):
        sess = Session()
        current_user = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()

        logout = False
        if current_user.getUserName() != 'Anonymous User' and current_user.getUserName() != 'alenm':
            person = sess.query(Person).filter(
                User.name == current_user.getUserName(), Person.user_id == User.id,
                ).first()

            if not person:
                self.request.response.expireCookie('__ac')
                self.request.response.redirect('/logout')

            if person is not None and 'webrep' not in person.webstatuses:
                self.request.response.expireCookie('__ac')
                self.request.response.redirect('/logout')
