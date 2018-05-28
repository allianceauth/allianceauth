# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

__version__ = '2.0.4'
NAME = 'Alliance Auth v%s' % __version__
default_app_config = 'allianceauth.apps.AllianceAuthConfig'
