from five import grok
from zope import event
from zope.interface import Interface
from zope.lifecycleevent import ObjectAddedEvent
from z3c.saconfig import named_scoped_session
from Products.statusmessages.interfaces import IStatusMessage

from nuw.types.record import Record
from nuw.types.group import Group
from nuw.types.grouprecord import GroupRecord

from datetime import datetime
import uuid

grok.templatedir('templates')

Session = named_scoped_session('nuw.types')

class ISendSMS(Interface):
    """ SendSMS Marker interface
    """

class SendSMS(grok.View):
    grok.context(ISendSMS)
    character_limit = 140

    def update(self):
        self.errors = dict()
        self.success = False

        self.entry = self.request.form.get('entry', None)
        self.worksites = self.request.form.get('worksites', None)
        self.campaigns = self.request.form.get('campaigns', None)
        if self.worksites and self.campaigns:
            self.errors['recipients'] = 'Please only choose from either worksites or campaigns. '
        self.recipients = self.worksites or self.campaigns

        if self.entry == '':
            self.errors['entry'] = 'Please enter in a message. '

        if self.entry:
            if len(self.entry) > self.character_limit:
                self.errors['entry'] = 'Please limit message to less than 140 characters. '

            if self.recipients == [''] or not self.recipients:
                self.errors['recipients'] = 'Please choose at least one worksite, or a campaign. '

            if not self.errors:
                self.success = True
                self.submit_message(self.recipients, self.entry)
                return

        if self.errors:
            IStatusMessage(self.request).addStatusMessage(
                    unicode(self.errors.get('entry', '') + self.errors.get('recipients', '')),
                    'error')

    def submit_message(self, recipients, message):
        message = unicode(message)
        sess = Session()
        for recipient in recipients:
            group = sess.query(Group).filter(Group.groupid==unicode(recipient)).first()
            if not group:
                IStatusMessage(self.request).addStatusMessage(
                    u'Group of id: '+recipient+' not found within DB!',
                    'error')
                return

        time_now = datetime.now()
        new_recordid = str(uuid.uuid4())
        new_sms = Record(new_recordid, notes=message, type='SMS', startdate=time_now)
        sess.add(new_sms)
        # notify the API
        event.notify(ObjectAddedEvent(new_sms, self, new_sms.id))
        new_sms = sess.query(Record).filter(Record.recordid==new_recordid).first()
        if new_sms:
            for recipient in recipients:
                new_grouprecord = GroupRecord(str(uuid.uuid4()), groupid=unicode(recipient), recordid=new_recordid)
                sess.add(new_grouprecord)
                # notify the API
                event.notify(ObjectAddedEvent(new_grouprecord, self, new_grouprecord.id))
            IStatusMessage(self.request).addStatusMessage(
                u'Your SMS has been added, ready to be sent!',
                'info')
            self.recipients = None
            self.entry = None
            self.campaigns = None
            self.worksites = None
            self.errors = dict()
        else:
            IStatusMessage(self.request).addStatusMessage(
                u'New SMS not found within DB!',
                'error')
            return

        return True

    def get_messages(self):
        sess = Session()
        messages = list()
        for record in sess.query(Record).filter(Record.recordtype_id==1).order_by(Record.id.desc()).limit(10):
            recipients = '['
            for grouprecord in sess.query(GroupRecord).filter(GroupRecord.recordid==record.recordid):
                for group in sess.query(Group).filter(Group.groupid==grouprecord.groupid):
                    recipients += str(group.long_name or group.name)+',\n'
            messages.append({'message':record.notes,
                    'recipients':recipients[:len(recipients)-2]+']',
                    'sent':self.context.toLocalizedTime(record.startdate, long_format=1)})
        return messages

    def get_group_longname(self, groupid):
        sess = Session()
        group = sess.query(Group).filter(Group.groupid==groupid).first()
        if group:
            return group.long_name
        return groupid + " not found!"

    def get_campaigns(self):
        sess = Session()
        return sess.query(Group).filter(Group.grouptype_id == 6).order_by(Group.id.desc())
