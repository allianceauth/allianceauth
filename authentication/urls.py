from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from authentication import views
from registration.backends.hmac import urls

# inject our custom view classes into the HMAC scheme but use their urlpatterns because :efficiency:
urls.views = views

app_name = 'authentication'

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='public/login.html'), name='login'),
    url(r'^account/login/$', TemplateView.as_view(template_name='public/login.html')),
    url(r'^account/characters/main/$', views.main_character_change, name='change_main_character'),
    url(r'^account/characters/add/$', views.add_character, name='add_character'),
    url(r'^account/', include(urls, namespace='registration')),
    url(r'^help/$', login_required(TemplateView.as_view(template_name='public/help.html')), name='help'),
    url(r'^dashboard/$',
        login_required(TemplateView.as_view(template_name='authentication/dashboard.html')), name='dashboard'),
]
