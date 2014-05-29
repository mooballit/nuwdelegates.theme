from five import grok
from zope.interface import Interface
from nuw.types.authentication import get_user_worksite
from nuwdelegates.theme.interfaces import IThemeSpecific
from user_agents import parse
from pprint import pprint

grok.templatedir( 'templates' )
grok.layer( IThemeSpecific )

class SiteList( grok.View ):
    grok.context( Interface )

    def update( self ):
        self.worksite = get_user_worksite( self.context )

        self.mobile = False
        ua = parse(self.request.environ["HTTP_USER_AGENT"])
        if ua.is_tablet or ua.is_mobile:
            self.mobile = True