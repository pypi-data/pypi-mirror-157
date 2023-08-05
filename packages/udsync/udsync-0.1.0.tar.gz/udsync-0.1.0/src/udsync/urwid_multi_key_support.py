#!/usr/bin/env python3

import re
import shlex
import argparse
import abc
import typing

import urwid

from gettext import gettext as _

from .base_classes import Logger
from .config import Config
from .urwid_colors import ColorStr, ColorConfig, URWID_TYPE_MARKUP

URWID_TYPE_SIZE = typing.Union[typing.Tuple[int], typing.Tuple[int, int]]
URWID_TYPE_KEY = str
URWID_TYPE_WIDGET = typing.Any

CURSOR_MAX_UP = 'cursor max up'
CURSOR_MAX_DOWN = 'cursor max down'


class KeyMapper:

	KEY_ALL = '*'
	SEP_KEY = ''

	# ------- init -------

	def init_key_mapper(self, logger: Logger, command_map: 'SubCommandMap') -> None:
		self.logger = logger
		self._default_command_map = command_map

	# ------- splitting and joining keys -------

	keys_map: typing.Dict[URWID_TYPE_KEY, str] = {
		' ' : 'space',
		'<' : 'less',
		'>' : 'greater',
	}

	reo_split_keys = re.compile(r'<([^<>]+|<[^<>]+>)>|([^<>])')


	@classmethod
	def format_key(cls, key: URWID_TYPE_KEY) -> str:
		key = cls.keys_map.get(key, key)

		if len(key) == 1 and key != '?':
			return key
		else:
			return '<%s>' % key

	@classmethod
	def format_keys(cls, keys: typing.Sequence[URWID_TYPE_KEY]) -> str:
		return ''.join(cls.format_key(k) for k in keys)


	@classmethod
	def parse_keys(cls, key_names: str) -> typing.Sequence[URWID_TYPE_KEY]:
		out = [cls.parse_key(k) for k in cls.reo_split_keys.split(key_names) if k]
		assert len(out) >= 1
		return out

	@classmethod
	def parse_key(cls, key_name: str) -> URWID_TYPE_KEY:
		for i_urwid_key, i_key_name in cls.keys_map.items():
			if i_key_name == key_name:
				return i_urwid_key
		return key_name


	# ------- setters -------

	def bind_key(self, key_names: str, cmd: str) -> None:
		new = True
		keys = self.parse_keys(key_names)
		cmdmap = self._default_command_map

		for i in range(len(keys)-1):
			key = keys[i]
			val = cmdmap[key]
			if isinstance(val, SubCommandMap):
				cmdmap = val
			else:
				if val:
					self.logger.show_info(_('overwriting key mapping {oldkey} with {newkey}').format(oldkey=self.format_keys(keys[:i+1]), newkey=self.format_keys(keys)))
				new = False
				new_cmdmap = SubCommandMap()
				cmdmap[key] = new_cmdmap
				cmdmap = new_cmdmap

		key = keys[-1]
		val = cmdmap[key]
		if isinstance(val, SubCommandMap):
			n = len(tuple(self.iter_commands_unsorted(cmdmap)))
			self.logger.show_info(_('overwriting {n} key mapping(s) starting with {key}').format(n=n, key=self.format_keys(keys)))
		elif val:
			self.logger.show_info(_('overwriting key mapping {key}').format(key=self.format_keys(keys)))
		elif new:
			self.logger.show_info(_('defining new key mapping {key}').format(key=self.format_keys(keys)))

		cmdmap[key] = cmd

	def unbind_key(self, key_names: str) -> None:
		cmdmap = self._default_command_map

		if key_names == self.KEY_ALL:
			n = len(tuple(self.iter_commands_unsorted(cmdmap)))
			self.logger.show_info(_('removing all {n} key mappings').format(n=n))
			clear_commandmap(cmdmap)
			return

		keys = self.parse_keys(key_names)
		for key in keys[:-1]:
			val = cmdmap[key]
			if isinstance(val, SubCommandMap):
				cmdmap = val
			else:
				self.logger.show_error(_('{key} was not mapped').format(key=key_names))
				return

		key = keys[-1]
		val = cmdmap[key]
		if val is None:
			self.logger.show_error(_('{key} was not mapped').format(key=key_names))
			return

		if isinstance(val, SubCommandMap):
			cmdmap = val
			n = len(tuple(self.iter_commands_unsorted(cmdmap)))
			self.logger.show_info(_('removing all {n} key mappings starting with {key}').format(n=n, key=key_names))
		else:
			self.logger.show_info(_('unmapping {key}').format(key=key_names))
		del cmdmap[key]

	def mapclear(self) -> None:
		clear_commandmap(self._default_command_map)


	# ------- getters -------

	@classmethod
	def iter_commands(cls, command_map: 'SubCommandMap') -> typing.Iterable[typing.Tuple[str, str]]:
		return sorted(cls.iter_commands_unsorted(command_map), key=cls.sortkey_key_cmd)

	@classmethod
	def iter_commands_unsorted(cls, command_map: 'SubCommandMap') -> typing.Iterator[typing.Tuple[str, str]]:
		for urwid_key in iter_commandmap_keys(command_map):
			cmd = command_map[urwid_key]
			key_name = cls.format_key(urwid_key)
			if isinstance(cmd, SubCommandMap):
				for i_keys, i_cmd in cls.iter_commands_unsorted(cmd):
					i_keys = key_name + cls.SEP_KEY + i_keys
					yield i_keys, i_cmd
			else:
				assert cmd is not None
				yield key_name, cmd

	@classmethod
	def sortkey_key_cmd(cls, key_cmd: typing.Tuple[str, str]) -> str:
		return key_cmd[1]



class MultiKeySupport(KeyMapper):

	'''
	This class can be mixed into an urwid widget to implement commands
	which are triggered when a sequence of several keys is pressed.

	A child class must call

	* :meth:`MultiKeySupport.init_multi_key_support` in the constructor
	* :meth:`MultiKeySupport.waiting_for_next_key` at the beginning of :meth:`urwid.Widget.keypress` and return None if True is returned
	* :meth:`MultiKeySupport.reset_command_map` at the end of :meth:`urwid.Widget.keypress`

	A child class is expected to inherit :attr:`_command_map` from :class:`urwid.Widget`.

	|WARNING| Widgets which inherit from this class may *not* be nested.

	Example::

		class MyListBox(urwid.TreeListBox, MultiKeySupport):

			def __init__(self, app: App, tree_walker: urwid.TreeWalker) -> None:
				super().__init__(tree_walker)
				self.init_multi_key_support(app)
				self.app = app

				self._command_map['q'] = FUNC_QUIT
				self.bind_key('yps', FUNC_YANK_PATH_SRC)
				self.bind_key('ypd', FUNC_YANK_PATH_DST)
				self.replace_command(urwid.CURSOR_LEFT, FUNC_VIEW_COLLAPSE_PARENT)
				self.replace_command(urwid.CURSOR_RIGHT, FUNC_VIEW_EXPAND)

			def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
				if self.waiting_for_next_key(key):
					return None

				try:
					func = self._command_map[key]
					if func == FUNC_VIEW_COLLAPSE_PARENT:
						self.collapse_parent()
					elif func == FUNC_VIEW_EXPAND:
						self.set_expanded(True)
					elif func == FUNC_YANK_PATH_SRC:
						self.app.yank(self.focus.get_model().path_src)
					elif func == FUNC_YANK_PATH_DST:
						self.app.yank(self.focus.get_model().path_dst)
					elif func == FUNC_QUIT:
						self.app.quit()
					else:
						return typing.cast(typing.Optional[URWID_TYPE_KEY], self.__super.keypress(size, key))

					return None

				finally:
					self.reset_command_map()
	'''


	# ------- implementing methods used by urwid widgets -------

	_command_map: 'SubCommandMap'

	def init_multi_key_support(self, overlay_opener: 'OverlayPressedKeysOpener') -> None:
		self.init_key_mapper(overlay_opener, self._command_map)
		self._pressed_keys: typing.List[URWID_TYPE_KEY] = []
		self._overlay_opener = overlay_opener

	def waiting_for_next_key(self, key: URWID_TYPE_KEY) -> bool:
		cmd = self._command_map[key]
		if isinstance(cmd, SubCommandMap):
			if self._command_map is not self._default_command_map:
				self._overlay_opener.close_pressed_keys_overlay()
			self._command_map = cmd
			self._pressed_keys.append(key)
			self._overlay_opener.open_pressed_keys_overlay(self._pressed_keys, cmd)
			return True

		return False

	def reset_command_map(self) -> None:
		if self._command_map is self._default_command_map:
			return

		self._command_map = self._default_command_map
		self._pressed_keys = []
		self._overlay_opener.close_pressed_keys_overlay()


class SubCommandMap:

	implemented_commands: typing.Container[str]

	def __init__(self) -> None:
		self._command: typing.Dict[URWID_TYPE_KEY, typing.Union[str, 'SubCommandMap']] = {}

	def copy(self) -> 'SubCommandMap':
		out = SubCommandMap()
		out._command = self._command.copy()
		return out

	def __getitem__(self, key: URWID_TYPE_KEY) -> typing.Union[str, 'SubCommandMap', None]:
		return self._command.get(key)

	def __setitem__(self, key: URWID_TYPE_KEY, value: typing.Union[str, 'SubCommandMap']) -> None:
		self._command[key] = value

	def __delitem__(self, key: URWID_TYPE_KEY) -> None:
		del self._command[key]

	def __contains__(self, other: typing.Any) -> bool:
		# no infinite loop when trying `' ' in SubCommandMap()`
		# I am not implementing this method because urwid.CommandMap does not support it either
		raise NotImplementedError()

	def __iter__(self) -> typing.Iterator[URWID_TYPE_KEY]:
		# no infinite loop when trying to iterate over SubCommandMap
		# https://stackoverflow.com/q/26611554
		# I am not implementing this method because urwid.CommandMap does not support it either
		raise NotImplementedError()

	def __repr__(self) -> str:
		return '%s(%s)' % (type(self).__name__, self._command)


# I am not implementing these in SubCommandMap because they are for urwid.CommandMap, too

def iter_commandmap_keys(command_map: SubCommandMap) -> typing.KeysView[URWID_TYPE_KEY]:
	return command_map._command.keys()

def iter_commandmap_values(command_map: SubCommandMap) -> typing.ValuesView[typing.Union[str, SubCommandMap]]:
	return command_map._command.values()

def iter_commandmap_items(command_map: SubCommandMap) -> typing.ItemsView[URWID_TYPE_KEY, typing.Union[str, SubCommandMap]]:
	return command_map._command.items()

def clear_commandmap(command_map: SubCommandMap) -> None:
	return command_map._command.clear()

def replace_command(command_map: SubCommandMap, old_cmd: str, new_cmd: str) -> None:
	for key, val in iter_commandmap_items(command_map):
		if isinstance(val, SubCommandMap):
			replace_command(val, old_cmd, new_cmd)
		elif val == old_cmd:
			command_map[key] = new_cmd


# ========== config file ==========


class ParseException(Exception):
	pass

class ArgumentParser(argparse.ArgumentParser):

	def error(self, message: str) -> typing.NoReturn:
		raise ParseException(message)


class CommandMapExporter:

	COMMENT_PREFIXES = ('"', '#')

	MAP = ('map',)
	UNMAP = ('unmap', 'unm')
	CLEAR = ('mapclear', 'mapc')

	def __init__(self,
		logger: Logger,
		command_maps: typing.Union[typing.Dict[str, SubCommandMap], SubCommandMap],
		reference_command_map: SubCommandMap = SubCommandMap(),
	) -> None:
		self.logger = logger
		if not isinstance(command_maps, dict):
			command_maps = {'general' : command_maps}
		self.keymaps = {name:KeyMapper() for name in command_maps}
		for name in command_maps:
			self.keymaps[name].init_key_mapper(logger, command_maps[name])
		self.reference_command_map = reference_command_map

	# ------- load -------

	def load(self, fn: str) -> None:
		with open(fn, 'rt') as f:
			for lnno, ln in enumerate(f, 1):
				self.parse_line(ln, lnno, f.name)

	def parse_line(self, ln: str, lnno: typing.Optional[int] = None, fn: typing.Optional[str] = None) -> None:
		'''
		:param ln: The line to be parsed
		:param lnno: The number of the line, used in error messages
		:param fn: The full name of the file from which ln was read, used in error messages

		Calls :meth:`parse_error` if something goes wrong, e.g. too many arguments
		'''
		ln = ln.strip()
		if not ln:
			return
		if self.is_comment(ln):
			return

		ln_splitted = shlex.split(ln, comments=True)
		self.parse_splitted_line(ln_splitted, ln, lnno, fn)

	def parse_splitted_line(self, ln_splitted: typing.Sequence[str], ln: str, lnno: typing.Optional[int] = None, fn: typing.Optional[str] = None) -> None:
		cmd = ln_splitted[0]

		try:
			if cmd in self.MAP:
				self.map(ln_splitted)
			elif cmd in self.UNMAP:
				self.unmap(ln_splitted)
			elif cmd in self.CLEAR:
				self.mapclear(ln_splitted)
			else:
				self.unknown_command(ln_splitted, ln, lnno, fn)
		except ParseException as e:
			self.parse_error(str(e), ln, lnno)
			return

	def is_comment(self, ln: str) -> bool:
		for c in self.COMMENT_PREFIXES:
			if ln.startswith(c):
				return True
		return False


	def map(self, cmd: typing.Sequence[str]) -> None:
		p = ArgumentParser(cmd[0])
		p.add_argument('maps', nargs='?', type=KeyMapName(self.keymaps), default=KeyMapName.ALL)
		p.add_argument('key')
		p.add_argument('cmd')

		args = p.parse_args(cmd[1:])
		for map_name in args.maps:
			self.keymaps[map_name].bind_key(args.key, args.cmd)

	def unmap(self, cmd: typing.Sequence[str]) -> None:
		p = ArgumentParser(cmd[0])
		p.add_argument('maps', nargs='?', type=KeyMapName(self.keymaps), default=KeyMapName.ALL)
		p.add_argument('key')

		args = p.parse_args(cmd[1:])
		for map_name in args.maps:
			self.keymaps[map_name].unbind_key(args.key)

	def mapclear(self, cmd: typing.Sequence[str]) -> None:
		p = ArgumentParser(cmd[0])
		p.add_argument('maps', nargs='?', type=KeyMapName(self.keymaps), default=KeyMapName.ALL)

		args = p.parse_args(cmd[1:])
		for map_name in args.maps:
			self.keymaps[map_name].mapclear()

	def unknown_command(self, ln_splitted: typing.Sequence[str], ln: str, lnno: typing.Optional[int], fn: typing.Optional[str]) -> typing.Optional[typing.NoReturn]:
		raise ParseException('unkown command %r' % ln_splitted[0])


	# ------- save -------

	def save(self, fn: str) -> None:
		'''
		Save the current key mappings to a file.

		:param fn: The name of the file to write to
		'''
		with open(fn, 'wt') as f:
			self.save_to_open_file(f)

	def save_to_open_file(self, f: typing.TextIO) -> None:
		clear_pattern = self.CLEAR[0] + '\n'
		map_pattern = self.MAP[0] + ' {key}\t{cmd}\n'
		specific_map_pattern = self.MAP[0] + ' {map_name} {key}\t{cmd}\n'
		specific_unmap_pattern = self.UNMAP[0] + ' {map_name} {key}\n'
		n = '\n'

		f.write(clear_pattern)

		keys_defined_for_all = dict(KeyMapper.iter_commands_unsorted(self.reference_command_map))
		keys_defined_for_all.update(self.keys_with_same_commands())
		for key, cmd in sorted(keys_defined_for_all.items(), key=KeyMapper.sortkey_key_cmd):
			ln = map_pattern.format(key=shlex.quote(key), cmd=shlex.quote(cmd))
			f.write(n + ln)
			n = ''

		for map_name, keymapper in self.keymaps.items():
			n = '\n'
			keys_to_be_unbound = list(keys_defined_for_all.keys())
			for key, cmd in keymapper.iter_commands(keymapper._default_command_map):
				try:
					keys_to_be_unbound.remove(key)
				except ValueError:
					pass
				if keys_defined_for_all.get(key, None) == cmd:
					continue
				ln = specific_map_pattern.format(map_name=map_name, key=shlex.quote(key), cmd=shlex.quote(cmd))
				f.write(n + ln)
				n = ''

			for key in keys_to_be_unbound:
				ln = specific_unmap_pattern.format(map_name=map_name, key=shlex.quote(key))
				f.write(n + ln)
				n = ''

	def keys_with_same_commands(self) -> typing.Mapping[str, str]:
		s_s_key_cmd = [tuple(keymapper.iter_commands(keymapper._default_command_map)) for keymapper in self.keymaps.values()]
		keys_defined_in_all_maps = set.intersection(*(set(key for key, cmd in s_key_cmd) for s_key_cmd in s_s_key_cmd))

		keys_equal_in_all_maps = {key:cmd for key, cmd in s_s_key_cmd[0] if key in keys_defined_in_all_maps}
		for s_key_cmd in s_s_key_cmd[1:]:
			for key, cmd in s_key_cmd:
				_cmd = keys_equal_in_all_maps.get(key, None)
				if _cmd is not None and _cmd != cmd:
					del keys_equal_in_all_maps[key]

		return keys_equal_in_all_maps


	# ------- error handling -------

	def parse_error(self, msg: str, ln: str, lnno: typing.Optional[int]) -> None:
		'''
		Is called if something went wrong while trying to load a key mappings file.
		This method compiles the given information into an error message and calls :meth:`Logger.show_error`.

		:param msg: The error message
		:param ln: The line where the error occured
		:param lnno: The number of the line
		'''
		if lnno is not None:
			lnref = 'line %s' % lnno
		else:
			lnref = 'line'
		msg +=  f' while trying to parse {lnref} {ln!r}'
		self.logger.show_error(msg)

class KeyMapName:

	SEP = ','
	ALL = 'all'

	def __init__(self, map_names: typing.Iterable[str]) -> None:
		self.map_names = tuple(map_names)

	def __call__(self, map_names: str) -> typing.Sequence[str]:
		if map_names == self.ALL:
			return self.map_names

		out = []
		for name in map_names.split(self.SEP):
			if name not in self.map_names:
				raise ValueError('{name} is not a valid key map name, should be one of {allowed_values}'.format(
					name = name, allowed_values = ', '.join(n for n in self.map_names + (self.ALL,))))
			out.append(name)

		return out


# ========== overlay widget ==========

class OverlayPressedKeysOpener(Logger):

	@abc.abstractmethod
	def open_pressed_keys_overlay(self, keys: typing.Sequence[URWID_TYPE_KEY], command_map: SubCommandMap) -> None:
		raise NotImplementedError()

	@abc.abstractmethod
	def close_pressed_keys_overlay(self) -> None:
		raise NotImplementedError()


class OverlayPressedKeys(urwid.Overlay):

	BORDER_LEFT = 0
	BORDER_RIGHT = 3
	BORDER_TOP = 1


	class BgContainer(urwid.WidgetWrap):

		def __init__(self, master: urwid.Widget, widget: urwid.Widget) -> None:
			self.master = master
			super().__init__(widget)

		def render(self, size: typing.Tuple[int, ...], focus: bool = False) -> urwid.Canvas:
			return self._w.render(size, self.master.is_focused)


	def __init__(self, bg_widget: urwid.Widget, pressed_keys: typing.Sequence[URWID_TYPE_KEY], command_map: SubCommandMap, *, title: typing.Optional[str] = None) -> None:
		self.bg_widget = bg_widget
		# I can set the OverlayPressedKeysOpener to None because the listbox does not receive any keypresses, this widget forwards them all to bg_widget
		self.listbox = PressedKeysWidget(None, pressed_keys, command_map, title=title)  # type: ignore [arg-type]

		header = urwid.Text('')
		self.frame = urwid.Frame(self.listbox, header=header)
		self.fg_widget = urwid.Padding(self.frame, left=self.BORDER_LEFT, right=self.BORDER_RIGHT)

		kw = {
			'align': urwid.LEFT,
			'valign': urwid.BOTTOM,
			'width': self.get_width(),
			'height': self.get_height(),
		}

		bottom_w = self.BgContainer(self, self.bg_widget)
		super().__init__(self.fg_widget, bottom_w, **kw)

	def get_width(self) -> int:
		out = self.listbox.get_width()
		out += self.BORDER_LEFT + self.BORDER_RIGHT
		return out

	def get_height(self) -> int:
		out = self.listbox.get_height()
		out += self.BORDER_TOP
		return out

	def keypress(self, size: typing.Tuple[int, ...], key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		return typing.cast(typing.Optional[URWID_TYPE_KEY], self.bg_widget.keypress(size, key))

	def render(self, size: typing.Tuple[int, ...], focus: bool = False) -> urwid.Canvas:
		self.is_focused = focus
		return super().render(size, focus)


class ExtendedListBox(urwid.ListBox, MultiKeySupport):

	ELLIPSIS = _('...')

	color_title = ColorConfig('help.color.list.title', 'default,bold')
	color_ellipsis = ColorConfig('help.color.list.ellipsis', 'default')

	def __init__(self, pressed_keys_opener: OverlayPressedKeysOpener, widgets: typing.Sequence[urwid.Widget]) -> None:
		self.ellipsis_widget = urwid.Text((self.color_ellipsis, self.ELLIPSIS), align=urwid.CENTER)
		self.key_handler: typing.Optional[typing.Callable[[URWID_TYPE_SIZE, URWID_TYPE_KEY], typing.Optional[URWID_TYPE_KEY]]] = None

		body = urwid.SimpleFocusListWalker(widgets)
		super().__init__(body)
		self.init_multi_key_support(pressed_keys_opener)

	def set_key_handler(self, callback: typing.Callable[[URWID_TYPE_SIZE, URWID_TYPE_KEY], typing.Optional[URWID_TYPE_KEY]]) -> None:
		self.key_handler = callback


	# ------- keypress -------

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if self.waiting_for_next_key(key):
			return None

		if self.key_handler is not None and self.key_handler(size, key) is None:
			self.reset_command_map()
			return None

		func = self._command_map[key]
		if func == CURSOR_MAX_UP:
			self.set_focus(0)
		elif func == CURSOR_MAX_DOWN:
			self.set_focus(len(self.body)-1)
		else:
			self.reset_command_map()
			return typing.cast(typing.Optional[URWID_TYPE_KEY], self.__super.keypress(size, key))

		self.reset_command_map()
		return None


	# ------- render -------

	def render(self, size: typing.Tuple[int, ...], focus: bool = False) -> urwid.Canvas:
		bottom_canvas = super().render(size, focus)

		middle, top, bottom = self.calculate_visible(size)
		assert len(top[1]) == middle[0]

		number_invisible_lines_above = middle[2] - middle[0]
		assert not number_invisible_lines_above < 0
		if number_invisible_lines_above > 0:
			top_canvas = self.ellipsis_widget.render((size[0],))
			top_canvas = urwid.CompositeCanvas(top_canvas)
			left = 0
			top = 0
			bottom_canvas = urwid.CanvasOverlay(top_canvas, bottom_canvas, left, top)

		number_invisible_lines_below = len(self.body) - 1 - (middle[2] + len(bottom[1]))
		assert not number_invisible_lines_below < 0
		if number_invisible_lines_below > 0:
			top_canvas = self.ellipsis_widget.render((size[0],))
			top_canvas = urwid.CompositeCanvas(top_canvas)
			left = 0
			top = size[1] - 1
			bottom_canvas = urwid.CanvasOverlay(top_canvas, bottom_canvas, left, top)

		return bottom_canvas


class PressedKeysWidget(ExtendedListBox):

	MAX_WIDTH = 40

	def __init__(self, pressed_keys_opener: OverlayPressedKeysOpener, pressed_keys: typing.Sequence[URWID_TYPE_KEY], command_map: 'SubCommandMap', *, title: typing.Optional[str] = None) -> None:
		widgets = []
		if title:
			widgets.append(urwid.Text((self.color_title, title)))

		key_cmd_list = KeyMapper.iter_commands(command_map)
		max_key_width = max(len(key_cmd[0]) for key_cmd in key_cmd_list)
		prefix = MultiKeySupport.format_keys(pressed_keys)
		n_pressed_keys = len(prefix)
		for keys, cmd in key_cmd_list:
			keys = prefix + keys
			widgets.append(PressedKeysLineWidget(keys, cmd, max_key_width=max_key_width, n_pressed_keys=n_pressed_keys))

		super().__init__(pressed_keys_opener, widgets)
		self._size = self.calc_size()


	# ------- size -------

	def calc_size(self) -> typing.Tuple[int, int]:
		if self.MAX_WIDTH:
			max_width = self.MAX_WIDTH
		else:
			max_width = self.app.screen.get_cols_rows()[0]

		width, height = 0, 0
		for widget in self.body:
			line_width, line_height = self.measure_text_size(widget, max_width)
			if line_width > width:
				width = line_width
			height += line_height

		return width, height

	@staticmethod
	def measure_text_size(text_widget: urwid.Text, max_width: int) -> typing.Tuple[int, int]:
		'''
		Calculate the size of a Text widget.
		Text.pack is similar but ignores indentation, see urwid.text_layout.line_width.
		'''
		layout_struct = text_widget.base_widget.get_line_translation(max_width)
		height = len(layout_struct)
		width = typing.cast(int, max(sum(seg[0] for seg in ln) for ln in layout_struct))
		return width, height

	def get_height(self) -> int:
		return self._size[1]

	def get_width(self) -> int:
		return self._size[0]


class PressedKeysLineWidget(urwid.Text):

	SEP = ' '

	color_key = ColorConfig('help.color.key', 'red')
	color_key_pressed = ColorConfig('help.color.key.pressed', 'default')
	color_cmd = ColorConfig('help.color.cmd', 'blue')

	def __init__(self, key: str, cmd: str, *, max_key_width: int, n_pressed_keys: typing.Optional[int] = None) -> None:
		markup: typing.List[typing.Union[typing.Tuple[str, str], str]] = []
		key_width = len(key)
		align = ' ' * (max_key_width - key_width)
		if n_pressed_keys:
			markup.append((self.color_key_pressed, key[:n_pressed_keys]))
			key = key[n_pressed_keys:]
		markup.append((self.color_key, key))
		markup.append(align)
		markup.append(self.SEP)
		markup.append((self.color_cmd, cmd))
		super().__init__(markup)


# ========== help bar ==========

class HelpItem:

	type_name = "'help text: command' or 'help text: <key>'"
	type_article = None

	SEP = ': '

	def __init__(self, cmd: str, name: typing.Optional[str] = None) -> None:
		'''
		:param cmd: the command for which you want to show the keyboard shortcuts.
		            Alternatively, if you want to show a group of keyboard shortcuts,
		            the start key(s) with which all shortcuts begin wrapped in angular braces
		            in a syntax which is understood by :meth:`KeyMapper.parse_keys`.
		            If this is the only argument given it is the string representation of a HelpItem
		            as returned by :meth:`__str__`.
		:param name: one or two words to describe what cmd does.
		'''
		if name is None:
			# parsing value from config file
			name, cmd = cmd.split(self.SEP, 1)

		self.cmd = cmd
		self.name = name

	def __str__(self) -> str:
		return self.name + self.SEP + self.cmd

	def __eq__(self, other: typing.Any) -> bool:
		if isinstance(other, HelpItem):
			return self.cmd == other.cmd and self.name == other.name
		return NotImplemented


class HelpBar(urwid.WidgetWrap):

	bg = 'bright black'
	col = ColorConfig('help-bar.color', f'default/{bg}')
	fmt = Config('help-bar.fmt', ColorStr(f'<color=red/{bg}>{{key}} </color><color=default/{bg}>{{cmd}}</color>'),
		help='how to format a key/command pair in a help bar. Supports the wild cards {{key}} and {{cmd}}.')
	sep = Config('help-bar.sep', ColorStr(f'<color=black/{bg}> │ </color>'),
		help='the separator which is placed between two key/commands pairs. See also %help-bar.fmt%.')
	key_sep = Config('help-bar.key-sep', ColorStr(f'<color=default/{bg}>/</color>'),
		help='the separator which is placed between two key mappings for the same command when replacing the {{key}} wildcard in %help-bar.fmt%')
	unmapped_commands_are_errors = Config('help-bar.show-error-for-unmapped-commands', True)

	def __init__(self, content: typing.Sequence[HelpItem], command_map: SubCommandMap, logger: Logger, *, edit_context: bool) -> None:
		'''
		the arguments are passed through to :meth:`set_help`
		'''
		self.logger = logger
		self.text = urwid.Text('')
		widget = urwid.Padding(self.text)
		widget = urwid.AttrMap(widget, self.col)
		super().__init__(widget)
		self.set_help(content, command_map, edit_context=edit_context)

	def set_help(self, content: typing.Sequence[HelpItem], command_map: SubCommandMap, *, edit_context: bool) -> None:
		'''
		:param edit_context: an Edit like widget is focused where characters are inserted instead of triggering a command
		'''
		all_key_mappings = list(KeyMapper.iter_commands(command_map))
		markup: URWID_TYPE_MARKUP = []
		sep = ColorStr.to_markup(self.sep)
		for help_item in content:
			if help_item.cmd.startswith('<'):
				if not self.is_key_mapped(help_item.cmd, command_map):
					keys = []
					if self.unmapped_commands_are_errors:
						self.logger.show_error('no commands are mapped to the key %s' % help_item.cmd)
				else:
					keys = [KeyMapper.format_keys(KeyMapper.parse_keys(help_item.cmd))]
			else:
				keys = [key for key, cmd in all_key_mappings if cmd == help_item.cmd and (not edit_context or self.is_key_usable_in_edit_context(key))]
				if self.unmapped_commands_are_errors and not keys:
					self.logger.show_error('no keys are mapped to the command %r' % help_item.cmd)
			if not keys:
				continue
			if markup:
				markup.append(sep)
			markup.append(ColorStr.to_markup(self.fmt, format=dict(key=self.key_sep.join(keys), cmd=help_item.name), values_are_color_str=True))
		self.text.set_text(markup)

	@staticmethod
	def is_key_mapped(key: str, command_map: SubCommandMap) -> bool:
		keys = KeyMapper.parse_keys(key)
		for k in keys[:-1]:
			mapped = command_map[k]
			if mapped is None:
				return False
			if isinstance(mapped, str):
				return False
			command_map = mapped

		k = keys[-1]
		mapped = command_map[k]
		return mapped is not None

	def is_key_usable_in_edit_context(self, key: str) -> bool:
		keys = KeyMapper.parse_keys(key)
		key0 = keys[0]
		if len(key0) > 1:
			return True
		return False
