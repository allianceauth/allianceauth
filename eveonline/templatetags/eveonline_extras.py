from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='api_link')
def api_link(api, style_class):
    if settings.API_KEY_AUDIT_URL:
        url = settings.API_KEY_AUDIT_URL.format(api_id=api.api_id, vcode=api.api_key, pk=api.pk)
        element = "<a href='{url}' class='{style}' target='_new'>{api_id}</a>".format(url=url, style=style_class,
                                                                                      api_id=api.api_id)
    else:
        element = "<a href='#' class='{style}' onclick='return prompt({prompt}, {vcode})'>{api_id}</a>".format(
            style=style_class, prompt='"Verification Code"', vcode='"%s"' % api.api_key, api_id=api.api_id)
    return mark_safe(element)
