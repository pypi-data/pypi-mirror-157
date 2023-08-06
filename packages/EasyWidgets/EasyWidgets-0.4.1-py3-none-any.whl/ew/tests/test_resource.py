import os.path
import textwrap

from webob import Response
from webtest import TestApp

from ew import widget_context, Snippet, WidgetMiddleware, Widget
from ew import ResourceManager
from ew.tests.helpers import REGISTRY

import ew.jinja2_ew
import pytest

TEMPLATE = Snippet('''<html>
<head>
{% for x in resource_manager.emit('head_css') %}{{ x }}{% endfor %}
{% for x in resource_manager.emit('head_js') %}{{ x }}{% endfor %}
</head>
<body>
{% for x in resource_manager.emit('body_top_js') %}{{ x }}{% endfor %}
{{ widget.display() }}
{% for x in resource_manager.emit('body_js') %}{{ x }}{% endfor %}
{% for x in resource_manager.emit('body_js_tail') %}{{ x }}{% endfor %}
</body>
</html>''', 'jinja2')


class TestResourceInclusion:

    def setup_method(self):
        self.w = Widget(
            template=Snippet('<h1>My Widget</h1>'),
            resources=lambda:[
                self.ew.CSSScript('/* head_css */'),
                self.ew.JSScript('/* head_js */', 'head_js'),
                self.ew.JSScript('/* body_top_js */', 'body_top_js'),
                self.ew.JSScript('/* body_js */', 'body_js'),
                self.ew.JSScript('/* body_tail */', 'body_js_tail')
                ])
        self.app = TestApp(_WidgetTest(self.w))
    ew = ew.jinja2_ew

    def test_render(self):
        res = self.app.get('/')
        parts = [
            '''<!-- ew:head_css -->
<style>/* head_css */</style>
<!-- /ew:head_css -->''',
            '''<!-- ew:head_js -->
<script type="text/javascript">/* head_js */</script>
<!-- /ew:head_js -->''',
            '''<!-- ew:body_top_js -->
<script type="text/javascript">/* body_top_js */</script>
<!-- /ew:body_top_js -->''',
            '''<h1>My Widget</h1>''',
            '''<!-- ew:body_js -->
<script type="text/javascript">/* body_js */</script>
<!-- /ew:body_js -->''',
            '''<!-- ew:body_js_tail -->
<script type="text/javascript">/* body_tail */</script>
<!-- /ew:body_js_tail -->''' ]
        for part in parts:
            assert part in res, f'{part} not in {res}'


class TestScripts:

    def setup_method(self):
        self.resources = [
                self.ew.JSLink('a/foo.js'),
                self.ew.JSLink('a/bar.js'),
                self.ew.CSSLink('a/foo.css'),
                self.ew.CSSLink('a/bar.css')]
        self.w = Widget(
            template=Snippet('<h1>My Widget</h1>'),
            resources=lambda:self.resources)
        ResourceManager.paths = []
        self.wtest = _WidgetTest(self.w)
        self.app = TestApp(self.wtest)

    ew = ew.jinja2_ew

    def test_render(self):
        app = TestApp(_WidgetTest(self.w))
        res = app.get('/')
        assert 'href="/_ew_resources/a/foo.css"' in res, res
        assert 'href="/_ew_resources/a/bar.css"' in res, res
        assert 'src="/_ew_resources/a/foo.js"' in res, res
        assert 'src="/_ew_resources/a/bar.js"' in res, res

    def test_serve(self):
        app = TestApp(_WidgetTest(self.w))
        app.get('/some/arbitrary/url')
        app.get('/_ew_resources/a/foo.css', status=404)
        ResourceManager.register_directory(
            'a',
            os.path.join(os.path.dirname(__file__), 'data'))
        res = app.get('/_ew_resources/a/test.css')
        assert '/* Test CSS file */'  in res, res
        assert str(res).count('/* Test CSS file */') == 1, res

    def test_render_compressed(self):
        app = TestApp(_WidgetTest(self.w, compress=True))
        res = app.get('/')
        assert ('href="/_ew_resources/_slim/css?href='
            'a%2Ffoo.css%3Ba%2Fbar.css"') in  res, res
        assert ('src="/_ew_resources/_slim/js?href='
            'a%2Ffoo.js%3Ba%2Fbar.js"') in res, res

    def test_serve_compressed(self):
        ResourceManager.resource_cache = {}
        app = TestApp(_WidgetTest(self.w, use_jsmin=False))
        app.get('/some/arbitrary/url')
        app.get('/_ew_resources/a/foo.css', status=404)
        ResourceManager.register_directory(
            'a',
            os.path.join(os.path.dirname(__file__), 'data'))
        res = app.get('/_ew_resources/_slim/css?href=a%2Ftest.css%3Ba%2Ftest.css')
        assert str(res).count('/* Test CSS file */') == 2, res
        old_sz = len(str(app.get('/_ew_resources/_slim/js?href=a%2Ftest.js')))
        app = TestApp(_WidgetTest(self.w, use_jsmin=True, use_cssmin=True))
        ResourceManager.resource_cache = {}
        res = app.get('/_ew_resources/_slim/js?href=a%2Ftest.js')
        assert len(str(res)) < old_sz, res
        res = app.get('/_ew_resources/_slim/css?href=a%2Ftest.css')
        assert res.text == textwrap.dedent('''
        /* a/test.css */
        .foo{color:red}.foo{background-color:blue}''')
        res = app.get('/_ew_resources/_slim/css?href=a%2Ftest-utf8.css')
        assert '/foo/ƒ¶≈ç.test' in res.text
        res = app.get('/_ew_resources/_slim/js?href=a%2Ftest-utf8.js')
        assert 'ƒ∂ß' in res.text

        app.get('/_ew_resources/_slim/js')  # no param
        app.get('/_ew_resources/_slim/js?href=foo;bar;;baz')  # bad params

    def test_reregister(self):
        ResourceManager.register_directory('a', 'foo')
        ResourceManager.register_directory('a', 'foo')
        with pytest.raises(AssertionError):
            ResourceManager.register_directory('a', 'bar')

    def test_incompressible(self):
        self.resources.append(self.ew.JSLink('a/baz.js', compress=False))
        app = TestApp(_WidgetTest(self.w, compress=True))
        res = app.get('/')
        assert ('src="/_ew_resources/_slim/js?href='
                'a%2Ffoo.js%3Ba%2Fbar.js"') in res, res
        assert 'src="/_ew_resources/a/baz.js"' in res, res


class _WidgetTest:

    def __init__(self, widget, **kwargs):
        self.widget = widget
        kw = dict(register_resources=False)
        kw.update(kwargs)
        self.app = WidgetMiddleware(self._core_app, **kw)

    def __call__(self, environ, start_response):
        environ['paste.registry'] = REGISTRY
        return self.app(environ, start_response)

    def _core_app(self, environ, start_response):
        res = Response()
        widget_context.resource_manager.register(self.widget)
        res.text = TEMPLATE(dict(
                widget=self.widget,
                resource_manager=widget_context.resource_manager))
        return res(environ, start_response)

class TestResourceSecurity:

    def setup_method(self):
        self.rm = ResourceManager()
        self.rm.register_directory('res-test', '/a/b/c')

    def test_cant_break_out(self):
        assert self.rm.get_filename('res-test/../etc/passwd') ==    None

