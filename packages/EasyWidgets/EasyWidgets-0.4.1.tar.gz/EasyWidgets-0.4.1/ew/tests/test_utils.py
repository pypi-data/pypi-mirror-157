import pytest

from ew import utils
from ew import widget


class TestBunch:

    def test_like_dict(self):
        b = utils.Bunch(
            foo=0, bar=1)
        assert b == dict(foo=0, bar=1)

    def test_like_object(self):
        b = utils.Bunch(
            foo=0, bar=1)
        assert b.foo == 0
        assert b.bar == 1

    def test_invalid_getattr(self):
        b = utils.Bunch(
            foo=0, bar=1)
        with pytest.raises(AttributeError):
            getattr(b, 'baz')

    def test_invalid_getitem(self):
        b = utils.Bunch(
            foo=0, bar=1)
        pytest.raises(KeyError, b.__getitem__, 'baz')


class TestPushContext:

    def test_push_context(self):
        x = utils.Bunch(foo=1, bar=2)
        with utils.push_context(x, foo=4, baz=0):
            assert x.foo == 4
            assert x.bar == 2
            assert x.baz == 0
        assert x.foo == 1
        pytest.raises(KeyError, x.__getitem__, 'baz')


class TestNameListAsClass:

    def setup_method(self):
        class widgets(utils.NameList):
            a=widget.Widget()
            b=widget.Widget(name='boo')
        self.widgets = widgets

    def test_widget_names(self):
        assert self.widgets.a.name == 'a'
        assert self.widgets.b.name == 'boo'
        with pytest.raises(AttributeError):
            getattr(self.widgets, 'c')

    def test_widgets_by_index(self):
        assert self.widgets[0] == self.widgets.a
        assert self.widgets[1] == self.widgets.b
        assert self.widgets == [ self.widgets.a, self.widgets.b ]


class TestWidgetListAsList:

    def setup_method(self):
        self.a = widget.Widget(name='a')
        self.b = widget.Widget(name='b')
        self.c = widget.Widget(name='c')
        self.widgets = utils.NameList([self.a,self.b])
        self.widgets.append(self.c)

    def test_widgets_by_index(self):
        assert self.widgets[0] == self.a
        assert self.widgets[1] == self.b
        assert self.widgets[2] == self.c
        assert self.widgets == [ self.a, self.b, self.c ]

    def test_widgets_by_name(self):
        assert self.widgets.a == self.a
        assert self.widgets.b == self.b
        assert self.widgets['a'] == self.a
        assert self.widgets['b'] == self.b
