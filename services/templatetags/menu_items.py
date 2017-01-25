from __future__ import unicode_literals

from django import template

from alliance_auth.hooks import get_hooks

register = template.Library()


def process_menu_items(hooks, request):
    _menu_items = list()
    items = [fn() for fn in hooks]
    items.sort(key=lambda i: i.order)
    for item in items:
        _menu_items.append(item.render(request))
    return _menu_items


@register.inclusion_tag('public/menublock.html', takes_context=True)
def menu_main(context):
    request = context['request']

    return {
        'menu_items': process_menu_items(get_hooks('menu_main_hook'), request),
    }


@register.inclusion_tag('public/menublock.html', takes_context=True)
def menu_aux(context):
    request = context['request']

    return {
        'menu_items': process_menu_items(get_hooks('menu_aux_hook'), request),
    }


@register.inclusion_tag('public/menublock.html', takes_context=True)
def menu_util(context):
    request = context['request']

    return {
        'menu_items': process_menu_items(get_hooks('menu_util_hook'), request),
    }
