#!/usr/bin/env pytest --capture=no

import os
import shutil
import enum
import typing
import pytest
import re

from udsync.base_classes import Logger
from udsync.config import Config, DictConfig, ConfigExporter, MultiConfig, MultiDictConfig, ConfigId, Command, CommandWithAlternatives
from udsync.urwid_multi_key_support import HelpItem
from udsync import urwid_colors


PATH_ROOT = 'autotest'
FN_CONFIG = os.path.join(PATH_ROOT, 'config')

@pytest.fixture(autouse=True)
def reset_config() -> None:
	Config.instances.clear()
	MultiConfig.config_ids.clear()
	urwid_colors.ColorConfig.color_configs.clear()

@pytest.fixture()
def create_test_dir() -> None:
	if os.path.exists(PATH_ROOT):
		shutil.rmtree(PATH_ROOT)
	os.mkdir(PATH_ROOT)


class ParseError(ValueError):
	pass

class TestLogger(Logger):
	def show_error(self, msg: typing.Union[BaseException, str]) -> None:
		raise ParseError(msg)
	def show_info(self, msg: str) -> None:
		pass

exporter = ConfigExporter(TestLogger())


class COLOR(enum.Enum):
	RED = 'red'
	GREEN = 'green'
	BLUE = 'blue'


def test_get_and_set() -> None:
	class MyTestClass:
		myint = Config('a', 42, help='test attribute')

	t = MyTestClass()

	assert t.myint == 42
	assert isinstance(type(t).myint, Config)
	assert type(t).myint.key == 'a'
	assert type(t).myint.value == 42
	assert type(t).myint.help == 'test attribute'

	t.myint = 0

	assert t.myint == 0
	assert isinstance(type(t).myint, Config)
	assert type(t).myint.key == 'a'

def test_settings_are_consistent_across_different_objects() -> None:
	class MyTestClass:
		myint = Config('a', 42)

	t1 = MyTestClass()
	t2 = MyTestClass()

	t1.myint += 1

	assert t1.myint == 43
	assert t2.myint == 43

	t3 = MyTestClass()

	assert t1.myint == 43
	assert t2.myint == 43
	assert t3.myint == 43

def test_unique_keys() -> None:
	class A:
		a = Config('foo', 1)

	class B:
		with pytest.raises(ValueError):
			b = Config('foo', 2)

def test__format_allowed_values_or_type() -> None:
	class SomeType:
		type_name = 'something'
		def __init__(self, val: str) -> None:
			self.val = val

	class MyTestClass:
		a = Config('a', 'hello world')
		b = Config('b', True)
		c = Config('c', COLOR.RED)
		f = Config('f', 3.14159)
		i = Config('i', 42)
		s = Config('s', SomeType('foo'))

	assert MyTestClass.a.format_allowed_values_or_type() == 'a str'
	assert MyTestClass.b.format_allowed_values_or_type() == 'one of true, false'
	assert MyTestClass.c.format_allowed_values_or_type() == 'one of red, green, blue'
	assert MyTestClass.f.format_allowed_values_or_type() == 'a float'
	assert MyTestClass.i.format_allowed_values_or_type() == 'an int'
	assert MyTestClass.s.format_allowed_values_or_type() == 'a something'

def test__format_allowed_values_or_type__list__type() -> None:
	l = Config('l', [1, 2, 3])
	assert l.format_allowed_values_or_type() == 'a comma separated list of int'

def test__format_allowed_values_or_type__list__values() -> None:
	l = Config('l', [COLOR.RED, COLOR.GREEN])
	assert l.format_allowed_values_or_type() == 'a comma separated list of red, green, blue'

def test__format_allowed_values_or_type__no_article() -> None:
	class Color:
		type_name = 'foreground[,emphases][/background]'
		type_article = None
	col = Config('col', Color())
	assert col.format_allowed_values_or_type() == 'foreground[,emphases][/background]'

def test__format_allowed_values_or_type__explicit_article() -> None:
	class Hour:
		type_name = 'hour'
		type_article = 'an'
		def __init__(self, val: int) -> None:
			self.val = val
	l = Config('h', Hour(12))
	assert l.format_allowed_values_or_type() == 'an hour'


# ------- save only some -------

def test_save_some_in_given_order(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 1)
		b = Config('b', 2)
		c = Config('c', 3)
		d = DictConfig('d', {COLOR.RED:1, COLOR.GREEN:2, COLOR.BLUE:3})

	exporter.save(FN_CONFIG, [MyTestClass.b, MyTestClass.d], comments=False)

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
set b = 2
set d.blue = 3
set d.green = 2
set d.red = 1
'''

	exporter.save(FN_CONFIG, [MyTestClass.d, MyTestClass.b], comments=False)

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
set d.blue = 3
set d.green = 2
set d.red = 1
set b = 2
'''

def test_save_some_sorted(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 1)
		b = Config('b', 2)
		c = Config('c', 3)
		d = DictConfig('d', {COLOR.RED:1, COLOR.GREEN:2, COLOR.BLUE:3})

	exporter.save(FN_CONFIG, {MyTestClass.d, MyTestClass.b}, comments=False)

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
set b = 2
set d.blue = 3
set d.green = 2
set d.red = 1
'''


def test_save_ignore(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 1)
		b = Config('b', 2)
		c = Config('c', 3)
		d = DictConfig('d', {COLOR.RED:1, COLOR.GREEN:2, COLOR.BLUE:3})

	exporter.save(FN_CONFIG, ignore={MyTestClass.d, MyTestClass.b}, comments=False)

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
set a = 1
set c = 3
'''

def test_save_ignore_multi_config(create_test_dir: None) -> None:
	class MyTestClass:
		def __init__(self, config_id: ConfigId) -> None:
			self.config_id = config_id
		a = Config('a', 1)
		b = Config('b', 2)
		c = Config('c', 3)
		m = MultiConfig('m', 42)

	t1 = MyTestClass(ConfigId('1'))
	assert t1.m == 42
	t1.m = 1
	assert t1.m == 1

	t2 = MyTestClass(ConfigId('2'))
	assert t2.m == 42
	t2.m = 2
	assert t2.m == 2

	exporter.save(FN_CONFIG, ignore={MyTestClass.b, MyTestClass.m}, comments=False)

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
set a = 1
set c = 3
'''


def test_save_ignore_default_focus(create_test_dir: None) -> None:
	class MyTestClass:
		a = urwid_colors.ColorConfig('a', 'red')

	exporter.save(FN_CONFIG, comments=False)

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
set a = red/default
'''

def test_save_dont_ignore_default_focus(create_test_dir: None) -> None:
	class MyTestClass:
		a = urwid_colors.ColorConfig('a', 'red', focus='yellow')

	exporter.save(FN_CONFIG, comments=False)

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
set a = red/default
set a-focus = yellow/default
'''

# ------- syntax -------

def test_load_with_spaces(create_test_dir: None) -> None:
	class MyTestClass:
		myint = Config('a', 42)

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a = 1')

	t = MyTestClass()
	assert t.myint == 42

	exporter.load(FN_CONFIG)
	assert t.myint == 1

def test_load_without_spaces(create_test_dir: None) -> None:
	class MyTestClass:
		myint = Config('a', 42)

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a=1')

	t = MyTestClass()
	assert t.myint == 42

	exporter.load(FN_CONFIG)
	assert t.myint == 1

def test_load_without_equals(create_test_dir: None) -> None:
	class MyTestClass:
		myint = Config('a', 42)
		mystr = Config('b', 'foo')

	with open(FN_CONFIG, 'wt') as f:
		f.write('''
			set a 1
			set b "foo bar"
		''')

	t = MyTestClass()
	assert t.myint == 42
	assert t.mystr == 'foo'

	exporter.load(FN_CONFIG)
	assert t.myint == 1
	assert t.mystr == 'foo bar'

def test_load_multiple(create_test_dir: None) -> None:
	class MyTestClass:
		myint = Config('a', 42)
		mystr = Config('b', 'foo')

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a=1 b="foo bar"')

	t = MyTestClass()
	assert t.myint == 42
	assert t.mystr == 'foo'

	exporter.load(FN_CONFIG)
	assert t.myint == 1
	assert t.mystr == 'foo bar'


def test_load_multi_config(create_test_dir: None) -> None:
	class MyTestClass:
		a = MultiConfig('a', 0)
		def __init__(self, config_id: ConfigId) -> None:
			self.config_id = config_id

	with open(FN_CONFIG, 'wt') as f:
		f.write('''
			[foo]
			set a = 11

			[bar]
			set a = 22
		''')

	t1 = MyTestClass(ConfigId('none'))
	t2 = MyTestClass(ConfigId('foo'))
	t3 = MyTestClass(ConfigId('bar'))
	assert t1.a == 0
	assert t2.a == 0
	assert t3.a == 0
	assert not MultiConfig.config_ids

	exporter.load(FN_CONFIG)
	assert t1.a == 0
	assert t2.a == 11
	assert t3.a == 22
	assert MultiConfig.config_ids == [ConfigId('foo'), ConfigId('bar')]

def test_load_multi_config_include(create_test_dir: None) -> None:
	class MyTestClass:
		path_src = MultiConfig('path.src', '')
		path_dst = MultiConfig('path.dst', '')
		direction = MultiConfig('direction', '')

		def __init__(self, config_id: ConfigId) -> None:
			self.config_id = config_id

	with open(FN_CONFIG, 'wt') as f:
		f.write('''
			[doc]
			set path.src = src/documents
			set path.dst = dst/documents
			include mirror

			[music]
			set path.src = src/music
			set path.dst = dst/music
			include mirror

			[pic]
			set path.src = src/pictures
			set path.dst = dst/pictures
			include two-way
		''')

	with open(os.path.join(PATH_ROOT, 'mirror'), 'wt') as f:
		f.write('''
			set direction = '>'
		''')

	with open(os.path.join(PATH_ROOT, 'two-way'), 'wt') as f:
		f.write('''
			set direction = '<>'
		''')

	exporter.load(FN_CONFIG)

	doc = MyTestClass(ConfigId('doc'))
	pic = MyTestClass(ConfigId('pic'))
	music = MyTestClass(ConfigId('music'))

	assert doc.path_src == 'src/documents'
	assert doc.path_dst == 'dst/documents'
	assert doc.direction == '>'

	assert music.path_src == 'src/music'
	assert music.path_dst == 'dst/music'
	assert music.direction == '>'

	assert pic.path_src == 'src/pictures'
	assert pic.path_dst == 'dst/pictures'
	assert pic.direction == '<>'


def test_load_set_focus_color(create_test_dir: None) -> None:
	a = urwid_colors.ColorConfig('a', 'default')
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'default,standout/default')

	with open(FN_CONFIG, 'wt') as f:
		f.write('''
			set a-focus = red
		''')

	exporter.load(FN_CONFIG)
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'red/default')

def test_load_update_focus_color(create_test_dir: None) -> None:
	a = urwid_colors.ColorConfig('a', 'default')
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'default,standout/default')

	with open(FN_CONFIG, 'wt') as f:
		f.write('''
			set a = cyan
		''')

	exporter.load(FN_CONFIG)
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'cyan/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'cyan,standout/default')


def test_load_dont_update_focus_color_if_it_was_given_in_init(create_test_dir: None) -> None:
	a = urwid_colors.ColorConfig('a', 'default', focus='black/yellow')
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'black/yellow')

	with open(FN_CONFIG, 'wt') as f:
		f.write('''
			set a = cyan
		''')

	exporter.load(FN_CONFIG)
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'cyan/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'black/yellow')

def test_load_dont_update_focus_color_if_it_was_set_explicitly_in_config_file(create_test_dir: None) -> None:
	a = urwid_colors.ColorConfig('a', 'default')
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'default,standout/default')

	with open(FN_CONFIG, 'wt') as f:
		f.write('''
			set a-focus = magenta/cyan
			set a = cyan
		''')

	exporter.load(FN_CONFIG)
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'cyan/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'magenta/cyan')


# ------- data types -------

def test_save_and_load_int(create_test_dir: None) -> None:
	class MyTestClass:
		myint = Config('a', 42)

	t = MyTestClass()

	t.myint = 1
	assert t.myint == 1
	exporter.save(FN_CONFIG)
	assert t.myint == 1

	t.myint = 2
	assert t.myint == 2

	exporter.load(FN_CONFIG)
	assert t.myint == 1

	t.myint = 3
	exporter.save(FN_CONFIG)
	assert t.myint == 3

	t.myint = 4
	assert t.myint == 4

	exporter.load(FN_CONFIG)
	assert t.myint == 3

def test_save_and_load_bool(create_test_dir: None) -> None:
	class MyTestClass:
		mybool = Config('a', True)

	exporter.save(FN_CONFIG)

	t = MyTestClass()
	assert t.mybool == True

	t.mybool = False
	assert t.mybool == False

	exporter.load(FN_CONFIG)
	assert t.mybool == True

	t.mybool = False
	assert t.mybool == False
	exporter.save(FN_CONFIG)
	assert t.mybool == False

	t.mybool = True
	assert t.mybool == True

	exporter.load(FN_CONFIG)
	assert t.mybool == False

def test_save_and_load_float(create_test_dir: None) -> None:
	class MyTestClass:
		myfloat = Config('a', 3.14159)

	exporter.save(FN_CONFIG)

	t = MyTestClass()
	exporter.save(FN_CONFIG)
	assert t.myfloat == pytest.approx(3.14159)

	t.myfloat = 1.414
	assert t.myfloat == pytest.approx(1.414)

	exporter.load(FN_CONFIG)
	assert t.myfloat == pytest.approx(3.14159)

def test_save_and_load_str(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 'hello world')

	t = MyTestClass()
	assert t.a == 'hello world'

	t.a = 'hi there'
	assert t.a == 'hi there'
	exporter.save(FN_CONFIG)
	assert t.a == 'hi there'

	t.a = 'huhu'
	assert t.a == 'huhu'

	exporter.load(FN_CONFIG)
	assert t.a == 'hi there'

def test_save_and_load_spaces(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 'hello world')

	t = MyTestClass()
	assert t.a == 'hello world'

	t.a = '   '
	assert t.a == '   '
	exporter.save(FN_CONFIG)
	assert t.a == '   '

	t.a = 'huhu'
	assert t.a == 'huhu'

	exporter.load(FN_CONFIG)
	assert t.a == '   '

def test_save_and_load_enum(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', COLOR.RED)

	t = MyTestClass()
	assert t.a is COLOR.RED

	t.a = COLOR.GREEN
	assert t.a is COLOR.GREEN
	exporter.save(FN_CONFIG)
	assert t.a is COLOR.GREEN

	t.a = COLOR.BLUE
	assert t.a is COLOR.BLUE

	exporter.load(FN_CONFIG)
	assert t.a is COLOR.GREEN  # type: ignore [comparison-overlap]  # mypy does not undertstand that exporter.load should have changed t.a


def test_save_and_load_list_of_int(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', [42])

	t = MyTestClass()
	assert t.a == [42]

	t.a = [1, 2, 3]
	assert t.a == [1, 2, 3]
	exporter.save(FN_CONFIG)
	assert t.a == [1, 2, 3]

	t.a = [4]
	assert t.a == [4]

	exporter.load(FN_CONFIG)
	assert t.a == [1, 2, 3]

def test_save_and_load_list_of_int__with_allowed_values(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', [42], allowed_values=(1,2,3,4,5,42))

	t = MyTestClass()
	assert t.a == [42]

	t.a = [1, 2, 3]
	assert t.a == [1, 2, 3]
	exporter.save(FN_CONFIG)
	assert t.a == [1, 2, 3]

	t.a = [4]
	assert t.a == [4]

	exporter.load(FN_CONFIG)
	assert t.a == [1, 2, 3]

def test_save_and_load_list_of_enum(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', [COLOR.RED])

	t = MyTestClass()
	assert t.a == [COLOR.RED]

	t.a = [COLOR.BLUE, COLOR.GREEN]
	assert t.a == [COLOR.BLUE, COLOR.GREEN]
	exporter.save(FN_CONFIG)
	assert t.a == [COLOR.BLUE, COLOR.GREEN]

	t.a = [COLOR.RED, COLOR.BLUE]
	assert t.a == [COLOR.RED, COLOR.BLUE]

	exporter.load(FN_CONFIG)
	assert t.a == [COLOR.BLUE, COLOR.GREEN]


def test_save_and_load_dict_enum(create_test_dir: None) -> None:
	class MyTestClass:
		color = DictConfig('color', {COLOR.RED:1, COLOR.GREEN:2, COLOR.BLUE:3}, ignore_keys={COLOR.BLUE})

	t = MyTestClass()
	exporter.save(FN_CONFIG)
	assert t.color[COLOR.RED] == 1
	assert t.color[COLOR.GREEN] == 2
	assert t.color[COLOR.BLUE] == 3

	t.color[COLOR.RED] = 10
	t.color[COLOR.GREEN] = 20
	t.color[COLOR.BLUE] = 30
	assert t.color[COLOR.RED] == 10
	assert t.color[COLOR.GREEN] == 20
	assert t.color[COLOR.BLUE] == 30

	exporter.load(FN_CONFIG)
	assert t.color[COLOR.RED] == 1
	assert t.color[COLOR.GREEN] == 2
	assert t.color[COLOR.BLUE] == 30

def test_save_and_load_multi_dict_enum(create_test_dir: None) -> None:
	class MyTestClass:
		def __init__(self, config_id: str):
			self.config_id = ConfigId(config_id)
		color = MultiDictConfig('color', {COLOR.RED:1, COLOR.GREEN:2, COLOR.BLUE:3}, ignore_keys={COLOR.BLUE})

	t0 = MyTestClass('t0')
	assert t0.color[COLOR.RED] == 1
	assert t0.color[COLOR.GREEN] == 2
	assert t0.color[COLOR.BLUE] == 3

	t0.color[COLOR.RED] = -1
	t0.color[COLOR.GREEN] = -2
	with pytest.raises(TypeError):
		t0.color[COLOR.BLUE] = -3
	assert t0.color[COLOR.RED] == -1
	assert t0.color[COLOR.GREEN] == -2
	assert t0.color[COLOR.BLUE] == 3

	t1 = MyTestClass('t1')
	assert t1.color[COLOR.RED] == 1
	assert t1.color[COLOR.GREEN] == 2
	assert t1.color[COLOR.BLUE] == 3
	t1.color[COLOR.RED] = 11
	t1.color[COLOR.GREEN] = 12
	with pytest.raises(TypeError):
		t1.color[COLOR.BLUE] = 13
	assert t1.color[COLOR.RED] == 11
	assert t1.color[COLOR.GREEN] == 12
	assert t1.color[COLOR.BLUE] == 3
	assert t0.color[COLOR.RED] == -1
	assert t0.color[COLOR.GREEN] == -2
	assert t0.color[COLOR.BLUE] == 3

	exporter.save(FN_CONFIG)
	t0.color[COLOR.RED] = 100
	t0.color[COLOR.GREEN] = 200
	with pytest.raises(TypeError):
		t0.color[COLOR.BLUE] = 300
	assert t0.color[COLOR.RED] == 100
	assert t0.color[COLOR.GREEN] == 200
	assert t0.color[COLOR.BLUE] == 3
	assert t1.color[COLOR.RED] == 11
	assert t1.color[COLOR.GREEN] == 12
	assert t1.color[COLOR.BLUE] == 3

	t1.color[COLOR.RED] = 1100
	t1.color[COLOR.GREEN] = 1200
	with pytest.raises(TypeError):
		t1.color[COLOR.BLUE] = 1300
	assert t1.color[COLOR.RED] == 1100
	assert t1.color[COLOR.GREEN] == 1200
	assert t1.color[COLOR.BLUE] == 3
	assert t0.color[COLOR.RED] == 100
	assert t0.color[COLOR.GREEN] == 200
	assert t0.color[COLOR.BLUE] == 3

	t2 = MyTestClass('t2')
	assert t2.color[COLOR.RED] == 1
	assert t2.color[COLOR.GREEN] == 2
	assert t2.color[COLOR.BLUE] == 3

	exporter.load(FN_CONFIG)
	assert t0.color[COLOR.RED] == -1
	assert t0.color[COLOR.GREEN] == -2
	assert t0.color[COLOR.BLUE] == 3
	assert t1.color[COLOR.RED] == 11
	assert t1.color[COLOR.GREEN] == 12
	assert t1.color[COLOR.BLUE] == 3
	assert t2.color[COLOR.RED] == 1
	assert t2.color[COLOR.GREEN] == 2
	assert t2.color[COLOR.BLUE] == 3


def test_save_and_load_color(create_test_dir: None) -> None:
	class MyTestClass:
		color = urwid_colors.ColorConfig('mycolor', 'default')

	t = MyTestClass()
	assert t.color == 'mycolor'
	assert type(t).color.color.str_repr == 'default/default'

	type(t).color.parse_and_set_value(None, 'red/yellow')
	exporter.save(FN_CONFIG)
	assert t.color == 'mycolor'
	assert type(t).color.color.str_repr == 'red/yellow'

	type(t).color.parse_and_set_value(None, 'yellow/blue')
	assert t.color == 'mycolor'
	assert type(t).color.color.str_repr == 'yellow/blue'

	exporter.load(FN_CONFIG)
	assert t.color == 'mycolor'
	assert type(t).color.color.str_repr == 'red/yellow'

def test_save_and_load_color_str(create_test_dir: None) -> None:
	class MyTestClass:
		fmt = Config('fmt', urwid_colors.ColorStr('hello world'))

	t = MyTestClass()
	assert t.fmt == 'hello world'

	t.fmt = urwid_colors.ColorStr('<color=green>hello</color> <color=blue>world</color>')
	exporter.save(FN_CONFIG)
	assert t.fmt == '<color=green>hello</color> <color=blue>world</color>'

	t.fmt = urwid_colors.ColorStr('123')
	assert t.fmt == '123'

	exporter.load(FN_CONFIG)
	assert t.fmt == '<color=green>hello</color> <color=blue>world</color>'

def test_save_and_load_help_item(create_test_dir: None) -> None:
	CURSOR_LEFT = 'cursor left'
	CURSOR_RIGHT = 'cursor right'

	class MyTestClass:
		help_content = Config('fmt', [
			HelpItem(CURSOR_LEFT, 'left'),
			HelpItem(CURSOR_RIGHT, 'right'),
		])

	t = MyTestClass()
	exporter.save(FN_CONFIG)
	assert t.help_content == [
		HelpItem(CURSOR_LEFT, 'left'),
		HelpItem(CURSOR_RIGHT, 'right'),
	]

	t.help_content.clear()
	assert t.help_content == []

	exporter.load(FN_CONFIG)
	assert t.help_content == [
		HelpItem(CURSOR_LEFT, 'left'),
		HelpItem(CURSOR_RIGHT, 'right'),
	]

def test_save_and_load_command(create_test_dir: None) -> None:
	WC_PATH = '{path}'
	class MyTestClass:
		cmd = Config('cmd.file-browser', Command(['ranger', WC_PATH]))

	t = MyTestClass()
	exporter.save(FN_CONFIG)
	assert t.cmd == Command(['ranger', WC_PATH])

	t.cmd = Command(['xdg-open', WC_PATH])
	assert t.cmd == Command(['xdg-open', WC_PATH])

	exporter.load(FN_CONFIG)
	assert t.cmd == Command(['ranger', WC_PATH])

def test_command_dunder_methods() -> None:
	cmd = Command(['ranger', 'a dir'])
	assert len(cmd) == 2
	assert cmd[0] == 'ranger'
	assert cmd[1] == 'a dir'
	assert str(cmd) == "ranger 'a dir'"
	assert repr(cmd) == "Command(['ranger', 'a dir'])"

def test_save_and_load_command_with_alternatives(create_test_dir: None) -> None:
	WC_PATH = '{path}'
	class MyTestClass:
		cmd = Config('cmd.file-browser', CommandWithAlternatives([['ranger', WC_PATH], ['xdg-open', WC_PATH]]))

	t = MyTestClass()
	exporter.save(FN_CONFIG)
	assert repr(t.cmd) == repr(CommandWithAlternatives([['ranger', WC_PATH], ['xdg-open', WC_PATH]]))

	t.cmd = CommandWithAlternatives([['vim', WC_PATH]])
	assert repr(t.cmd) == repr(CommandWithAlternatives([['vim', WC_PATH]]))

	exporter.load(FN_CONFIG)
	assert repr(t.cmd) == repr(CommandWithAlternatives([['ranger', WC_PATH], ['xdg-open', WC_PATH]]))

def test_command_with_alternative_dunder_methods(monkeypatch: typing.Any) -> None:
	monkeypatch.setattr(shutil, 'which', lambda cmd: cmd == 'xdg-open')
	cmd = CommandWithAlternatives([Command(['ranger', 'a dir']), Command(['xdg-open', 'a dir']), Command(['vim', 'a dir'])])
	assert len(cmd) == 2
	assert cmd[0] == 'xdg-open'
	assert cmd[1] == 'a dir'
	assert str(cmd) == "ranger 'a dir'||xdg-open 'a dir'||vim 'a dir'"
	assert repr(cmd) == "CommandWithAlternatives([Command(['ranger', 'a dir']), Command(['xdg-open', 'a dir']), Command(['vim', 'a dir'])])"


# ------- config groups -------

def test__multi_config(create_test_dir: None) -> None:
	class MyTestClass:

		context_dependent_int = MultiConfig('context-dependent-int', 0)
		global_int = Config('global-int', 0)

		def __init__(self, config_id: ConfigId) -> None:
			self.config_id = config_id

	t1 = MyTestClass(ConfigId('foo'))
	t2 = MyTestClass(ConfigId('bar'))
	assert t1.context_dependent_int == 0
	assert t2.context_dependent_int == 0
	assert t1.global_int == 0
	assert t2.global_int == 0

	t1.context_dependent_int = 1
	t2.context_dependent_int = 2
	t1.global_int = -1
	t2.global_int = 42
	exporter.save(FN_CONFIG)
	assert t1.context_dependent_int == 1
	assert t2.context_dependent_int == 2
	assert t1.global_int == 42
	assert t2.global_int == 42

	t1.context_dependent_int = 10
	t2.context_dependent_int = 20
	t1.global_int = -2
	t2.global_int = 0xFF
	assert t1.context_dependent_int == 10
	assert t2.context_dependent_int == 20
	assert t1.global_int == 0xFF
	assert t2.global_int == 0xFF

	exporter.load(FN_CONFIG)
	assert t1.context_dependent_int == 1
	assert t2.context_dependent_int == 2
	assert t1.global_int == 42
	assert t2.global_int == 42

def test__multi_config_dict__set_defaults(create_test_dir: None) -> None:
	class MyTestClass:
		directions = MultiDictConfig('directions', {
			'new' : '>',
			'del' : '>',
			'dir' : '=',
		}, ignore_keys='dir')

		def __init__(self, config_id: str) -> None:
			self.config_id = ConfigId(config_id)

	assert MyTestClass.directions['new'] == '>'
	assert MyTestClass.directions['del'] == '>'
	assert MyTestClass.directions['dir'] == '='

	MyTestClass.directions['new'] = '<'
	assert MyTestClass.directions['new'] == '<'

	MyTestClass.directions['dir'] = '<'
	assert MyTestClass.directions['dir'] == '<'

	t1 = MyTestClass('t1')
	assert t1.directions['new'] == '<'
	assert t1.directions['dir'] == '<'

	t1.directions['new'] = '>'
	assert t1.directions['new'] == '>'
	assert MyTestClass.directions['new'] == '<'

	with pytest.raises(TypeError):
		t1.directions['dir'] = '>'
	assert t1.directions['dir'] == '<'
	assert MyTestClass.directions['dir'] == '<'

def test__multi_config_dict__load_defaults(create_test_dir: None) -> None:
	class MyTestClass:
		directions = MultiDictConfig('directions', {
			'new' : '>',
			'del' : '>',
			'dir' : '=',
		}, ignore_keys='dir')

		def __init__(self, config_id: str) -> None:
			self.config_id = ConfigId(config_id)

	assert MyTestClass.directions['new'] == '>'
	assert MyTestClass.directions['del'] == '>'
	assert MyTestClass.directions['dir'] == '='

	with open(FN_CONFIG, 'wt') as f:
		f.write('set directions.new = "<"')
	exporter.load(FN_CONFIG)
	assert MyTestClass.directions['new'] == '<'
	assert MyTestClass.directions['del'] == '>'
	assert MyTestClass.directions['dir'] == '='

	with open(FN_CONFIG, 'wt') as f:
		f.write('set directions.dir = "<"')
	with pytest.raises(ParseError):
		exporter.load(FN_CONFIG)
	assert MyTestClass.directions['new'] == '<'
	assert MyTestClass.directions['del'] == '>'
	assert MyTestClass.directions['dir'] == '='

	t1 = MyTestClass('t1')
	assert t1.directions['new'] == '<'
	assert t1.directions['del'] == '>'
	assert t1.directions['dir'] == '='


# ------- comments -------

def test_load_vim_comment(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 1)

	t = MyTestClass()
	assert t.a == 1

	with open(FN_CONFIG, 'wt') as f:
		f.write('"a = 2')
	exporter.load(FN_CONFIG)
	assert t.a == 1

def test_load_bash_comment(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 1)

	t = MyTestClass()
	assert t.a == 1

	with open(FN_CONFIG, 'wt') as f:
		f.write('#a = 2')
	exporter.load(FN_CONFIG)
	assert t.a == 1


# ------- errors -------

def test_load_invalid_color(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', COLOR.RED)

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a = yellow')

	with pytest.raises(ParseError, match=re.escape("invalid value for a: 'yellow' (should be one of red, green, blue)")):
		exporter.load(FN_CONFIG)

def test_load_forbidden_color(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', COLOR.GREEN, allowed_values=(COLOR.GREEN, COLOR.BLUE))

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a = red')

	with pytest.raises(ParseError, match=re.escape("invalid value for a: 'red' (should be one of green, blue)")):
		exporter.load(FN_CONFIG)

def test_load_forbidden_number_in_list(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', [1], allowed_values=(1, 2, 3, 4))

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a = 1,5')

	with pytest.raises(ParseError, match=re.escape("invalid value for a: '5' (should be one of 1, 2, 3, 4) while trying to parse line 1 'set a = 1,5'")):
		exporter.load(FN_CONFIG)

def test_load_forbidden_value_for_multi_dict_config(create_test_dir: None) -> None:
	class MyTestClass:

		a = MultiDictConfig('a', {
			1 : 'a',
			2 : 'b' ,
			3 : 'c' ,
		}, allowed_values='abc')

		def __init__(self, config_id: str) -> None:
			self.config_id = ConfigId(config_id)

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a.1=d')

	with pytest.raises(ParseError, match=re.escape("invalid value for a.1: 'd' (should be one of a, b, c)")):
		exporter.load(FN_CONFIG)

	t = MyTestClass('general')
	assert t.a[1] == 'a'
	assert t.a[2] == 'b'
	assert t.a[3] == 'c'

def test_continue_setting_after_error_on_same_line(create_test_dir: None) -> None:
	class MyTestClass:

		a = MultiDictConfig('a', {
			1 : 'a',
			2 : 'b' ,
			3 : 'c' ,
		}, allowed_values='abc')

		def __init__(self, config_id: str) -> None:
			self.config_id = ConfigId(config_id)

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a.1=d a.2=c')

	with pytest.raises(ParseError, match=re.escape("invalid value for a.1: 'd' (should be one of a, b, c)")):
		exporter.load(FN_CONFIG)

	t = MyTestClass('general')
	assert t.a[1] == 'a'
	assert t.a[2] == 'c'
	assert t.a[3] == 'c'

def test_load_invalid_int(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 1)

	with open(FN_CONFIG, 'wt') as f:
		f.write('set a = 1e3')

	with pytest.raises(ParseError, match=re.escape("invalid literal for int")):
		exporter.load(FN_CONFIG)

def test_load_invalid_key(create_test_dir: None) -> None:
	class MyTestClass:
		a = Config('a', 1)

	with open(FN_CONFIG, 'wt') as f:
		f.write('set b = true')

	with pytest.raises(ParseError, match=re.escape("invalid key 'b'")):
		exporter.load(FN_CONFIG)
