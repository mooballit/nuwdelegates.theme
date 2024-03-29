from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer bound to a Skin
       Selection in portal_skins.
       If you need to register a viewlet only for the nuwdelegates.theme
       skin, this is the interface that must be used for the layer attribute
       in nuwdelegates.theme/browser/configure.zcml.
    """
