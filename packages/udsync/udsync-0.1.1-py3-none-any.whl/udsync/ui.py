#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import re
import time
import contextlib
import threading
import pkgutil
import enum
import typing

import urwid
import urwid_timed_progress

from . import urwid_multi_key_support

QUIT = 'quit'
CONFIG = 'config'
HELP_LIST_OF_KEY_MAPPINGS = 'help key-mappings'
HELP_LIST_OF_COMMANDS = 'help commands'
HELP_CONFIG = 'help config'

urwid.command_map['j'] = urwid.CURSOR_DOWN
urwid.command_map['k'] = urwid.CURSOR_UP
urwid.command_map['h'] = urwid.CURSOR_LEFT
urwid.command_map['l'] = urwid.CURSOR_RIGHT
urwid.command_map['p'] = CONFIG
urwid.command_map['f1'] = HELP_LIST_OF_KEY_MAPPINGS
urwid.command_map['f2'] = HELP_LIST_OF_KEY_MAPPINGS
urwid.command_map['f3'] = HELP_LIST_OF_COMMANDS
urwid.command_map['f4'] = HELP_CONFIG
urwid.command_map['q'] = QUIT


from . import urwid_dialog
from . import urwid_directory_chooser
from . import urwid_colors

from . import model
from .config import Config, DictConfig, ConfigTrackingChanges, MultiConfig, ConfigId, Path, CommandWithAlternatives, SortedEnum
from . import configfile
from . import lsblk
from . import clipboard
from .subprocess_pipe import run_and_pipe
from . import base_classes

CANCEL = urwid_dialog.CANCEL
CURSOR_MAX_UP = urwid_directory_chooser.CURSOR_MAX_UP
CURSOR_MAX_DOWN = urwid_directory_chooser.CURSOR_MAX_DOWN

urwid.command_map.implemented_commands = {
	urwid.CURSOR_LEFT,
	urwid.CURSOR_RIGHT,
	urwid.CURSOR_MAX_LEFT,
	urwid.CURSOR_MAX_RIGHT,
	urwid.CURSOR_UP,
	urwid.CURSOR_DOWN,
	urwid.CURSOR_PAGE_UP,
	urwid.CURSOR_PAGE_DOWN,
	CURSOR_MAX_UP,
	CURSOR_MAX_DOWN,
	urwid_dialog.NEXT_SELECTABLE,
	urwid_dialog.PREV_SELECTABLE,
	urwid.ACTIVATE,
	CANCEL,
	QUIT,
	CONFIG,
	HELP_LIST_OF_KEY_MAPPINGS,
	HELP_LIST_OF_COMMANDS,
	HELP_CONFIG,
}

URWID_TYPE_SIZE = typing.Union[typing.Tuple[int], typing.Tuple[int, int]]
URWID_TYPE_KEY = str
URWID_TYPE_ATTR = str


FUNC_NODE_TOGGLE_IGNORE = 'node.toggle_ignore'
FUNC_NODE_TOGGLE_DIRECTION = 'node.toggle_direction'
FUNC_NODE_SET_DIRECTION_SRC_TO_DST = 'node.set_direction(SRC_TO_DST)'
FUNC_NODE_SET_DIRECTION_DST_TO_SRC = 'node.set_direction(DST_TO_SRC)'
FUNC_NODE_UPDATE = 'node.update'
FUNC_VIEW_EXPAND = 'view.expand'
FUNC_VIEW_COLLAPSE = 'view.collapse'
FUNC_VIEW_COLLAPSE_PARENT = 'view.collapse_parent'
FUNC_YANK_PATH_SRC = 'yank.src'
FUNC_YANK_PATH_DST = 'yank.dst'
FUNC_OPEN_SRC = 'open src'
FUNC_OPEN_DST = 'open dst'
FUNC_DIFF = 'diff'


ERROR_FAILED_TO_MOUNT_DEVICE = 1


def is_installed(cmd: str) -> bool:
	return bool(shutil.which(cmd))


@enum.unique
class LOG_LEVEL(SortedEnum):
	INFO = 'info'
	WARNING = 'warning'
	ERROR = 'error'



pattern_seconds = Config('time-formatter.pattern.seconds', '{s:.2f}s')
pattern_minutes = Config('time-formatter.pattern.minutes', '{m}:{s:02d}min')
pattern_hours = Config('time-formatter.pattern.hours', '{h}:{m:02d}h')
def time_difference_to_str(seconds: float) -> str:
	s = int(seconds)
	m = s // 60
	if m == 0:
		return pattern_seconds.value.format(s=seconds)
	s %= 60
	h = m // 60
	if h == 0:
		return pattern_minutes.value.format(s=s, m=m)
	m %= 60
	return pattern_hours.value.format(s=s, m=m, h=h)


class App(urwid_directory_chooser.App):

	resource_help_config = 'doc/config.md'

	DIR_BACKUP_PLANS = 'backup-plans'

	handle_mouse = Config('urwid.handle-mouse', False, help={True: 'urwid intercepts mouse events so you cannot select and copy text as usual', False: 'this behaves like a normal terminal application'})

	default_backup_plan = Config('default-backup-plan', 'default', help='the name of the default backup plan to be loaded if no command line arguments are given')
	path_src = MultiConfig('path.src', Path(''), help='the source path to be used if no path is given on the command line')
	path_dst = MultiConfig('path.dst', Path(''), help='the destination path to be used if no path is given on the command line')

	should_ask_to_create_backup_plan = Config('ask-to-create-backup-plan', True, help='ask if the backup plan should be created if a not existing backup plan is passed as command line argument')

	log_level = ConfigTrackingChanges('status.level', LOG_LEVEL.INFO)

	color_error = urwid_colors.ColorConfig('status.color.error', 'red')
	color_info = urwid_colors.ColorConfig('status.color.info', 'default')

	progress_bar_update_time = Config('progress-bar.update-time', 0.5, help='number of seconds between two updates of the progress bar')
	time_before_opening_loading_screen = Config('time-before-opening-progress-bar', 1, help='wait time before opening the progress bar to avoid an unnecessary progress bar when scanning small directories')

	WC_PATH = '{path}'
	cmd_file_browser = Config('cmd.filebrowser', CommandWithAlternatives([
		['ranger', WC_PATH],
		['xdg-open', WC_PATH],
		['vim', WC_PATH],
	]), help='the command used to open a directory')

	help_bar_content_progress_bar = [
		urwid_multi_key_support.HelpItem(QUIT, 'quit'),
	]

	# ------- app.init -------

	def __init__(self, path_src: typing.Optional[str], path_dst: typing.Optional[str]) -> None:
		self.delay_show()
		lsblk.udisksctl.set_logger(self)
		self.frameview = urwid.Frame(None)
		self.screen = self.create_screen()
		self.loop = urwid.MainLoop(self.frameview, screen=self.screen, input_filter=self.input_filter, unhandled_input=self.unhandled_input, handle_mouse=self.handle_mouse)
		self._last_widget: typing.Optional[urwid.Widget] = None
		urwid_colors.ColorStr.set_logger(self)
		urwid_colors.ColorStr.set_register_color(self.register_color)
		urwid_colors.ColorConfig.set_register_color(self.register_color)

		self.command_maps = {
			'diff' : DiffWidget._command_map,
			'edit' : urwid_directory_chooser.ExtendedEdit._command_map,
			'directory-browser.menu' : urwid_directory_chooser.MenuWidget._command_map,
			'general' : urwid.command_map,
		}
		self.config = configfile.Exporter(self, self.command_maps, urwid.command_map)
		self.load_config()

		self.undelay_show()

		if path_dst is None:
			if path_src is None:
				backup_plan = self.default_backup_plan
			else:
				backup_plan = path_src
				path_src = None
			if not self.load_backup_plan(backup_plan):
				return
		else:
			assert path_src
			self.config_id = MultiConfig.default_config_id
			self.path_src = Path(path_src)
			self.path_dst = Path(path_dst)
			del self.config_id
		self.init_model()

	def init_model(self) -> None:
		cls = type(self)
		paths = []
		for config_id in cls.path_src.config_ids:
			self.config_id = config_id
			try:
				path_src = self.path_src
				src_defined = bool(path_src)
			except KeyError:
				src_defined = False
			try:
				path_dst = self.path_dst
				dst_defined = bool(path_dst)
			except KeyError:
				dst_defined = False
			del self.config_id

			if not src_defined and not dst_defined:
				if config_id == MultiConfig.default_config_id:
					continue
				self.show_error('{key_src} and {key_dst} undefined for {config_id}'.format(key_src=cls.path_src.key, key_dst=cls.path_dst.key, config_id=config_id))
				continue
			elif not src_defined:
				self.show_error('{key_src} undefined for {config_id}'.format(key_src=cls.path_src.key, config_id=config_id))
				continue
			elif not dst_defined:
				self.show_error('{key_dst} undefined for {config_id}'.format(key_dst=cls.path_dst.key, config_id=config_id))
				continue

			try:
				expanded_path_src = lsblk.mounter.expand_path(path_src, self.password_screen())
			except lsblk.SubprocessException as e:
				self.unrecoverable_error(ERROR_FAILED_TO_MOUNT_DEVICE, 'failed to mount {key} {path!r}'.format(key=cls.path_src.key, path=path_src.raw))

			try:
				expanded_path_dst = lsblk.mounter.expand_path(path_dst, self.password_screen())
			except lsblk.SubprocessException as e:
				self.unrecoverable_error(ERROR_FAILED_TO_MOUNT_DEVICE, 'failed to mount {key} {path!r}'.format(key=cls.path_dst.key, path=path_dst.raw))

			paths.append((config_id, expanded_path_src, expanded_path_dst))

		self.meta_node = model.MetaNode()
		self.loader_thread = threading.Thread(target=self._load_model_in_other_thread, args=[paths], daemon=True)
		self.loader_thread.start()
		self.loader_thread.join(self.time_before_opening_loading_screen)
		if self.loader_thread.is_alive():
			self.number_files: typing.Optional[int] = None
			self.counter_thread = threading.Thread(target=self._count_number_files_in_other_thread, args=[paths], daemon=True)
			self.counter_thread.start()
			self.progressbar = MyProgressBar(self)
			self.frameview.body = urwid.Filler(self.progressbar)
			self.show_help_bar(self.help_bar_content_progress_bar, urwid.command_map, edit_context=False)
			self.loop.set_alarm_in(self.progress_bar_update_time, self.update_progressbar)
		else:
			self.after_load()


	def _load_model_in_other_thread(self, paths: typing.Sequence[typing.Tuple[ConfigId, str, str]]) -> None:
		self._exception_in_loader = None
		try:
			self.t0 = time.time()
			self.meta_node.load(paths)
			self.t1 = time.time()
		except BaseException as e:
			self._exception_in_loader = e


	def _count_number_files_in_other_thread(self, paths: typing.Sequence[typing.Tuple[ConfigId, str, str]]) -> None:
		self.number_files = sum(model.count_files(path_src) for config_id, path_src, path_dst in paths)

	def update_progressbar(self, loop: urwid.MainLoop, user_data: typing.Any) -> None:
		if self.loader_thread.is_alive():
			self.progressbar.add_progress(model.ComparisonNode.number_nodes - self.progressbar.current, self.number_files)
			self.loop.set_alarm_in(self.progress_bar_update_time, self.update_progressbar)
		else:
			self.after_load()

	def after_load(self) -> None:
		if self._exception_in_loader:
			raise self._exception_in_loader
		root_directory_node = FileOrDirectoryNode(self.meta_node)
		self.statistics_widget = StatisticsWidget()
		treeview = DiffWidget(self, urwid.TreeWalker(root_directory_node))
		treeview.set_error_listener(self.on_error)
		widget = urwid.Frame(treeview, footer=self.statistics_widget)
		self.frameview.body = widget
		self.show_info('scanning the directories has taken %s' % time_difference_to_str(self.t1-self.t0))

	def show_help_bar(self, help_bar_content: typing.Sequence[urwid_multi_key_support.HelpItem], command_map: urwid_multi_key_support.SubCommandMap, *, edit_context: bool) -> None:
		self.frameview.header = urwid_multi_key_support.HelpBar(help_bar_content, command_map, self, edit_context=edit_context)

	def save_help_bar(self) -> None:
		self._prev_help_bar = self.frameview.header

	def restore_help_bar(self) -> None:
		self.frameview.header = self._prev_help_bar


	def load_backup_plan(self, name: str) -> bool:
		if self.is_path(name):
			fn = name
		else:
			path = self.get_backup_plan_directory()
			fn = os.path.join(path, name)
		if not os.path.isfile(fn):
			if self.should_ask_to_create_backup_plan:
				self.ask_to_create_backup_plan(name, fn)
				return False
			else:
				self.error_in_init(f'backup plan {name!r} does not exist')
		self.load_config(fn)
		return True

	@classmethod
	def get_backup_plan_directory(cls) -> str:
		path = os.path.split(configfile.Exporter.get_filename_to_write())[0]
		path = os.path.join(path, cls.DIR_BACKUP_PLANS)
		return path

	@classmethod
	def list_backup_plans(cls) -> typing.Sequence[str]:
		out = os.listdir(cls.get_backup_plan_directory())
		out = [fn for fn in out if not fn.startswith('.')]
		out.sort()
		return out

	@classmethod
	def edit_backup_plan(cls, name: str) -> None:
		fn = os.path.join(cls.get_backup_plan_directory(), name)
		cmd = [cls.get_editor(), fn]
		subprocess.run(cmd)

	@classmethod
	def delete_backup_plan(cls, name: str) -> None:
		fn = os.path.join(cls.get_backup_plan_directory(), name)
		os.remove(fn)

	def is_path(self, name: str) -> bool:
		return os.path.isabs(name) or name.split(os.path.sep)[0] in (os.path.curdir, os.path.pardir)

	def ask_to_create_backup_plan(self, name: str, fn: str) -> None:
		dialog = urwid_dialog.YesNoDialog(self, f'Backup plan {name!r} does not exist. Do you want to create it?', yes=lambda: self.ask_for_backup_plan_data(name, fn), no=self.quit)
		dialog.set_key_handler(self.handle_key)
		self.frameview.body = dialog

	def ask_for_backup_plan_data(self, name: str, fn: str) -> None:
		self.frameview.body = BackupPlanWidget(self, name, fn, create=self.create_backup_plan, cancel=self.quit)

	def create_backup_plan(self, widget: 'BackupPlanWidget') -> None:
		name = widget.get_name()
		fn = widget.get_file_name()
		for paths_group in widget.get_path_groups():
			self.config_id = self.generate_config_id(paths_group)
			self.path_src = Path(paths_group.get_path_src())
			self.path_dst = Path(paths_group.get_path_dst())
			del self.config_id
		self.config.save(fn, settings=[App.path_src, App.path_dst, model.ComparisonNode.state_direction_map], key_maps=False)
		self.ask_to_edit_backup_plan(fn)

	def ask_to_edit_backup_plan(self, fn: str) -> None:
		self.frameview.body = urwid_dialog.YesNoDialog(
			self,
			'I have created {fn}.\nDo you want to edit it (e.g. to change default directions)?'.format(fn=fn),
			yes = lambda: self.edit_backup_plan_and_start(fn),
			no = self.init_model,
		)

	def edit_backup_plan_and_start(self, fn: str) -> None:
		self.run_tui_command([self.get_editor(), fn])
		MultiConfig.reset()
		self.load_config(fn)
		self.init_model()

	def generate_config_id(self, paths_group: 'PathsGroup') -> ConfigId:
		path_src = paths_group.get_path_src()
		out = ConfigId(os.path.split(path_src)[1])
		if out not in MultiConfig.config_ids:
			return out

		return ConfigId('%s > %s' % (path_src, paths_group.get_path_dst()))


	def create_screen(self) -> urwid.BaseScreen:
		from urwid.raw_display import Screen
		screen = Screen()
		return screen


	def error_in_init(self, msg: str) -> typing.NoReturn:
		for i_attr, i_msg in self._delayed_messages:
			print(i_msg, file=sys.stderr)

		print(msg, file=sys.stderr)
		sys.exit(1)


	# ------- show -------

	loglevel_attributes = {
		LOG_LEVEL.ERROR : color_error.value,
		LOG_LEVEL.INFO : color_info.value,
	}

	def on_error(self, exc: Exception) -> None:
		msg = str(exc)
		self.show_error(msg)

	def show_error(self, msg: typing.Union[BaseException, str]) -> None:
		self.show(LOG_LEVEL.ERROR, str(msg))

	def show_info(self, msg: str) -> None:
		self.show(LOG_LEVEL.INFO, msg)


	def delay_show(self) -> None:
		self._delay_show = True
		self._delayed_messages: typing.List[typing.Tuple[LOG_LEVEL, str]] = []
	
	def undelay_show(self) -> None:
		for lv, msg in self._delayed_messages:
			self._show_directly(lv, msg)
		del self._delayed_messages
		self._delay_show = False

	def show(self, lv: LOG_LEVEL, msg: str) -> None:
		if lv < self.log_level:
			return

		if self._delay_show:
			self._show_delayed(lv, msg)
		else:
			self._show_directly(lv, msg)

	def _show_delayed(self, lv: LOG_LEVEL, msg: str) -> None:
		self._delayed_messages.append((lv, msg))

	def _show_directly(self, lv: LOG_LEVEL, msg: str) -> None:
		if not isinstance(self.frameview.footer, urwid.Pile):
			self.frameview.footer = urwid.Pile([])
		attr = self.loglevel_attributes[lv]
		widget = urwid.Text((attr, msg))
		self.frameview.footer.contents.append((widget, (urwid.PACK, None)))


	def input_filter(self, keys: typing.List[URWID_TYPE_KEY], raw: typing.List[int]) -> typing.List[URWID_TYPE_KEY]:
		self.frameview.footer = None
		return keys


	def unrecoverable_error(self, exit_code: int, err_message: str) -> typing.NoReturn:
		self.screen.stop()
		print(err_message, file=sys.stderr)
		sys.exit(exit_code)


	def handle_key(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		cmd = urwid.command_map[key]
		if cmd == HELP_LIST_OF_KEY_MAPPINGS:
			self.open_help_list_of_key_mappings()
		elif cmd == HELP_LIST_OF_COMMANDS:
			self.open_help_list_of_commands()
		elif cmd == HELP_CONFIG:
			self.open_help_config()

		elif cmd == CONFIG:
			self.open_config()
		elif cmd == QUIT:
			self.quit()
		else:
			return key

		return None


	# ------- pressed keys overlay -------

	def open_pressed_keys_overlay(self, pressed_keys: typing.Sequence[URWID_TYPE_KEY], command_map: urwid_multi_key_support.SubCommandMap) -> None:
		self._body_widget = self.frameview.body
		self.frameview.body = urwid_multi_key_support.OverlayPressedKeys(self.frameview.body, pressed_keys, command_map)

	def close_pressed_keys_overlay(self) -> None:
		self.frameview.body = self._body_widget
		self._body_widget = None


	# ------- actions -------

	def unhandled_input(self, key: URWID_TYPE_KEY) -> bool:
		cmd = urwid.command_map[key]
		if cmd == QUIT:
			self.quit()
		else:
			return False
		return True  # type: ignore [unreachable]

	def quit(self) -> typing.NoReturn:
		raise urwid.ExitMainLoop()

	def run_tui_command(self, cmd: typing.Sequence[str]) -> None:
		self.screen.stop()
		run_and_pipe(cmd)
		self.screen.start()

	def create_config_if_not_existing(self) -> str:
		# I have moved this into a separate function to avoid a bug in mypy 0.950
		# complaining about "Implicit return in function which does not return"
		fn = self.config.get_filename_to_write()
		if not os.path.isfile(fn):
			self.config.save(fn, ignore={App.path_src, App.path_dst, App.log_level}, no_multi=True, comment_out=True)
		return fn

	def open_config(self) -> None:
		fn = self.create_config_if_not_existing()
		self.open_file(fn)
		self.load_config(fn)

	def load_config(self, fn: typing.Optional[str] = None) -> None:
		conf_log_level = type(self).log_level
		conf_log_level.save_value(LOG_LEVEL.WARNING)
		self.config.load(fn)
		if not conf_log_level.has_changed():
			conf_log_level.restore_value()

	def open_file_or_directory(self, path: str) -> None:
		if os.path.isfile(path):
			self.open_file(path)
		else:
			self.open_directory(path)

	def open_directory(self, path: str) -> None:
		self.run_tui_command(self.cmd_file_browser.replace(self.WC_PATH, path))

	def open_file(self, fn: str) -> None:
		cmd = [self.get_editor(), fn]
		self.run_tui_command(cmd)

	@classmethod
	def get_editor(cls) -> str:
		cmd = os.environ.get('EDITOR', None)
		if cmd:
			return cmd

		cmd = 'vim'
		if is_installed(cmd):
			return cmd

		return 'nano'


	# ------- help -------

	def open_help_list_of_key_mappings(self) -> None:
		self.open_help(HelpWidgetListOfKeyMappings(self, self.command_maps))

	def open_help_list_of_commands(self) -> None:
		self.open_help(HelpWidgetListOfImplementedCommands(self))

	def open_help_config(self) -> None:
		self.open_help(HelpWidgetFromResource(self, self.resource_help_config))

	def open_help(self, widget: urwid.Widget) -> None:
		if self._last_widget is None:
			self.save_help_bar()
			self._last_widget = self.frameview.body
		self.frameview.body = widget
		self.show_help_bar(widget.help_bar_content, widget._command_map, edit_context=False)

	def close_help(self) -> None:
		self.frameview.body = self._last_widget
		self.restore_help_bar()


	# ------- main -------

	def mainloop(self) -> None:
		self.loop.run()

	def register_color(self, color: urwid_colors.Color) -> None:
		self.screen.register_palette_entry(*color.to_palette_tuple())

	@contextlib.contextmanager
	def password_screen(self) -> typing.Iterator[None]:
		self.screen.stop()
		try:
			yield None
		finally:
			self.screen.start()


# ========== main widget ==========

class DiffWidget(urwid.TreeListBox, urwid_multi_key_support.MultiKeySupport):

	help_bar_content = Config('diff.help-bar', [
		urwid_multi_key_support.HelpItem(HELP_LIST_OF_KEY_MAPPINGS, 'help'),
		urwid_multi_key_support.HelpItem(FUNC_NODE_TOGGLE_DIRECTION, 'toggle direction'),
		urwid_multi_key_support.HelpItem(FUNC_NODE_TOGGLE_IGNORE, 'toggle ignore'),
		urwid_multi_key_support.HelpItem(FUNC_DIFF, 'show changes'),
		urwid_multi_key_support.HelpItem('<O>', 'open ...'),
		urwid_multi_key_support.HelpItem('<y>', 'copy ...'),
		urwid_multi_key_support.HelpItem(CONFIG, 'edit config'),
	])

	PATH_SRC = '{path.src}'
	PATH_DST = '{path.dst}'
	cmd_diff = Config('cmd.diff', CommandWithAlternatives([
		['diff', '--color=always', '--side-by-side', PATH_SRC, PATH_DST, '|', 'less', '-R'],
		['vimdiff', PATH_SRC, PATH_DST],
	]), help='the command used to display the differences between two files')

	_command_map = urwid.command_map.copy()
	urwid_multi_key_support.replace_command(_command_map, urwid.CURSOR_MAX_LEFT, CURSOR_MAX_UP)
	urwid_multi_key_support.replace_command(_command_map, urwid.CURSOR_MAX_RIGHT, CURSOR_MAX_DOWN)
	urwid_multi_key_support.replace_command(_command_map, urwid.CURSOR_LEFT, FUNC_VIEW_COLLAPSE_PARENT)
	urwid_multi_key_support.replace_command(_command_map, urwid.CURSOR_RIGHT, FUNC_VIEW_EXPAND)
	_command_map['u'] = FUNC_NODE_TOGGLE_DIRECTION
	_command_map[' '] = FUNC_NODE_TOGGLE_IGNORE
	_command_map['>'] = FUNC_NODE_SET_DIRECTION_SRC_TO_DST
	_command_map['<'] = FUNC_NODE_SET_DIRECTION_DST_TO_SRC
	_command_map['f5'] = FUNC_NODE_UPDATE
	_command_map['d'] = FUNC_DIFF
	_command_map['y'] = urwid_multi_key_support.SubCommandMap()
	_command_map['y']['p'] = urwid_multi_key_support.SubCommandMap()
	_command_map['y']['p']['s'] = FUNC_YANK_PATH_SRC
	_command_map['y']['p']['d'] = FUNC_YANK_PATH_DST
	_command_map['O'] = urwid_multi_key_support.SubCommandMap()
	_command_map['O']['<'] = FUNC_OPEN_SRC
	_command_map['O']['>'] = FUNC_OPEN_DST
	_command_map.implemented_commands = {
		urwid.CURSOR_UP,
		urwid.CURSOR_DOWN,
		urwid.CURSOR_PAGE_UP,
		urwid.CURSOR_PAGE_DOWN,
		CURSOR_MAX_UP,
		CURSOR_MAX_DOWN,
		FUNC_VIEW_COLLAPSE,
		FUNC_VIEW_COLLAPSE_PARENT,
		FUNC_VIEW_EXPAND,
		FUNC_NODE_TOGGLE_DIRECTION,
		FUNC_NODE_TOGGLE_IGNORE,
		FUNC_NODE_SET_DIRECTION_SRC_TO_DST,
		FUNC_NODE_SET_DIRECTION_DST_TO_SRC,
		FUNC_NODE_UPDATE,
		FUNC_YANK_PATH_SRC,
		FUNC_YANK_PATH_DST,
		FUNC_OPEN_SRC,
		FUNC_OPEN_DST,
		FUNC_DIFF,
		HELP_LIST_OF_KEY_MAPPINGS,
		HELP_LIST_OF_COMMANDS,
		HELP_CONFIG,
		CONFIG,
		QUIT,
	}

	def __init__(self, app: App, tree_walker: urwid.TreeWalker) -> None:
		super().__init__(tree_walker)
		self.init_multi_key_support(app)
		self.app = app
		self.clipboard = clipboard.Clipboard(self.app)
		self.update_statistics()
		self.app.show_help_bar(self.help_bar_content, self._command_map, edit_context=False)

	def update_statistics(self) -> None:
		self.app.statistics_widget.set(self.focus.get_model())


	# ------- overriding methods -------

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if self.waiting_for_next_key(key):
			return None

		try:
			func = self._command_map[key]
			if func == FUNC_VIEW_COLLAPSE:
				self.set_expanded(False)
			elif func == FUNC_VIEW_COLLAPSE_PARENT:
				self.collapse_parent()
			elif func == FUNC_VIEW_EXPAND:
				self.set_expanded(True)
			elif func == CURSOR_MAX_UP:
				self.focus_home(size)
			elif func == CURSOR_MAX_DOWN:
				self.focus_end(size)

			elif func == FUNC_NODE_TOGGLE_DIRECTION:
				try:
					self.focus.get_model().toggle_direction()
				except model.CommandNotAllowed as e:
					self.notify_error(e)
			elif func == FUNC_NODE_TOGGLE_IGNORE:
				try:
					self.focus.get_model().toggle_ignore()
				except model.CommandNotAllowed as e:
					self.notify_error(e)
			elif func == FUNC_NODE_SET_DIRECTION_SRC_TO_DST:
				try:
					self.focus.get_model().set_direction_recursively(model.DIRECTION.SRC_TO_DST)
				except model.CommandNotAllowed as e:
					self.notify_error(e)
			elif func == FUNC_NODE_SET_DIRECTION_DST_TO_SRC:
				try:
					self.focus.get_model().set_direction_recursively(model.DIRECTION.DST_TO_SRC)
				except model.CommandNotAllowed as e:
					self.notify_error(e)
			elif func == FUNC_NODE_UPDATE:
				self.focus.get_model().update()
				self.focus.update_widget()

			elif func == FUNC_YANK_PATH_SRC:
				self.clipboard.copy(self.focus.get_model().path_src)
			elif func == FUNC_YANK_PATH_DST:
				self.clipboard.copy(self.focus.get_model().path_dst)

			elif func == FUNC_OPEN_SRC:
				self.app.open_file_or_directory(self.focus.get_model().path_src)
			elif func == FUNC_OPEN_DST:
				self.app.open_file_or_directory(self.focus.get_model().path_dst)

			elif func == FUNC_DIFF:
				cn = self.focus.get_model()
				cmd = self.cmd_diff.replace(self.PATH_SRC, cn.path_src).replace(self.PATH_DST, cn.path_dst)
				self.app.run_tui_command(cmd)

			elif self.app.handle_key(size, key) is None:
				pass

			else:
				out = typing.cast(typing.Optional[URWID_TYPE_KEY], self.__super.keypress(size, key))
				if not out:
					self.update_statistics()
				return out

			self.update_statistics()
			assert func in self._default_command_map.implemented_commands
			return None

		finally:
			self.reset_command_map()


	# ------- custom methods -------

	def set_expanded(self, value: bool) -> None:
		comparison_widget: ComparisonWidget = self.focus
		comparison_widget.set_expanded(value)

		tree_node: FileOrDirectoryNode = comparison_widget.get_node()
		if hasattr(tree_node, 'last_focus') and tree_node.last_focus.is_existing():
			self.body.set_focus(tree_node.last_focus)

	def collapse_parent(self) -> None:
		comparison_widget: ComparisonWidget = self.focus
		tree_node: FileOrDirectoryNode = comparison_widget.get_node()
		if comparison_widget.expanded:
			comparison_widget.set_expanded(False)
			tree_node.last_focus = tree_node
			return

		parent_tree_node = tree_node.get_parent()
		if parent_tree_node is None:
			comparison_widget.set_expanded(False)
			tree_node.last_focus = tree_node
			return

		self.body.set_focus(parent_tree_node)
		parent_widget = parent_tree_node.get_widget()
		parent_widget.set_expanded(False)
		parent_tree_node.last_focus = tree_node


	def set_error_listener(self, callback: typing.Callable[[Exception], None]) -> None:
		self.error_listener = callback

	def notify_error(self, exception: Exception) -> None:
		if hasattr(self, 'error_listener'):
			self.error_listener(exception)


class ComparisonWidget(urwid.TreeWidget):

	indent_cols: int  # inherited from TreeWidget

	highlight_action_of_expanded_parent_as_changed = Config('diff.highligt-action-of-expanded-parent-as-changed', False)

	action_width = 5

	COLOR_SEP = urwid_colors.Color.SEP_COLOR
	BG_ACTION_DEFAULT = 'black'
	BG_ACTION_CHANGED = 'blue'

	FG_ACTION_CREATE  = 'green,bold'
	FG_ACTION_DELETE  = 'red,bold'
	FG_ACTION_CHANGE  = 'default'
	FG_ACTION_IGNORE  = 'default'
	FG_ACTION_NONE    = 'white'

	color_action_create = urwid_colors.ColorConfig('diff.color.action-create', FG_ACTION_CREATE + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_delete = urwid_colors.ColorConfig('diff.color.action-delete', FG_ACTION_DELETE + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_change = urwid_colors.ColorConfig('diff.color.action-change', FG_ACTION_CHANGE + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_ignore = urwid_colors.ColorConfig('diff.color.action-ignore', FG_ACTION_IGNORE + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_none   = urwid_colors.ColorConfig('diff.color.action-none',   FG_ACTION_NONE   + COLOR_SEP + BG_ACTION_DEFAULT)

	color_changed_action_create = urwid_colors.ColorConfig('diff.color.changed-action-create', FG_ACTION_CREATE + COLOR_SEP + BG_ACTION_CHANGED)
	color_changed_action_delete = urwid_colors.ColorConfig('diff.color.changed-action-delete', FG_ACTION_DELETE + COLOR_SEP + BG_ACTION_CHANGED)
	color_changed_action_change = urwid_colors.ColorConfig('diff.color.changed-action-change', FG_ACTION_CHANGE + COLOR_SEP + BG_ACTION_CHANGED)
	color_changed_action_ignore = urwid_colors.ColorConfig('diff.color.changed-action-ignore', FG_ACTION_IGNORE + COLOR_SEP + BG_ACTION_CHANGED)
	color_changed_action_none =   urwid_colors.ColorConfig('diff.color.changed-action-none',   FG_ACTION_NONE   + COLOR_SEP + BG_ACTION_CHANGED)

	action_symbol = DictConfig('diff.action-symbols', {
		model.ACTION.NONE               : ' = ',
		model.ACTION.IGNORE             : ' | ',
		model.ACTION.CREATE             : ' >+',
		model.ACTION.DELETE             : ' >-',
		model.ACTION.UPDATE             : ' > ',
		model.ACTION.DOWNGRADE          : ' >!',
		model.ACTION.UNDO_CREATE        : '-< ',
		model.ACTION.UNDO_DELETE        : '+< ',
		model.ACTION.UNDO_UPDATE        : '!< ',
		model.ACTION.UNDO_DOWNGRADE     : ' < ',
		model.ACTION.DIR_CHANGE_DESTINATION  : ' > ',
		model.ACTION.DIR_CHANGE_SOURCE  : ' < ',
		model.ACTION.DIR_CHANGE_BOTH    : '> <',
		model.ACTION.CHANGE_DESTINATION_TYPE : ' >t',
		model.ACTION.CHANGE_SOURCE_TYPE : 't< ',
		model.ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN        : '->+',
		model.ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN   : '+<-',
		model.ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN : '->t',
		model.ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN      : 't<-',
	})

	action_format = {
		model.ACTION.NONE               : (color_action_none.value,   color_changed_action_none.value),
		model.ACTION.IGNORE             : (color_action_ignore.value, color_changed_action_ignore.value),
		model.ACTION.CREATE             : (color_action_create.value, color_changed_action_create.value),
		model.ACTION.DELETE             : (color_action_delete.value, color_changed_action_delete.value),
		model.ACTION.UPDATE             : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.DOWNGRADE          : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.UNDO_CREATE        : (color_action_delete.value, color_changed_action_delete.value),
		model.ACTION.UNDO_DELETE        : (color_action_create.value, color_changed_action_create.value),
		model.ACTION.UNDO_UPDATE        : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.UNDO_DOWNGRADE     : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.DIR_CHANGE_DESTINATION  : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.DIR_CHANGE_SOURCE  : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.DIR_CHANGE_BOTH    : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CHANGE_DESTINATION_TYPE : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CHANGE_SOURCE_TYPE : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN        : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN   : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN      : (color_action_change.value, color_changed_action_change.value),
	}


	def __init__(self, tree_node: urwid.TreeNode) -> None:
		super().__init__(tree_node)

		cn = self.get_model()
		cn.set_direction_changed_listener(self.update_action)

		# I need to set self.expanded because it's used by urwid internally
		if isinstance(cn, model.DirectoryComparisonNode):
			self.expanded = cn.is_expanded
		else:
			self.expanded = False

	# methods of urwid.TreeWidget:
	# self.get_node() -> urwid.TreeNode

	def get_model(self) -> model.ComparisonNode:
		return typing.cast(model.ComparisonNode, self.get_node().get_value())

	def get_action(self) -> typing.Tuple[str, str]:
		comparison_node = self.get_model()
		has_action_been_changed = comparison_node.has_direction_been_changed()
		if isinstance(comparison_node, model.DirectoryComparisonNode) and (not comparison_node.is_expanded or self.highlight_action_of_expanded_parent_as_changed):
			has_action_been_changed = has_action_been_changed or comparison_node.has_child_direction_been_changed()
		action_symbol = self.action_symbol[comparison_node.action]
		action_format = self.action_format[comparison_node.action][has_action_been_changed]
		action_symbol = ' ' + action_symbol + ' '
		return (action_format, action_symbol)


	# ------- overriding methods -------

	def get_indented_widget(self) -> urwid.Widget:
		cn = self.get_model()

		indent_cols = self.get_indent_cols()
		is_expanded = isinstance(cn, model.DirectoryComparisonNode) and cn.is_expanded
		self.widget_src = FileWidget(cn.name_src, cn.type_src, cn.type_dst, cn.error_src, is_expanded, indent_cols)
		self.widget_dst = FileWidget(cn.name_dst, cn.type_dst, cn.type_src, cn.error_dst, is_expanded, indent_cols)
		self.widget_action = urwid.Text(self.get_action())

		widget = urwid.Columns(
			[
				('weight', 1, self.widget_src),
				('fixed', self.action_width, self.widget_action),
				('weight', 1, self.widget_dst)
			], dividechars=0)

		widget = urwid.AttrMap(widget, None, urwid_colors.focus_map)

		return widget

	def get_indent_cols(self) -> int:
		return self.indent_cols * (typing.cast(int, self.get_node().get_depth()) - 1)

	def update_expanded_icon(self) -> None:
		self.widget_src.update_expanded_icon(self.expanded)
		self.widget_dst.update_expanded_icon(self.expanded)


	def selectable(self) -> bool:
		return True


	# ------- custom methods -------

	def update_action(self) -> None:
		self.widget_action.set_text(self.get_action())

	def update_widget(self) -> None:
		self.get_node().reload_children()
		self._w = self.get_indented_widget()


	def set_expanded(self, value: bool) -> None:
		cn = self.get_model()
		if not isinstance(cn, model.DirectoryComparisonNode):
			return

		cn.set_expanded(value)
		# expanded is used by urwid so I need to set it
		self.expanded = value
		self.update_expanded_icon()
		if not self.highlight_action_of_expanded_parent_as_changed:
			self.update_action()

class TitleWidget(ComparisonWidget):

	color_title = urwid_colors.ColorConfig('diff.color.title', 'cyan')

	def get_indented_widget(self) -> urwid.Widget:
		cn = self.get_model()

		self.widget_src = urwid.Text(cn.name_src)
		self.widget_dst = urwid.Text(cn.name_dst)
		self.widget_action = urwid.Text(self.get_action())

		widget = urwid.Columns(
			[
				('weight', 1, self.widget_src),
				('fixed', self.action_width, self.widget_action),
				('weight', 1, self.widget_dst)
			], dividechars=0)

		widget = urwid.AttrMap(widget, None, urwid_colors.focus_map)
		widget = urwid.AttrMap(widget, self.color_title, type(self).color_title.focus.value)

		return widget

	def update_expanded_icon(self) -> None:
		pass

	def set_expanded(self, value: bool) -> None:
		pass


class FileWidget(urwid.AttrMap):

	color_type_file = urwid_colors.ColorConfig('diff.color.type-file', 'default', focus='black/white')
	color_type_dir = urwid_colors.ColorConfig('diff.color.type-dir', 'yellow', focus='black/yellow')
	color_type_missing_file = urwid_colors.ColorConfig('diff.color.type-missing-file', 'magenta', focus='magenta/white')
	color_type_missing_dir = urwid_colors.ColorConfig('diff.color.type-missing-dir', 'magenta', focus='magenta/yellow')
	color_error = urwid_colors.ColorConfig('diff.color.error', 'default/red')

	icon_directory_closed   = urwid.Text('[-] ')  #(' ')
	icon_directory_expanded = urwid.Text('[+] ')  #(' ')

	icon_file = urwid.Text('[f] ')  #(' ') #(' ')
	icon_not_existing = urwid.Text('[x] ')  #(' ')  #  

	icon_width = 4

	def __init__(self, name: str, filetype: model.TYPE, other_filetype: model.TYPE, error: typing.Optional[str], expanded: bool, indent_cols: int) -> None:
		self.filetype = filetype

		icon = self.get_icon_widget(expanded)
		name = urwid.Text(name)
		attr = self.get_attr(filetype, other_filetype, error)

		widget = urwid.Columns([('fixed', self.icon_width, icon), name], dividechars=1)
		widget = urwid.Padding(widget, width=('relative', 100), left=indent_cols)
		super().__init__(widget, attr)


	# ------- internal methods -------

	def get_attr(self, filetype: model.TYPE, other_filetype: model.TYPE, error: typing.Optional[str]) -> str:
		if error:
			return self.color_error
		elif filetype is model.TYPE.FILE:
			return self.color_type_file
		elif filetype is model.TYPE.DIRECTORY:
			return self.color_type_dir
		elif other_filetype is model.TYPE.DIRECTORY:
			return self.color_type_missing_dir
		else:
			return self.color_type_missing_file

	def get_icon_widget(self, expanded: bool) -> urwid.Widget:
		filetype = self.filetype
		if filetype == model.TYPE.DIRECTORY:
			if expanded:
				icon = self.icon_directory_expanded
			else:
				icon = self.icon_directory_closed
		elif filetype == model.TYPE.FILE:
			icon = self.icon_file
		elif filetype == model.TYPE.NOT_EXISTING:
			icon = self.icon_not_existing

		return icon


	# ------- public methods -------

	def update_expanded_icon(self, expanded: bool) -> None:
		# see original implementation of
		# urwid.TreeWidget.update_expanded_icon
		self.base_widget.widget_list[0] = self.get_icon_widget(expanded)


class FileOrDirectoryNode(urwid.ParentNode):

	_child_keys: typing.Optional[typing.Sequence[model.ComparisonNode]]
	_children: typing.Dict[model.ComparisonNode, urwid.TreeNode]

	def __init__(self, comparison_node: model.ComparisonNode, parent: typing.Optional[urwid.TreeNode] = None) -> None:
		super().__init__(value=comparison_node, key=comparison_node, parent=parent)


	# ------- overriding methods -------

	def load_widget(self) -> urwid.Widget:
		if isinstance(self.get_key(), model.MetaNode):
			return TitleWidget(self)
		return ComparisonWidget(self)

	def load_child_keys(self) -> typing.Sequence[model.ComparisonNode]:
		'''Provide ParentNode with an ordered list of child keys (implementation of virtual function)'''
		cn = self.get_value()
		if isinstance(cn, model.DirectoryComparisonNode):
			return cn.children
		else:
			return []

	def load_child_node(self, key: model.ComparisonNode) -> urwid.TreeNode:
		'''Load the child node for a given key (implementation of virtual function)'''
		return FileOrDirectoryNode(key, parent=self)

	def reload_children(self) -> None:
		self._child_keys = None
		self._children = {}


	# ------- custom methods -------

	def is_existing(self) -> bool:
		if self.get_parent() is None:
			return True
		return self.get_key() in self.get_parent().get_child_keys()


# ========== statistics widget ==========

class StatisticsWidget(urwid.WidgetWrap):

	sep = Config('diff.statistics.sep', urwid_colors.ColorStr(', '))
	pattern_errors = Config('diff.statistics.pattern.errors', urwid_colors.ColorStr('<color={' + FileWidget.color_error.key + '}>{n} error(s)</color>'))
	pattern_action = Config('diff.statistics.pattern.action', urwid_colors.ColorStr('{n}x<color={{action_color_name}}/bright black>{action_symbol}</color>'))

	actions = Config('diff.statistics.actions-to-show', [
		model.ACTION.NONE,
		model.ACTION.IGNORE,
		model.ACTION.CREATE,
		model.ACTION.DELETE,
		model.ACTION.UNDO_CREATE,
		model.ACTION.UNDO_DELETE,

		model.ACTION.UPDATE,
		model.ACTION.DOWNGRADE,
		model.ACTION.UNDO_UPDATE,
		model.ACTION.UNDO_DOWNGRADE,

		model.ACTION.CHANGE_DESTINATION_TYPE,
		model.ACTION.CHANGE_SOURCE_TYPE,

		model.ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		model.ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		model.ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN,
		model.ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN,
	])

	def __init__(self) -> None:
		self.text = urwid.Text('')
		super().__init__(self.text)

	def set(self, cn: model.ComparisonNode) -> None:
		if not isinstance(cn, model.DirectoryComparisonNode):
			self.text.set_text('')
			return

		statistics = cn.statistics
		markup = []
		if statistics.number_nodes_with_errors > 0:
			markup.append(urwid_colors.ColorStr.to_markup(self.pattern_errors, format=dict(n=statistics.number_nodes_with_errors)))
		for a in self.actions:
			n = statistics.statistics.get(a, 0)
			if n == 0:
				continue

			if markup:
				markup.append(urwid_colors.ColorStr.to_markup(self.sep))

			symbol = ComparisonWidget.action_symbol[a]
			name = a.name.lower()
			color_name = ComparisonWidget.action_format[a][0]
			markup.append(urwid_colors.ColorStr.to_markup(self.pattern_action.replace('{action_color_name}', color_name), format=dict(n=n, action_symbol=symbol, action_name=name)))

		markup = urwid_colors.ColorStr.simplify_markup(markup)
		self.text.set_text(markup)


# ========== create new backup plan ==========

class PathsGroup(urwid.WidgetWrap):

	after_edit = Config('backup-plan-widget.after-edit', urwid_colors.ColorStr(' <color=bright black>|</color> '), help='a symbol indicating the end of an edit widget')

	@property
	def base_widget(self) -> urwid.Widget:
		return self._w.base_widget

	def __init__(self, app: App, master: 'BackupPlanWidget') -> None:
		self.path_src = urwid_directory_chooser.PathEdit(app, 'src: ', '', master)
		self.path_dst = urwid_directory_chooser.PathEdit(app, 'dst: ', '', master)
		self.btn_add = urwid_dialog.ColorButton('+', master.add_path_group)
		self.btn_del = urwid_dialog.ColorButton('-', master.del_path_group)

		w_add = self.btn_add.calc_required_width()
		w_del = self.btn_del.calc_required_width()
		w_after_edit = urwid.Text(urwid_colors.ColorStr.to_markup(self.after_edit))
		widget = urwid_dialog.TabAwarePile((
			urwid_dialog.TabAwareColumns((
				self.path_src,
				(urwid.PACK, w_after_edit),
				(urwid.FIXED, w_add + w_del, urwid.Text('')),
			), cycle_focus=False),
			urwid_dialog.TabAwareColumns((
				self.path_dst,
				(urwid.PACK, w_after_edit),
				(urwid.FIXED, w_add, self.btn_add),
				(urwid.FIXED, w_del, self.btn_del)
			), cycle_focus=False),
			urwid.Text(''),
		), cycle_focus=False)
		super().__init__(widget)

	def focus_first(self) -> None:
		self._w.focus_position = 0
		self._w.contents[0][0].focus_position = 0

	def focus_last(self) -> None:
		self._w.focus_position = 1


	def has_opened_directory_chooser(self) -> bool:
		return self.path_src.has_opened_directory_chooser or self.path_dst.has_opened_directory_chooser

	def is_empty(self) -> bool:
		return not self.get_path_src() and not self.get_path_dst()

	def validate(self) -> bool:
		# I am saving the results in variabls to avoid short cicuiting the `and`
		# so that all invalid inputs are highlighted
		is_src_valid = self.path_src.validate()
		is_dst_valid = self.path_dst.validate()
		return is_src_valid and is_dst_valid

	def get_path_src(self) -> str:
		return self.path_src.get_path()

	def get_path_dst(self) -> str:
		return self.path_dst.get_path()


class BackupPlanWidget(urwid.WidgetWrap):

	help_bar_content = Config('backup-plan-widget.help-bar.button', [
		urwid_multi_key_support.HelpItem(urwid.ACTIVATE, 'click button'),
		urwid_multi_key_support.HelpItem(urwid_dialog.NEXT_SELECTABLE, 'focus next'),
		urwid_multi_key_support.HelpItem(urwid_dialog.PREV_SELECTABLE, 'focus previous'),
	])
	urwid_directory_chooser.PathEdit.help_bar_content.key = 'backup-plan-widget.help-bar.path-edit'

	def __init__(self, app: App, name: str, fn: str, create: typing.Callable[['BackupPlanWidget'], None], cancel: typing.Callable[[], None]):
		self.app = app
		self.name = name
		self.fn = fn
		text = urwid.Text(f'creating backup plan {name!r}')
		sep = urwid.Text('')
		self.create_callback = create
		self.btn_create = urwid_dialog.ColorButton('create', self.validate_and_create)
		self.btn_cancel = urwid_dialog.ColorButton('cancel', lambda btn: cancel())
		self.was_edit_path_focused = False

		self.buttons_frame = urwid_dialog.ButtonsFrame(self.btn_create, self.btn_cancel)
		self.pile = urwid_dialog.TabAwarePile([text, sep, PathsGroup(app, self), self.buttons_frame])
		widget = urwid.Filler(self.pile)
		super().__init__(widget)
		self.on_path_edit_focus_change(self.is_edit_path_focused())

	# ------- update help bar -------

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		out = super().keypress(size, key)
		if not out and self.is_edit_path_focused() != self.was_edit_path_focused:
			self.was_edit_path_focused = not self.was_edit_path_focused
			if not any(w.has_opened_directory_chooser() for w, options in self.pile.contents if isinstance(w, PathsGroup)):
				self.on_path_edit_focus_change(self.was_edit_path_focused)
		return typing.cast(typing.Optional[URWID_TYPE_KEY], out)

	def is_edit_path_focused(self) -> bool:
		widget = self._w
		while hasattr(widget, 'focus'):
			widget = widget.base_widget.focus
			if isinstance(widget, urwid_directory_chooser.PathEdit):
				return True
		return False

	def on_path_edit_focus_change(self, focus: bool) -> None:
		self.was_edit_path_focused = focus
		if focus:
			content = urwid_directory_chooser.PathEdit.help_bar_content.value
			edit_context = True
		else:
			content = self.help_bar_content
			edit_context = False
		self.app.show_help_bar(content, self._command_map, edit_context=edit_context)

	# ------- buttons -------

	def add_path_group(self, btn_add: urwid.Button) -> None:
		contents = self.pile.contents
		i = next(i for i in range(len(contents)) if isinstance(w := contents[i][0], PathsGroup) and w.btn_add.base_widget is btn_add)
		contents.insert(i+1, (PathsGroup(self.app, self), (urwid.PACK, None)))
		self.pile.focus_position = i + 1

	def del_path_group(self, btn_del: urwid.Button) -> None:
		contents = self.pile.contents
		i = next(i for i in range(len(contents)) if isinstance(w := contents[i][0], PathsGroup) and w.btn_del.base_widget is btn_del)
		del contents[i]

		if len(self.get_path_groups()) < 1:
			contents.insert(i, (PathsGroup(self.app, self), (urwid.PACK, None)))
			self.pile.focus_position = i

	def validate_and_create(self, btn_create: urwid.Button) -> None:
		paths = self.get_path_groups()
		if not paths:
			self.app.show_error('please enter a pair of paths')
		# I am using sum(not ...) instead of all(...) so that all widgets are validated and highlighted if they contain errors
		elif sum(not w.validate() for w in paths) >= 1:
			self.app.show_error('one or more entered paths are not existing')
		else:
			self.create_callback(self)

	# ------- getters -------

	def get_name(self) -> str:
		return self.name

	def get_file_name(self) -> str:
		return self.fn

	def get_path_groups(self) -> typing.Sequence[PathsGroup]:
		return [w for w, options in self.pile.contents if isinstance(w, PathsGroup) and not w.is_empty()]


# ========== progress bar ==========

class MyProgressBar(urwid_timed_progress.TimedProgressBar, urwid_multi_key_support.MultiKeySupport):

	color_todo = urwid_colors.ColorConfig('progress-bar.color.todo', 'default')
	color_done = urwid_colors.ColorConfig('progress-bar.color.done', 'green/white')
	expected_number_of_files = Config('progress-bar.estimated-number-of-files', 500000, help='a rough guess how many files need to be processed, used for the progress bar before finish counting the real number')
	unit = 'files'

	def __init__(self, app: App) -> None:
		super().__init__(self.color_todo, self.color_done, done=self.expected_number_of_files, units=self.unit)
		self.init_multi_key_support(app)
		self.app = app
		self._selectable = True

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if self.waiting_for_next_key(key):
			return None

		if super().keypress(size, key) is None:
			self.reset_command_map()
			return None

		self.reset_command_map()
		return self.app.handle_key(size, key)


# ========== help ==========

class HelpWidget(urwid.WidgetWrap):

	help_bar_content = Config('help-page.help-bar', [
		urwid_multi_key_support.HelpItem(CANCEL, 'back'),
		urwid_multi_key_support.HelpItem(urwid.CURSOR_UP, 'up'),
		urwid_multi_key_support.HelpItem(urwid.CURSOR_DOWN, 'down'),
	])

	color_section = urwid_colors.ColorConfig('help-page.color.section', 'default,bold')
	color_subsection = urwid_colors.ColorConfig('help-page.color.subsection', 'default')
	indentation = Config('help-page.indentation', '  ')
	indent_subsection_title = Config('help-page.indent-subsection-title', False)

	def __init__(self, widget: urwid_multi_key_support.ExtendedListBox, app: App) -> None:
		super().__init__(widget)
		self.app = app
		widget.set_key_handler(self.handle_key)

	def handle_key(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		cmd = self._command_map[key]
		if cmd == CANCEL:
			self.app.close_help()
		elif self.app.handle_key(size, key) is None:
			pass
		else:
			return key

		return None


class HelpWidgetListOfKeyMappings(HelpWidget):

	def __init__(self, app: App, command_maps: typing.Dict[str, urwid_multi_key_support.SubCommandMap]) -> None:
		widgets = []
		for widget_name, command_map in app.command_maps.items():
			title = 'key mappings in %s' % widget_name
			widget = urwid_multi_key_support.PressedKeysWidget(app, pressed_keys=[], command_map=command_map, title=title)
			widgets.extend(widget.body)
		widget = urwid_multi_key_support.ExtendedListBox(app, widgets)
		super().__init__(widget, app)


class HelpWidgetListOfImplementedCommands(HelpWidget):

	def __init__(self, app: App) -> None:
		widgets = []
		for name, cmdmap in app.command_maps.items():
			title = 'commands which can be mapped to keys in {map_name}'.format(map_name = name)
			widgets.append(HelpTitleWidget(self.color_section, title))
			for cmd in sorted(cmdmap.implemented_commands):
				widgets.append(HelpCommandWidget(cmd))
		widget = urwid_multi_key_support.ExtendedListBox(app, widgets)
		super().__init__(widget, app)

class HelpWidgetFromResource(HelpWidget):

	PREFIX_SECTION = '# '
	PREFIX_SUBSECTION = '## '
	TAB = '    '

	reo_command = re.compile(r'`(?P<command>.*?)`')

	pattern_cmd = Config('help-page.format.command', urwid_colors.ColorStr('<color={%s}>{cmd}</color>' % urwid_multi_key_support.PressedKeysLineWidget.color_cmd.key),
		help='how to format a command which no keys are mapped to. Supports the wildcard {cmd}.')
	pattern_key = Config('help-page.format.key', urwid_colors.ColorStr('<color={%s}>{key}</color> (<color={%s}>{cmd}</color>)' % (urwid_multi_key_support.PressedKeysLineWidget.color_key.key, urwid_multi_key_support.PressedKeysLineWidget.color_cmd.key)),
		help='how to format a command which one or more keys are mapped to. Supports the wildcards {key} and {cmd}.')

	def __init__(self, app: App, resource_name: str) -> None:
		self.app = app
		#https://stackoverflow.com/a/58941536
		raw = pkgutil.get_data(__name__, resource_name)
		assert raw is not None
		widgets = self.parse(raw.decode('utf-8'))
		widget = urwid_multi_key_support.ExtendedListBox(app, widgets)
		super().__init__(widget, app)

	def parse(self, raw: str) -> typing.Sequence[urwid.Widget]:
		widgets = []
		widgets.append(HelpLineWidget(self.indentation + '[The keyboard shortcuts mentioned in the following help page refer to the diff widget.]'))
		widgets.append(HelpLineWidget(''))
		for ln in raw.splitlines():
			ln = ln.rstrip()
			ln = ln.replace('\t', self.TAB)
			if ln.startswith(self.PREFIX_SUBSECTION):
				ln = ln[len(self.PREFIX_SUBSECTION):].strip()
				if self.indent_subsection_title:
					ln = self.indentation + ln
				widgets.append(HelpTitleWidget(self.color_subsection, ln))
			elif ln.startswith(self.PREFIX_SECTION):
				ln = ln[len(self.PREFIX_SECTION):].strip()
				widgets.append(HelpTitleWidget(self.color_section, ln))
			elif '{map_names}' in ln:
				ln = self.indentation + ln
				for map_name in self.app.command_maps.keys():
					widgets.append(HelpLineWidget(ln.format(map_names=map_name)))
			else:
				ln = self.indentation + ln
				widget = self.parse_text_line(ln)
				widgets.append(widget)

		return widgets

	def parse_text_line(self, ln: str) -> 'HelpLineWidget':
		splitted_line = self.reo_command.split(ln)
		markup = [splitted_line[0]]
		for i in range(1, len(splitted_line), 2):
			cmd = splitted_line[i]
			keys = [_key for _key, _cmd in urwid_multi_key_support.KeyMapper.iter_commands(DiffWidget._command_map) if _cmd == cmd]
			text = splitted_line[i+1]
			if keys:
				pattern = self.pattern_key
				format_args = {'cmd': cmd, 'key': keys[0]}
			else:
				pattern = self.pattern_cmd
				format_args = {'cmd': cmd}
			markup.append(urwid_colors.ColorStr.to_markup(pattern, format=format_args))
			markup.append(text)
		return HelpLineWidget(markup)


class HelpLineWidget(urwid.Text):
	pass

class HelpTitleWidget(urwid.Text):

	def __init__(self, color: str, text: str) -> None:
		super().__init__((color, text))

class HelpCommandWidget(urwid.Text):

	color_cmd = urwid_multi_key_support.PressedKeysLineWidget.color_cmd

	def __init__(self, text: str) -> None:
		super().__init__((self.color_cmd, text))


if __name__ == '__main__':
	app = App(os.path.join('test', 'src'), os.path.join('test', 'dst'))
	app.mainloop()
