# -*- extra stuff goes here -*-
from iw.rejectanonymous import addValidSubpartPrefixes, addValidIds
# Make sure less files get loaded
addValidIds( 'compiled_styles.css', 'logged_out' )
addValidSubpartPrefixes( 'themenuwdelegates.themeless' )

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

