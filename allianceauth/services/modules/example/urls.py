from django.conf.urls import url, include

app_name = 'example'

module_urls = [
    # Add your module URLs here
]

urlpatterns = [
    url(r'^example/', include((module_urls, app_name), namespace=app_name)),
]
