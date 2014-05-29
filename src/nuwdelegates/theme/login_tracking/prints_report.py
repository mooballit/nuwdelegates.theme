from five import grok
from zope.interface import Interface
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from nuw.types.login_tracking import PrintRecord 
from nuw.types.member import User, Person
from nuwdelegates.theme.interfaces import IThemeSpecific
from z3c.saconfig import named_scoped_session

from nuw.types.admin_area.admin_area import permission, LargeBatch

grok.templatedir('templates')
grok.layer(IThemeSpecific)
SESSION_KEY = 'nuw.types.login_tracking.'
Session = named_scoped_session("nuw.types")

class PrintsOverview(grok.View):
    grok.name('prints-overview')
    grok.context(Interface)
    pagesize = 50

    def update(self):          
        query = self.get_items()
        self.itemcount = int(len(query))

        self.b_start = self.request.SESSION.get(SESSION_KEY + self.b_start_str, 0)
        if self.request.get(self.b_start_str, None) is not None:
            self.b_start = int(self.request.get(self.b_start_str))
            self.request.SESSION.set(SESSION_KEY + self.b_start_str, self.b_start)

        self.items = list()
        for item in query[self.b_start:self.b_start+self.pagesize]:
            self.items.append(item)

    def get_items(self):
        self.b_start_str = 'b_start_users_print'
        users = Session.query(User).all()
        items = []
        for user in users:
            query = Session.query(PrintRecord)\
                .filter(PrintRecord.user_id == user.id)
            num_prints = query.count()
            if num_prints != 0:
                record = query.first()
                items.append({"id" : user.id, "username" : user.name, "num_prints": num_prints, 
                                       "last_print" : record.timestamp.strftime("%d/%m/%Y %H:%M")})  

        return sorted(items, key=lambda k: k['num_prints'], reverse=True)

    @property
    def batch(self):
        quantum = (self.itemcount >= 2000) or False
        p_range = (quantum and self.b_start >= 5*self.pagesize and 5) or 10

        return LargeBatch(
                self.items, self.itemcount, self.pagesize, start=self.b_start,
                quantumleap=quantum, pagerange=p_range,
                b_start_str=self.b_start_str)
        
class UserPrints(grok.View):
    grok.name('user-prints')
    grok.context(Interface)
    pagesize = 50

    def update(self):         
        form = self.request.form
        user_id =  form.get('id', None)
        if user_id:
            query = self.get_items(user_id)
        else:
            query = []
        self.itemcount = int(len(query))

        self.b_start = self.request.SESSION.get(SESSION_KEY + self.b_start_str, 0)
        if self.request.get(self.b_start_str, None) is not None:
            self.b_start = int(self.request.get(self.b_start_str))
            self.request.SESSION.set(SESSION_KEY + self.b_start_str, self.b_start)

        self.items = list()
        for item in query[self.b_start:self.b_start+self.pagesize]:
            self.items.append(item)
            
        self.person = Session.query(Person).filter(Person.user_id == user_id).one()

    def get_items(self, user_id):
        self.b_start_str = 'b_start_prints'
        query = Session.query(PrintRecord)\
            .filter(PrintRecord.user_id == user_id)\
            .order_by(PrintRecord.timestamp.desc())
        prints = query.all()
        items = []
        for record in prints:
            items.append({"id": record.id, "timestamp": record.timestamp.strftime("%d/%m/%Y %H:%M")})
        
        return items

    @property
    def batch(self):
        quantum = (self.itemcount >= 2000) or False
        p_range = (quantum and self.b_start >= 5*self.pagesize and 5) or 10

        return LargeBatch(
                self.items, self.itemcount, self.pagesize, start=self.b_start,
                quantumleap=quantum, pagerange=p_range,
                b_start_str=self.b_start_str)
        
class AjaxPrintView(grok.View):
    grok.name('hidden-print')
    grok.context(Interface)
    
    def update(self):
        portal_state = getMultiAdapter((self.context, self.request), 
                        name="plone_portal_state")
        mt = getToolByName(self.context, "portal_membership")
        if portal_state.anonymous():
            pass
        else:
            user = mt.getAuthenticatedMember()
            query = Session.query(User).filter(User.name == user.getId())
            if query.count() != 0: # if this user exists
                user = query.one()
                record = PrintRecord(user_id = user.id, user_name = user.name)
                Session.add(record)