"""
The MIT License (MIT)

Copyright (c) 2013 Guillaume Luchet

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from django.template import Library
from django.urls import resolve
from django.conf import settings
import re

register = Library()


@register.simple_tag
def renavactive(request, pattern):
    """
    {% renavactive request "^/a_regex" %}
    """
    if re.search(pattern, request.path):
        return getattr(settings, "NAVHELPER_ACTIVE_CLASS", "active")
    return getattr(settings, "NAVHELPER_NOT_ACTIVE_CLASS", "")


@register.simple_tag
def navactive(request, urls):
    """
    {% navactive request "view_name another_view_name" %}
    """
    url_list = set(urls.split())

    resolved = resolve(request.path)
    resolved_urls = set()
    if resolved.url_name:
        resolved_urls.add(resolved.url_name)
    if resolved.namespaces:
        resolved_urls = resolved_urls.union(["{}:{}".format(namespace, resolved.url_name) for namespace in resolved.namespaces])
        resolved_urls = resolved_urls.union(["{}:".format(namespace) for namespace in resolved.namespaces])
    if getattr(resolved, 'app_name', None):
        resolved_urls = resolved_urls.union(["{}:{}".format(resolved.app_name, resolved.url_name), "{}:".format(resolved.app_name)])
    if getattr(resolved, 'app_names', []):
        resolved_urls = resolved_urls.union(["{}:{}".format(app_name, resolved.url_name) for app_name in resolved.app_names])
        resolved_urls = resolved_urls.union(["{}:".format(app_name) for app_name in resolved.app_names])
    if url_list and resolved_urls and bool(resolved_urls & url_list):
        return getattr(settings, "NAVHELPER_ACTIVE_CLASS", "active")
    return getattr(settings, "NAVHELPER_NOT_ACTIVE_CLASS", "")
