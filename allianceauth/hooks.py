"""
Copyright (c) 2014 Torchbox Ltd and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Torchbox nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Based on https://github.com/torchbox/wagtail/blob/master/wagtail/wagtailcore/hooks.py
"""

from importlib import import_module

from django.apps import apps
from django.utils.module_loading import module_has_submodule

import logging

logger = logging.getLogger(__name__)

_hooks = {}  # Dict of Name: Fn's of registered hooks

_all_hooks_registered = False  # If all hooks have been searched for and registered yet


def register(name, fn=None):
    """
    Decorator to register a function as a hook

    Register hook for ``hook_name``. Can be used as a decorator::
        @register('hook_name')
        def my_hook(...):
            pass

    or as a function call::
        def my_hook(...):
            pass
        register('hook_name', my_hook)

    :param name: str Name of the hook/callback to register it as
    :param fn: function to register in the hook/callback
    :return: function Decorator if applied as a decorator
    """
    def _hook_add(func):
        if name not in _hooks:
            logger.debug("Creating new hook %s" % name)
            _hooks[name] = []

        logger.debug('Registering hook %s for function %s' % (name, fn))
        _hooks[name].append(func)

    if fn is None:
        # Behave like a decorator
        def decorator(func):
            _hook_add(func)
            return func
        return decorator
    else:
        # Behave like a function, just register hook
        _hook_add(fn)


def get_app_modules():
    """
    Get all the modules of the django app
    :return: name, module tuple
    """
    for app in apps.get_app_configs():
        yield app.name, app.module


def get_app_submodules(module_name):
    """
    Get a specific sub module of the app
    :param module_name: module name to get
    :return: name, module tuple
    """
    for name, module in get_app_modules():
        if module_has_submodule(module, module_name):
            yield name, import_module('{0}.{1}'.format(name, module_name))


def register_all_hooks():
    """
    Register all hooks found in 'auth_hooks' sub modules
    :return:
    """
    global _all_hooks_registered
    if not _all_hooks_registered:
        logger.debug("Searching for hooks")
        hooks = list(get_app_submodules('auth_hooks'))
        logger.debug("Got %s hooks" % len(hooks))
        _all_hooks_registered = True


def get_hooks(name):
    """
    Get all the hook functions for the given hook name
    :param name: str name of the hook to get the functions for
    :return: list of hook functions
    """
    register_all_hooks()
    return _hooks.get(name, [])

