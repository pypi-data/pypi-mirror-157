#!/usr/bin/env pytest

import pytest
import typing

from udsync.config import Config, MultiConfig
from udsync.urwid_colors import Color, ColorConfig, ColorStr


class COLOR:

	# ------- foreground -------

	FG_DEFAULT       = 'default'

	FG_BLACK         = 'black'
	FG_RED           = 'dark red'
	FG_GREEN         = 'dark green'
	FG_YELLOW        = 'brown'
	FG_BLUE          = 'dark blue'
	FG_MAGENTA       = 'dark magenta'
	FG_CYAN          = 'dark cyan'
	FG_WHITE         = 'light gray'

	FG_BRIGHT_BLACK   = 'dark gray'
	FG_BRIGHT_RED     = 'light red'
	FG_BRIGHT_GREEN   = 'light green'
	FG_BRIGHT_YELLOW  = 'yellow'
	FG_BRIGHT_BLUE    = 'light blue'
	FG_BRIGHT_MAGENTA = 'light magenta'
	FG_BRIGHT_CYAN    = 'light cyan'
	FG_BRIGHT_WHITE   = 'white'


	# ------- background -------

	BG_DEFAULT = 'default'

	BG_BLACK   = 'black'
	BG_RED     = 'dark red'
	BG_GREEN   = 'dark green'
	BG_YELLOW  = 'brown'
	BG_BLUE    = 'dark blue'
	BG_MAGENTA = 'dark magenta'
	BG_CYAN    = 'dark cyan'
	BG_WHITE   = 'light gray'

	BG_BRIGHT_BLACK   = 'dark gray'
	BG_BRIGHT_RED     = 'light red'
	BG_BRIGHT_GREEN   = 'light green'
	BG_BRIGHT_YELLOW  = 'yellow'
	BG_BRIGHT_BLUE    = 'light blue'
	BG_BRIGHT_MAGENTA = 'light magenta'
	BG_BRIGHT_CYAN    = 'light cyan'
	BG_BRIGHT_WHITE   = 'white'

class EMPH:

	'''usage: COLOR.FG_* + EMPH.BOLD'''

	BOLD      = ',bold'
	UNDERLINE = ',underline'
	STANDOUT  = ',standout'


@pytest.fixture(autouse=True)
def reset_config() -> None:
	Config.instances.clear()
	MultiConfig.config_ids.clear()
	ColorConfig.color_configs.clear()


# ------- Color -------

def test__fg_color_only() -> None:
	assert Color('yellow').to_palette_tuple() == ('yellow/default', COLOR.FG_YELLOW, COLOR.BG_DEFAULT)
	assert Color('default').to_palette_tuple() == ('default/default', COLOR.FG_DEFAULT, COLOR.BG_DEFAULT)

def test__fg_color_and_emph() -> None:
	assert Color('yellow,standout').to_palette_tuple() == ('yellow,standout/default', COLOR.FG_YELLOW + EMPH.STANDOUT, COLOR.BG_DEFAULT)

def test__fg_color_and_two_emph() -> None:
	assert Color('yellow,bold,underline').to_palette_tuple() == ('yellow,bold,underline/default', COLOR.FG_YELLOW + EMPH.BOLD + EMPH.UNDERLINE, COLOR.BG_DEFAULT)

def test__fg_bg() -> None:
	assert Color('black/white').to_palette_tuple() == ('black/white', COLOR.FG_BLACK, COLOR.BG_WHITE)
	assert Color('cyan/default').to_palette_tuple() == ('cyan/default', COLOR.FG_CYAN, COLOR.BG_DEFAULT)

def test__fg_emph_bg() -> None:
	assert Color('red,bold/yellow').to_palette_tuple() == ('red,bold/yellow', COLOR.FG_RED + EMPH.BOLD, COLOR.BG_YELLOW)

def test__specific_attr_name() -> None:
	assert Color('blue', attr_name='myattr').to_palette_tuple() == ('myattr', COLOR.FG_BLUE, COLOR.BG_DEFAULT)


def test__recreate_color() -> None:
	c1 = Color('magenta,strikethrough/green')
	c2 = Color(str(c1))
	assert c1.str_repr == c2.str_repr
	assert c1.fg == c2.fg
	assert c1.bg == c2.bg


# ------- ColorConfig -------

def test__reference__full() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green')
		cr = ColorConfig('color.ref', '{color.original}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.fg
	assert cr.bg == co.bg
	assert cr.str_repr == co.str_repr

def test__reference__implicit_fg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green')
		cr = ColorConfig('color.ref', '{color.original}/blue')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.fg
	assert cr.bg == COLOR.BG_BLUE

def test__reference__implicit_bg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green/blue')
		cr = ColorConfig('color.ref', 'yellow/{color.original}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == COLOR.FG_YELLOW
	assert cr.bg == co.bg

def test__reference__fg_only() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green/yellow')
		cr = ColorConfig('color.ref', '{color.original.fg}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.fg
	assert cr.bg == COLOR.BG_DEFAULT

def test__reference__fg_as_bg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green/yellow')
		cr = ColorConfig('color.ref', 'default/{color.original.fg}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == COLOR.FG_DEFAULT
	assert cr.bg == co.fg

def test__reference__bg_as_fg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green/yellow')
		cr = ColorConfig('color.ref', '{color.original.bg}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.bg
	assert cr.bg == COLOR.BG_DEFAULT

def test__reference__swap_fg_bg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'default')
		co = ColorConfig('color.original', 'magenta/cyan')
		cr = ColorConfig('color.ref', '{color.original.bg}/{color.original.fg}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.bg
	assert cr.bg == co.fg

def test__reference__mix_colors() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'default')
		co1 = ColorConfig('color.original-1', 'magenta/cyan')
		co2 = ColorConfig('color.original-2', 'yellow/blue')
		cr1 = ColorConfig('color.ref-1', '{color.original-1.fg}/{color.original-2.bg}')
		cr2 = ColorConfig('color.ref-2', '{color.original-2.fg}/{color.original-1.bg}')

	co1 = Test.co1.color
	co2 = Test.co2.color
	cr1 = Test.cr1.color
	cr2 = Test.cr2.color

	assert cr1.fg == co1.fg
	assert cr1.bg == co2.bg
	assert cr2.fg == co2.fg
	assert cr2.bg == co1.bg


# ------- invalid Color -------

def test__invalid_fg() -> None:
	with pytest.raises(ValueError):
		Color('not existing color')

def test__invalid_emph() -> None:
	with pytest.raises(ValueError):
		Color('default,bold,invalid/default')

def test__invalid_bg() -> None:
	with pytest.raises(ValueError):
		Color('yellow/invalid')


# ------- Color.standout() -------

def test_emphasize() -> None:
	assert Color('default').standout() == 'default,standout/default'
	assert Color('yellow/red').standout() == 'yellow,standout/red'

def test_emphasize_config() -> None:
	class TitleWidget:
		color_title = ColorConfig('color.title', 'yellow/cyan')
		color_title_focus = color_title.focus

	w = TitleWidget()
	assert w.color_title == 'color.title'
	assert w.color_title_focus == 'color.title-focus'

	assert type(w).color_title.color.fg == COLOR.FG_YELLOW
	assert type(w).color_title.color.bg == COLOR.BG_CYAN
	assert type(w).color_title_focus.color.fg == COLOR.FG_YELLOW + EMPH.STANDOUT
	assert type(w).color_title_focus.color.bg == COLOR.BG_CYAN


# ------- ColorStr -------

@pytest.fixture
def registered_colors() -> typing.Set[str]:
	out = set()
	ColorStr.set_register_color(lambda c: out.add(c.str_repr))
	return out

def test_colored_str_to_markup_empty(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('') == ''
	assert set() == registered_colors

def test_colored_str_to_markup_str(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('abc') == 'abc'
	assert set() == registered_colors

def test_colored_str_to_markup_one_color(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('hello <color=red>world</color>') == ['hello ', ('red/default', 'world')]
	assert {'red/default'} == registered_colors

def test_colored_str_to_markup_nested_colors(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('<color=green>hello <color=red>world</color></color>') == ('green/default', ['hello ', ('red/default', 'world')])
	assert {'green/default', 'red/default'} == registered_colors

def test_colored_str_to_markup_chained_colors(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('a<color=yellow>b<color=red>c</color>d<color=green>e</color>f</color>g') == ['a', ('yellow/default', ['b', ('red/default', 'c'), 'd', ('green/default', 'e'), 'f']), 'g']
	assert {'yellow/default', 'red/default', 'green/default'} == registered_colors

def test_colored_str_to_markup_missing_closing_tag(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('hello <color=red>world') == ['hello ', ('red/default', 'world')]
	assert {'red/default'} == registered_colors

def test_colored_str_to_markup_missing_two_closing_tags(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('<color=red>hello <color=green>world') == ('red/default', ['hello ', ('green/default', 'world')])
	assert {'red/default', 'green/default'} == registered_colors

def test_colored_str_to_markup_reference_other_color(registered_colors: typing.Set[str]) -> None:
	ColorConfig('title', 'black/yellow')
	assert ColorStr.to_markup('<color=red>hello <color={title}>world') == ('red/default', ['hello ', ('black/yellow', 'world')])
	assert {'black/yellow', 'red/default'} == registered_colors

def test_colored_str_to_markup_with_format(registered_colors: typing.Set[str]) -> None:
	ColorConfig('O', 'black')
	ColorConfig('I', 'red')
	ColorConfig('II', 'green')
	assert ColorStr.to_markup('{O}<color={I}>{I}<color={II}>{II}</color>{I}', format={'O':'blk', 'I':'red', 'II':'grn'}) == ['blk', ('red/default', ['red', ('green/default', 'grn'), 'red'])]
	assert {'red/default', 'green/default'} == registered_colors

def test_colored_str_to_markup_with_format_where_values_are_color_str(registered_colors: typing.Set[str]) -> None:
	ColorConfig('O', 'black')
	ColorConfig('I', 'red')
	ColorConfig('II', 'green')
	assert ColorStr.to_markup('{O}<color={I}>{I}<color={II}>{II}</color>{I}', format={'O':'blk', 'I':'r<color=default/red>e</color>d', 'II':'g<color=default/green>r</color>n'}, values_are_color_str=True) \
		== ['blk', ('red/default', [['r', ('default/red', 'e'), 'd'], ('green/default', ['g', ('default/green', 'r'), 'n']), ['r', ('default/red', 'e'), 'd']])]
	assert {'red/default', 'green/default', 'default/red', 'default/green'} == registered_colors


# ------- simplify_markup -------

def test_simplify_markup__empty_str() -> None:
	ColorStr.simplify_markup('') == ''

def test_simplify_markup__nested_empty_lists() -> None:
	ColorStr.simplify_markup([[[]]]) == ''

def test_simplify_markup__nested_and_listed_lists() -> None:
	ColorStr.simplify_markup(['a', ['b'], ['c', 'd']]) == ['abcd']

def test_simplify_markup__tuples() -> None:
	ColorStr.simplify_markup(['a', [('red', 'b')], [('green', 'c'), 'd']]) == ['a', ('red', 'b'), ('green', 'c'), 'd']
