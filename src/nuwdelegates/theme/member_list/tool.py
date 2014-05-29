from five import grok
from nuw.types import Base
from nuw.types.authentication import get_user_worksite
from nuw.types.member import Person, email_exists, EmailExists, change_person_email
from nuw.types.role import Role, RoleType, get_person_agencies
from nuwdelegates.theme.interfaces import IThemeSpecific
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from sqlalchemy import Column, String, desc, func, PickleType
from sqlalchemy.dialects.postgresql import UUID
from z3c.saconfig import named_scoped_session
from zope.interface import Interface, implements
from zope.lifecycleevent import ObjectAddedEvent, ObjectModifiedEvent

import datetime
import json
import re
import uuid
import zope

from pprint import pprint

Session = named_scoped_session( 'nuw.types' )

grok.templatedir( 'templates' )
grok.layer( IThemeSpecific )

DEFAULT_CUSTOM_NAMES = {'custom1': 'Has Joined', 'custom2': 'Task1 (y/n)', 'custom3': 'Task2 (y/n)'}

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

class IMembersListAPITool( Interface ):
    '''
        Tool that shows a grid listing of NUW Members
    '''
    pass


class MembersListAPITool( UniqueObject, SimpleItem ):
    id = 'portal_memberslistapi'
    meta_type = 'NUW Members List API Tool'
    plone_tool = 1

    implements( IMembersListAPITool )

class MemberListColumnConfig( Base ):
    '''
        Stores a worksite's column configuration
    '''
    __tablename__ = 'memberlist_column_config'

    worksite_id = Column( UUID, primary_key = True )
    columns = Column(String)      # JSON Encoded list of column names
    custom_names = Column(String) # JSON Encoded list of names for each of the custom columns
    column_config = Column(PickleType) # Pickled dict of column configuration, types and their vocbaularies if applicable

# API Calls

class GetColumns( grok.View ):
    '''
        Will return a list of column names enabled for the current users worksite
    '''
    grok.context( IMembersListAPITool )
    grok.name( 'get_columns' )

    def render( self ):
        worksite = get_user_worksite( self.context )

        sess = Session()

        colconf = sess.query( MemberListColumnConfig ).filter( MemberListColumnConfig.worksite_id == worksite.groupid ).first()

        if colconf:
            return json.dumps( {
                'columns': json.loads( colconf.columns ),
                'custom_names': json.loads( colconf.custom_names ),
                'column_config' : colconf.column_config
            } )
        else:
            return json.dumps( {
                'columns': [ 'nuwdbid', 'name', 'shift', 'activity', 'locationcode', 'custom1', 'custom2', 'custom3', 'custom4' ],
                'custom_names': DEFAULT_CUSTOM_NAMES,
                'column_config' : None
            } )

class SetColumns(grok.View):
    '''
        Will set the active columns for the current users worksite
    '''
    grok.context(IMembersListAPITool)
    grok.name('set_columns')

    def update(self):
        if self.request.form:
            worksite = get_user_worksite(self.context)

            sess = Session()

            cols = self.request.form.pop('column[]')

            # Check if there is a config already
            conf = sess.query(MemberListColumnConfig).filter(MemberListColumnConfig.worksite_id == worksite.groupid).first()

            if conf:
                conf.columns = json.dumps(cols)
            else:
                # Create new config with default custom names
                conf = MemberListColumnConfig(worksite_id = worksite.groupid, columns = json.dumps(cols), custom_names = json.dumps(DEFAULT_CUSTOM_NAMES))

            sess.add(conf)

    def render(self):
        return json.dumps({'status': 'OK'})

class SaveCustomColumns(grok.View):
    """
    Saves the custom names and costum configuration for the worksite if available.
    """
    grok.context(IMembersListAPITool)
    grok.name('save_custom_columns')

    def update(self):
        if self.request.form:
            worksite = get_user_worksite(self.context)
            sess = Session()
            form = self.request.form

            # TODO: should really merged the two fields
            custom_names = {}
            for k in form.keys():
                if len(k.split('-')) == 1:
                    custom_names.update({k:form.pop(k)})

            # Check if there is a config already
            conf = sess.query(MemberListColumnConfig).filter(MemberListColumnConfig.worksite_id == worksite.groupid).first()
            if conf:
                conf.custom_names = json.dumps(custom_names)
                conf.column_config = form # PickleType ftw!
            else:
                # Create new config with default custom names
                conf = MemberListColumnConfig(worksite_id = worksite.groupid, custom_names = json.dumps(DEFAULT_CUSTOM_NAMES), column_config = form)

    def render(self):
        return json.dumps({'status': 'OK' })



class AddMember( grok.View ):
    '''
        Will add a member to the current users worksite
    '''
    grok.context( IMembersListAPITool )
    grok.name( 'add_member' )

    data = None

    def update( self ):
        if self.request.form:
            self.data = self.request.form

    def render( self ):
        if self.data:
            sess = Session()

            worksite = get_user_worksite( self.context )
            personid = str( uuid.uuid4() )

            try:
                self.data[ 'type' ] = 'Potential Member'
                self.data[ 'status' ] = 'potential member'

                pers = Person( personid, **self.data )
                sess.add( pers )
                role = Role( str( uuid.uuid4() ), groupid = worksite.groupid, personid = personid, role = 'Employee', startdate = datetime.datetime.now().isoformat() )
                sess.add( role )

                zope.event.notify( ObjectAddedEvent( pers, self.context, pers.id ) )
                zope.event.notify( ObjectAddedEvent( role, self.context, role.id ) )
                return json.dumps( { 'status': 'ok' } )
            except Exception as e:
                return json.dumps( { 'status': 'fail', 'except': str( e ) } )

class UpdateMember( grok.View ):
    '''
        Will update a members details
    '''
    grok.context( IMembersListAPITool )
    grok.name( 'update_member' )

    data = None

    def update( self ):
        if self.request.form:
            self.data = self.request.form

    def render( self ):
        if self.data:
            sess = Session()

            try:
                pers = sess.query( Person ).filter( Person.id == self.data['id'] ).first()
                if pers.email != self.data.get( 'email', pers.email ):
                    if email_exists( self.data['email'], personid = pers.personid ):
                        raise EmailExists
                    # Email is being updated. Need to update any subscriptions
                    change_person_email( self.context, pers, self.data[ 'email' ] )
                if self.data.get('dob', '') == '':
                    self.data['dob'] = None
                Person.apply_mapped_data( pers, self.data )
                sess.add( pers )
                zope.event.notify( ObjectModifiedEvent( pers ) )
                return json.dumps( { 'status': 'ok' } )
            except Exception as e:
                return json.dumps( { 'status': 'fail', 'except': str( e ) } )

class GetMembers( grok.View ):
    '''
        Will return a list of members based on query params
    '''
    grok.context( IMembersListAPITool )
    grok.name( 'get_members' )

    # Query params
    start = 0
    end = 0
    sort_column = None
    sort_dir = None
    search_string = None

    def update( self ):
        if self.request.form:
            self.start = int( self.request.form.get('start', 0))
            self.end = int( self.request.form.get('end', 0))
            self.sort_column = self.request.form.get('sort_column', None)
            self.sort_dir = self.request.form.get('sort_dir', None)
            self.search_string = self.request.form.get('search_string', None)
            self.search_type = self.request.form.get('search_type', None)

    def render( self ):
        sess = Session()

        ret = { 'members': [] }


        worksite = get_user_worksite( self.context )

        if worksite:
            q = sess.query( Person, func.string_agg( RoleType.token, ',' ).label( 'roles' ) ).filter(
                Role.personid == Person.personid, Role.groupid == worksite.groupid,
                Role.enddate.is_( None ) | ( Role.enddate > func.current_timestamp() ),
                RoleType.id == Role.type_id
            ).group_by( Person )

            if self.sort_column and hasattr( Person, self.sort_column ):
                if self.sort_dir and self.sort_dir == 'desc':
                    q = q.order_by( desc( getattr( Person, self.sort_column ) ) )
                else:
                    q = q.order_by( getattr( Person, self.sort_column ) )
            elif self.sort_column == 'name':
                # Sort the composite name column
                if self.sort_dir and self.sort_dir == 'desc':
                    q = q.order_by( desc( Person.lastname + ' ' + Person.firstname ) )
                else:
                    q = q.order_by( Person.firstname + ' ' + Person.lastname )

            if self.search_string and self.search_string != '':
                if self.search_type == 'name':
                    q = q.filter( getattr(Person, 'firstname').ilike( '%' + self.search_string + '%' ) | getattr(Person, 'lastname').ilike( '%' + self.search_string + '%' ) )
                elif self.search_type == 'postaddr':
                    q = q.filter( getattr(Person, 'postaddress1').ilike( '%' + self.search_string + '%' ) \
                                | getattr(Person, 'postaddress2').ilike( '%' + self.search_string + '%' ) \
                                | getattr(Person, 'postsuburb').ilike( '%' + self.search_string + '%' ) \
                                | getattr(Person, 'poststate').ilike( '%' + self.search_string + '%' ) \
                                | getattr(Person, 'postpcode').ilike( '%' + self.search_string + '%' ) )
                elif self.search_type == 'homeaddr':
                    q = q.filter( getattr(Person, 'homeaddress1').ilike( '%' + self.search_string + '%' ) \
                                | getattr(Person, 'homeaddress2').ilike( '%' + self.search_string + '%' ) \
                                | getattr(Person, 'homesuburb').ilike( '%' + self.search_string + '%' ) \
                                | getattr(Person, 'homestate').ilike( '%' + self.search_string + '%' ) \
                                | getattr(Person, 'homepostcode').ilike( '%' + self.search_string + '%' ) )
                elif self.search_type == 'postrts':
                    if self.search_string == 'true':
                        q = q.filter(getattr(Person, self.search_type) == True)
                    elif self.search_string == 'false':
                        q = q.filter(getattr(Person, self.search_type) == False)
                elif self.search_type == 'webstatus':
                    if self.search_string == 'P':
                        q = q.filter(getattr(Person, self.search_type) == '')
                    elif self.search_string == 'M':
                        q = q.filter((getattr(Person, self.search_type) == 'financial-member') | (getattr(Person, self.search_type) == 'unfinancial-member'))
                else:
                    q = q.filter(getattr(Person, self.search_type).ilike( '%' + self.search_string + '%' ))



            ret['total'] = q.count()
            ret['member_total'] = 0

            q = q[ self.start : self.end ]

            for mem, roles in q:
                data = mem.__dict__

                # Get Person's roles
                data['roles'] = roles.split( ',' )
                # Get Person's webstatuses
                data['webstatuses'] = mem.webstatuses
                del data['webstatus']

                if 'financial-member' in data['webstatuses']\
                        or 'unfinancial-member' in data['webstatuses']:
                        ret['member_total'] += 1

                data['type'] = mem.type and mem.type.token

                agencies = get_person_agencies(mem.personid)
                if agencies is not None and len(agencies):
                    data['agency'] = agencies[0].name
                else:
                    data['agency'] = None

                data.pop( '_sa_instance_state', None )

                if self.search_type == 'webstatus' and not self.search_string == '' and not self.search_string == 'P'\
                    and not self.search_string == 'M':
                    if self.search_string == 'D' and 'Delegate' in data['roles']:
                        if 'financial-member' in data['webstatuses']\
                        or 'unfinancial-member' in data['webstatuses']:
                            ret['members'].append(data)
                    elif self.search_string == '+' and 'Delegate' in data['roles'] and 'HSR' in data['roles']:
                        ret['members'].append(data)
                    elif self.search_string == 'H' and 'HSR' in data['roles']:
                        ret['members'].append(data)
                    elif self.search_string == 'A' and mem.activity == 'active':
                        ret['members'].append(data)
                    elif self.search_string == 'X' and mem.activity == 'hostile':
                        ret['members'].append(data)
                else:
                    ret['members'].append( data )
        else:
            ret['total'] = 0

        return json.dumps( ret, cls = DateEncoder )
