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
# -*- coding: utf-8 -*-

from django.template import Context, Template
from django.test import TestCase, RequestFactory


class NavhelperTemplateTagTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_navactive(self):
        self._navactive_common('active', '')

        with self.settings(NAVHELPER_ACTIVE_CLASS='my-active-class',
                           NAVHELPER_NOT_ACTIVE_CLASS='my-not-active-class'):
            self._navactive_common('my-active-class', 'my-not-active-class')

    def test_renavactive(self):
        self._renavactive_common('active', '')

        with self.settings(NAVHELPER_ACTIVE_CLASS='my-active-class',
                           NAVHELPER_NOT_ACTIVE_CLASS='my-not-active-class'):
            self._renavactive_common('my-active-class', 'my-not-active-class')

    def _navactive_common(self, active, not_active):
        request = self.factory.get('/main-page/')

        out = Template(
                "{% load navactive %}"
                "{% navactive request 'p1' %}"
            ).render(Context({"request": request}))
        self.assertEqual(out, active)

        out = Template(
                "{% load navactive %}"
                "{% navactive request 'p1-s1' %}"
            ).render(Context({"request": request}))
        self.assertEqual(out, not_active)

        out = Template(
                "{% load navactive %}"
                "{% navactive request 'p1 p1-s1' %}"
            ).render(Context({"request": request}))
        self.assertEqual(out, active)

        out = Template(
                "{% load navactive %}"
                "{% navactive request 'p2' %}"
            ).render(Context({"request": request}))
        self.assertEqual(out, not_active)

    def _renavactive_common(self, active, not_active):
        t1 = "{% load navactive %}{% renavactive request '^/main-page' %}"

        request = self.factory.get('/main-page/')
        out = Template(t1).render(Context({"request": request}))
        self.assertEqual(out, active)

        request = self.factory.get('/main-page/sub-section/')
        out = Template(t1).render(Context({"request": request}))
        self.assertEqual(out, active)

        request = self.factory.get('/second-page/')
        out = Template(t1).render(Context({"request": request}))
        self.assertEqual(out, not_active)
