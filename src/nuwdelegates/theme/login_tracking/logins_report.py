from five import grok
from zope.interface import Interface
from nuw.types.login_tracking import LoginRecord 
from nuw.types.member import User, Person
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from nuwdelegates.theme.interfaces import IThemeSpecific
from z3c.saconfig import named_scoped_session
from nuw.types.admin_area.admin_area import permission, LargeBatch

grok.templatedir('templates')
grok.layer(IThemeSpecific)
SESSION_KEY = 'nuw.types.login_tracking.'
Session = named_scoped_session("nuw.types")

class LoginsOverview(grok.View):
    grok.name('logins-overview')
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
        self.b_start_str = 'b_start_users'
        users = Session.query(User).all()
        items = []
        for user in users:
            query = Session.query(LoginRecord)\
                .filter(LoginRecord.user_id == user.id)
            num_logins = query.count()
            if num_logins != 0:
                record = query.first()
                items.append({"id" : user.id, "username" : user.name, "num_logins": num_logins, 
                                       "last_login" : record.timestamp.strftime("%d/%m/%Y %H:%M")})  

        return sorted(items, key=lambda k: k['num_logins'], reverse=True)

    @property
    def batch(self):
        quantum = (self.itemcount >= 2000) or False
        p_range = (quantum and self.b_start >= 5*self.pagesize and 5) or 10

        return LargeBatch(
                self.items, self.itemcount, self.pagesize, start=self.b_start,
                quantumleap=quantum, pagerange=p_range,
                b_start_str=self.b_start_str)
        
class UserLogins(grok.View):
    grok.name('user-logins')
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
        self.b_start_str = 'b_start_logins'
        query = Session.query(LoginRecord)\
            .filter(LoginRecord.user_id == user_id)\
            .order_by(LoginRecord.timestamp.desc())
        logins = query.all()
        items = []
        for record in logins:
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
        
    
@grok.subscribe(IUserLoggedInEvent)
def log_user_event(event):
    user = event.object
    
    query = Session.query(User).filter(User.name == user.getId())
    if query.count() != 0: # if this user exists
        user = query.one()
        record = LoginRecord(user_id = user.id, user_name = user.name)
        Session.add(record)