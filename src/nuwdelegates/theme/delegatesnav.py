from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

class INavigationNUW(IPortletDataProvider):
    """ These are not the classes you are looking for, move along. """

class Assignment(base.Assignment):
    implements(INavigationNUW)

    @property
    def title(self):
        return _(u"Union Rep Navigation")

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('browser/delegatesnav.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()


class AddForm(base.AddForm):
    form_fields = form.Fields(INavigationNUW)
    label = _(u"Add Union Rep Navigation Portlet")
    description = _(u"This portlet displays links to sections within the Rep site.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(INavigationNUW)
    label = _(u"Edit Union Rep Navigation Portlet")
    description = _(u"This portlet displays links to sections within the Rep site.")
