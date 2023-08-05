import enum
import os
import filecmp
import typing

from .config import Config, DictConfig, MultiConfig, MultiDictConfig, ConfigId


# ---------- types ----------
# each node has two types:
# one for source and one for destination

@enum.unique
class TYPE(enum.Enum):
	FILE = 'f'
	DIRECTORY = 'd'
	NOT_EXISTING = 'x'

	@classmethod
	def from_path(cls, path: str) -> 'TYPE':
		if not os.path.exists(path):
			return TYPE.NOT_EXISTING
		elif os.path.isdir(path):
			return TYPE.DIRECTORY
		else:
			return TYPE.FILE


# ---------- states ----------
# the state describes how the source
# has changed compared to the destination

@enum.unique
class STATE(enum.Enum):
	NEW      = '+'
	DELETED  = '-'
	SAME     = '='

	# ComparisonNode only
	NEWER    = '>'
	OLDER    = '<'

	# DirectoryComparisonNode only
	MODIFIED_DIR = 'm'
	REPLACED_FILE_BY_DIRECTORY = 'd'
	REPLACED_DIRECTORY_BY_FILE = 'f'

# states where children may not have arbitrary directions
STATES_WHICH_HAND_THEIR_DIRECTION_DOWN_TO_THEIR_CHILDREN = {
	# children may be configured to have a different direction
	# but that is to be ignored
	STATE.REPLACED_FILE_BY_DIRECTORY,
	STATE.REPLACED_DIRECTORY_BY_FILE,

	# children cannot have a different state than the parent
	# so usually they should have the same direction, anyway,
	# except if the direction of the parent has been changed by the user
	STATE.NEW,
	STATE.DELETED,
}



# ---------- directions ----------

@enum.unique
class DIRECTION(enum.Enum):
	SRC_TO_DST = '>>'
	DST_TO_SRC = '<<'
	NONE = '=='
	DEFAULT = '??'


@enum.unique
class MIXED_DIRECTION(enum.Enum):
	# DirectoryComparisonNode only
	MIXED = '<>'

DIRECTION_OF_CHILDREN = typing.Union[DIRECTION, MIXED_DIRECTION]


# ---------- actions ----------
# the action describes how the destination
# is changed to match the source

@enum.unique
class ACTION(enum.Enum):
	NONE        = 'none'
	IGNORE      = 'ignore'
	CREATE      = 'create'
	DELETE      = 'delete'
	UNDO_CREATE = 'undo-create'
	UNDO_DELETE = 'undo-delete'

	# ComparisonNode only
	UPDATE         = 'update'
	DOWNGRADE      = 'downgrade'
	UNDO_UPDATE    = 'undo-update'
	UNDO_DOWNGRADE = 'undo-downgrade'

	# DirectoryComparisonNode only
	DIR_CHANGE_DESTINATION  = 'dir-change-destination'
	DIR_CHANGE_SOURCE       = 'dir-change-source'
	DIR_CHANGE_BOTH         = 'dir-change-both'
	CHANGE_DESTINATION_TYPE = 'change-destination-type'
	CHANGE_SOURCE_TYPE      = 'change-source-type'

	CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN        = 'create-directory-but-delete-some-children'
	UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN   = 'undo-delete-directory-but-delete-some-children'
	CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN = 'change-destination-type-but-delete-some-children'
	CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN      = 'change-source-type-but-delete-some-children'



class CommandNotAllowed(Exception):
	pass


class ComparisonNode(object):

	number_nodes = 0

	expand_level = Config('diff.model.expand-level', 1,
		help='0 means no directories are expanded by default, 1 means the topmost directories are expanded, 2 means the topmost directories and their direct subdirectories are expanded, ..., -1 means all directories are expanded')

	# ---------- properties ----------

	@property
	def name_src(self) -> str:
		if self.parent is None or isinstance(self.parent, MetaNode):
			return self.path_src
		elif self.type_src is TYPE.NOT_EXISTING:
			return ''
		else:
			return self.name

	@property
	def name_dst(self) -> str:
		if self.parent is None or isinstance(self.parent, MetaNode):
			return self.path_dst
		elif self.type_dst is TYPE.NOT_EXISTING:
			return ''
		else:
			return self.name


	# ---------- constructor ----------

	def __init__(self,
		name: str,
		path_src: str,
		path_dst: str,
		parent: typing.Optional['DirectoryComparisonNode'] = None,
		config_id: typing.Optional[ConfigId] = None,
		direction: typing.Optional[DIRECTION] = None,
		level: int = 0,
	) -> None:
		'''
		path_src    path_dst
		   ↓           ↓
		type_src    type_dst
		   ↘           ↙
		       state
		   /     ↓
		   | direction    ← user input
		   ↘     ↓
		       action     → output to user

		The state describes how the src has changed since the last backup (represented by dst).
		The action describes how dst needs to be changed in order to make it the same like src.

		direction is derived from the state of *this* node, regardless of it's children.
		DirectoryComparisonNode has a separate attribute direction_of_children.
		action on the other hand is not solely derived from this node's state and direction
		but from direction_of_children, too.

		STATE.MODIFIED_DIR always has DIRECTION.NONE because it means that the directory
		is existing on both sides, so as far as this node is concerned nothing needs to be done.
		The resulting action is determined by the direction_of_children.

		Example:
		state = NEW means a file or directory has been been created in src since the last backup
		(i.e. type_src = FILE|DIRECTORY and type_dst = NOT_EXISTING)
		with direction = SRC_TO_DST this is resolved by action = CREATE
		(i.e. copy the file/directory from path_src to path_dst)
		with direction = DST_TO_SRC this is resolved by action = UNDO_CREATE
		(i.e. delete the file/directory in path_src)
		with direction = NONE this is not resolved (i.e. action = IGNORE)
		'''
		if config_id is None:
			config_id = MultiConfig.default_config_id
		self.parent   = parent
		self.name     = name
		self.path_src = path_src
		self.path_dst = path_dst
		self.config_id = config_id
		self.type_src: TYPE
		self.type_dst: TYPE
		self.error_src: typing.Optional[str] = None
		self.error_dst: typing.Optional[str] = None
		self.state: STATE
		self.default_direction: DIRECTION
		self.direction: DIRECTION
		self.action: ACTION
		self.listener_direction_changed: typing.Optional[typing.Callable[[], None]] = None
		self.level = level

		if direction is not None:
			self.direction = direction

		type(self).number_nodes += 1
		self.update()


	# ---------- update ----------

	def set_direction_changed_listener(self, listener: typing.Callable[[], None]) -> None:
		self.listener_direction_changed = listener

	def notify_direction_changed(self) -> None:
		if self.listener_direction_changed is not None:
			self.listener_direction_changed()


	# ---------- mappings ----------

	state_direction_map = MultiDictConfig('diff.model.default-direction', {
		STATE.SAME    : DIRECTION.SRC_TO_DST,
		STATE.NEW     : DIRECTION.SRC_TO_DST,
		STATE.DELETED : DIRECTION.SRC_TO_DST,
		STATE.NEWER   : DIRECTION.SRC_TO_DST,
		STATE.OLDER   : DIRECTION.SRC_TO_DST,
	}, ignore_keys={STATE.MODIFIED_DIR}, allowed_values=(DIRECTION.SRC_TO_DST, DIRECTION.DST_TO_SRC, DIRECTION.NONE))

	direction_state_action_map = {
		DIRECTION.SRC_TO_DST : {
			STATE.SAME    : ACTION.NONE,
			STATE.NEW     : ACTION.CREATE,
			STATE.DELETED : ACTION.DELETE,
			STATE.NEWER   : ACTION.UPDATE,
			STATE.OLDER   : ACTION.DOWNGRADE,
		},
		DIRECTION.DST_TO_SRC : {
			STATE.SAME    : ACTION.NONE,
			STATE.NEW     : ACTION.UNDO_CREATE,
			STATE.DELETED : ACTION.UNDO_DELETE,
			STATE.NEWER   : ACTION.UNDO_UPDATE,
			STATE.OLDER   : ACTION.UNDO_DOWNGRADE,
		},
		DIRECTION.NONE : {
			STATE.SAME    : ACTION.NONE,
			STATE.NEW     : ACTION.IGNORE,
			STATE.DELETED : ACTION.IGNORE,
			STATE.NEWER   : ACTION.IGNORE,
			STATE.OLDER   : ACTION.IGNORE,
		},
	}


	# ---------- update ----------

	def update(self) -> None:
		self.type_src = TYPE.from_path(self.path_src)
		self.type_dst = TYPE.from_path(self.path_dst)

		if self.type_src is TYPE.DIRECTORY or self.type_dst is TYPE.DIRECTORY:
			self.convert_to_directory_node()
		else:
			self.convert_to_file_node()

		if self.type_src is TYPE.NOT_EXISTING and self.type_dst is TYPE.NOT_EXISTING:
			self.state = STATE.SAME
		elif self.type_src is TYPE.NOT_EXISTING:
			self.state = STATE.DELETED
		elif self.type_dst is TYPE.NOT_EXISTING:
			self.state = STATE.NEW
		else:
			self.type_specific_update()

		self.update_direction()

	def convert_to_directory_node(self) -> None:
		self.__class__ = DirectoryComparisonNode
		self.children: typing.List[ComparisonNode] = []
		self.statistics = Statistics()
		self.loaded_children = False
		self.direction_of_children: DIRECTION_OF_CHILDREN
		self.is_expanded: bool

	def convert_to_file_node(self) -> None:
		pass

	def type_specific_update(self) -> None:
		if filecmp.cmp(self.path_src, self.path_dst):
			state = STATE.SAME
		elif os.path.getmtime(self.path_src) < os.path.getmtime(self.path_dst):
			state = STATE.OLDER
		else:
			state = STATE.NEWER
		self.state = state

	def update_direction(self) -> None:
		self.default_direction = self.state_direction_map[self.state]
		if not hasattr(self, 'direction'):
			self.direction = self.default_direction
		self.update_action()

	def update_action(self) -> None:
		self.action = self.direction_state_action_map[self.direction][self.state]


	# ---------- setters ----------

	def toggle_direction(self) -> None:
		if self.direction is DIRECTION.SRC_TO_DST:
			self.set_direction_recursively(DIRECTION.DST_TO_SRC)
		else:
			self.set_direction_recursively(DIRECTION.SRC_TO_DST)

	def set_direction_recursively(self, direction: DIRECTION, *, update_parent_now: bool = True) -> None:
		if direction is DIRECTION.DEFAULT:
			direction = self.default_direction

		if self.direction is not direction:
			if update_parent_now:
				self.check_new_direction(direction)
			self.direction = direction
			self.update_action()
			self.notify_direction_changed()
			if update_parent_now:
				self.update_parent_recursively()

	def check_new_direction(self, direction: DIRECTION) -> None:
		# The following tables show which directions are allowed depending on the direction of a parent and it's state.
		# The first line indicates the state of the parent `parent.state`.
		# The rows indicate direction of the parent `parent.direction`.
		# The columns indicate the direction of the child `direction` (which is checked for validity here).
		#
		# NEW | REPLACED_FILE_BY_DIRECTORY
		#          c > x    c / x    c < x
		# d > x    ok       ok       ok
		# d / x    no       ok       ok
		# d < x    no       no       ok
		#
		# DELETED | REPLACED_DIRECTORY_BY_FILE
		#          x > c    x / c    x < c
		# x > d    ok       no       no
		# x / d    ok       ok       no
		# x < d    ok       ok       ok

		if direction is DIRECTION.DEFAULT:
			return

		parent = self.parent
		while True:
			if parent is None or isinstance(parent, MetaNode):
				break
			if parent.state is STATE.NEW or parent.state is STATE.REPLACED_FILE_BY_DIRECTORY:
				if direction is DIRECTION.DST_TO_SRC:
					pass
				elif direction is DIRECTION.NONE:
					if parent.direction is DIRECTION.DST_TO_SRC:
						raise CommandNotAllowed('you cannot ignore the child if the creation of the parent directory is undone')
				else:
					assert direction is DIRECTION.SRC_TO_DST
					if parent.direction is not DIRECTION.SRC_TO_DST:
						raise CommandNotAllowed('you cannot create the child without creating the parent directory')
				break
			if parent.state is STATE.DELETED or parent.state is STATE.REPLACED_DIRECTORY_BY_FILE:
				if direction is DIRECTION.SRC_TO_DST:
					pass
				elif direction is DIRECTION.NONE:
					if parent.direction is DIRECTION.SRC_TO_DST:
						raise CommandNotAllowed('you cannot ignore the child if the parent directory is deleted')
				else:
					assert direction is DIRECTION.DST_TO_SRC
					if parent.direction is not DIRECTION.DST_TO_SRC:
						raise CommandNotAllowed('you cannot undo the deletion of the child without undoing the deletion of the parent directory')
				break
			parent = parent.parent

	def update_parent_recursively(self) -> None:
		if self.parent is not None:
			self.parent.update_direction()
			self.parent.notify_direction_changed()
			self.parent.update_parent_recursively()

	def ignore(self) -> None:
		self.set_direction_recursively(DIRECTION.NONE)

	def unignore(self) -> None:
		self.set_direction_recursively(DIRECTION.DEFAULT)

	def toggle_ignore(self) -> None:
		if self.direction is DIRECTION.NONE:
			self.unignore()
		else:
			self.ignore()


	# ---------- getters ----------

	def has_children(self) -> bool:
		return False

	def has_direction_been_changed(self) -> bool:
		if self.state == STATE.SAME:
			return False
		return self.direction is not self.default_direction


	# ---------- to string ----------

	def __repr__(self) -> str:
		return '<%s object %s>' % (type(self).__name__, self.path_src)

	def __str__(self) -> str:
		return self.tostring(0)

	def tostring(self, level: int) -> str:
		width_left = 30
		indentation = level * '    '
		pattern_left = '({self.state.value}) {indentation}[{self.type_src.value}] {self.name_src} '
		#pattern_left = '{indentation}[{self.type_src}] {self.name_src} '
		pattern_right = ' {indentation}[{self.type_dst.value}] {self.name_dst}'
		level += 1

		action_symbols = {
			ACTION.NONE              : ' = ',
			ACTION.IGNORE            : ' | ',
			ACTION.CREATE            : ' >+',
			ACTION.DELETE            : ' >-',
			ACTION.UPDATE            : ' > ',
			ACTION.DOWNGRADE         : ' >!',
			ACTION.UNDO_CREATE       : '-< ',
			ACTION.UNDO_DELETE       : '+< ',
			ACTION.UNDO_UPDATE       : '!< ',
			ACTION.UNDO_DOWNGRADE    : ' < ',
			ACTION.DIR_CHANGE_DESTINATION : ' > ',
			ACTION.DIR_CHANGE_SOURCE : ' < ',
			ACTION.DIR_CHANGE_BOTH   : '> <',
			ACTION.CHANGE_DESTINATION_TYPE: ' >t',
			ACTION.CHANGE_SOURCE_TYPE: 't< ',
			ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN        : '->+',
			ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN   : '+<-',
			ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN : '->t',
			ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN      : 't<-',
		}

		ln = pattern_left.format(indentation=indentation, self=self)
		ln = ln.ljust(width_left)
		ln += action_symbols[self.action]
		ln += pattern_right.format(indentation=indentation, self=self)

		return ln


class DirectoryComparisonNode(ComparisonNode):

	# ---------- mappings ----------

	state_direction_map = ComparisonNode.state_direction_map
	state_direction_map[STATE.REPLACED_FILE_BY_DIRECTORY] = DIRECTION.SRC_TO_DST
	state_direction_map[STATE.REPLACED_DIRECTORY_BY_FILE] = DIRECTION.SRC_TO_DST
	# this entry does not really make sense it's just so that I can use super().update_direction()
	# this must be NONE because the directory exists on both sides, only the children differ
	# if set to something else the resulting ACTION may include a direction in which the children are not changed
	state_direction_map[STATE.MODIFIED_DIR] = DIRECTION.NONE

	direction_state_action_map = ComparisonNode.direction_state_action_map
	direction_state_action_map[DIRECTION.SRC_TO_DST][STATE.REPLACED_FILE_BY_DIRECTORY] = ACTION.CHANGE_DESTINATION_TYPE
	direction_state_action_map[DIRECTION.SRC_TO_DST][STATE.REPLACED_DIRECTORY_BY_FILE] = ACTION.CHANGE_DESTINATION_TYPE
	direction_state_action_map[DIRECTION.SRC_TO_DST][STATE.MODIFIED_DIR]               = ACTION.DIR_CHANGE_DESTINATION
	direction_state_action_map[DIRECTION.DST_TO_SRC][STATE.REPLACED_FILE_BY_DIRECTORY] = ACTION.CHANGE_SOURCE_TYPE
	direction_state_action_map[DIRECTION.DST_TO_SRC][STATE.REPLACED_DIRECTORY_BY_FILE] = ACTION.CHANGE_SOURCE_TYPE
	direction_state_action_map[DIRECTION.DST_TO_SRC][STATE.MODIFIED_DIR]               = ACTION.DIR_CHANGE_SOURCE
	direction_state_action_map[DIRECTION.NONE][STATE.REPLACED_FILE_BY_DIRECTORY]       = ACTION.IGNORE
	direction_state_action_map[DIRECTION.NONE][STATE.REPLACED_DIRECTORY_BY_FILE]       = ACTION.IGNORE
	direction_state_action_map[DIRECTION.NONE][STATE.MODIFIED_DIR]                     = ACTION.IGNORE


	# ---------- update ----------

	def convert_to_directory_node(self) -> None:
		pass

	def convert_to_file_node(self) -> None:
		self.__class__ = ComparisonNode  # type: ignore [assignment]
		del self.children
		del self.statistics
		del self.loaded_children
		del self.is_expanded
		del self.direction_of_children

	def type_specific_update(self) -> None:
		if self.type_src is not self.type_dst:
			if self.type_src is TYPE.FILE:
				self.state = STATE.REPLACED_DIRECTORY_BY_FILE
			else:
				self.state = STATE.REPLACED_FILE_BY_DIRECTORY
			if not getattr(self, 'is_expanded', False):
				return
		else:
			self.state = STATE.SAME
			# is updated to STATE.MODIFIED_DIR in update_children if appropriate
		self.update_children()

	def update_children(self) -> None:
		'''
		updates self.children
		if self.state is STATE.SAME update it to STATE.MODIFIED_DIR if children differ

		this does not update self.statistics, so make sure to run update_direction afterwards
		'''
		self.loaded_children = True

		if os.path.isdir(self.path_src):
			try:
				children_src = os.listdir(self.path_src)
			except PermissionError as e:
				children_src = []
				self.error_src = str(e)
		else:
			children_src = []

		if os.path.isdir(self.path_dst):
			try:
				children_dst = os.listdir(self.path_dst)
			except PermissionError as e:
				children_dst = []
				self.error_dst = str(e)
		else:
			children_dst = []

		content = set(children_src + children_dst)

		i = 0
		n = len(self.children)
		iterator_filenames = iter(sorted(content))
		try:
			filename = next(iterator_filenames)
			while i < n:
				child = self.children[i]
				# Python 3 has no cmp anymore
				if filename == child.name:
					child.update()
				elif filename < child.name:
					child = self.create_child_node(filename)
					self.children.insert(i, child)
					n += 1
				else:
					del self.children[i]
					n -= 1
					continue

				if self.state is STATE.SAME and child.state is not STATE.SAME:
					self.state = STATE.MODIFIED_DIR
				i += 1
				filename = next(iterator_filenames)

			self.children.insert(i, self.create_child_node_and_update_state(filename))
			for filename in iterator_filenames:
				self.children.append(self.create_child_node_and_update_state(filename))
		except StopIteration:
			del self.children[i:]

	def create_child_node(self, filename: str) -> ComparisonNode:
		direction = None
		if self.state in STATES_WHICH_HAND_THEIR_DIRECTION_DOWN_TO_THEIR_CHILDREN:
			direction = self.direction
		return ComparisonNode(
			parent = self,
			name = filename,
			# this addition of strings is around 8x faster than os.path.join
			path_src = self.path_src + os.sep + filename,
			path_dst = self.path_dst + os.sep + filename,
			config_id = self.config_id,
			direction = direction,
			level = self.level + 1,
		)

	def create_child_node_and_update_state(self, filename: str) -> ComparisonNode:
		node = self.create_child_node(filename)
		if self.state is STATE.SAME and node.state is not STATE.SAME:
			self.state = STATE.MODIFIED_DIR
		return node

	def update_direction(self) -> None:
		self.statistics.clear()
		for child in self.children:
			self.statistics.add(child)
		self.direction_of_children = self.statistics.get_direction()
		super().update_direction()
		self.update_is_expanded()

	def update_is_expanded(self) -> None:
		if not hasattr(self, 'is_expanded'):
			self.is_expanded = self.get_auto_is_expanded()

	def get_auto_is_expanded(self) -> bool:
		if self.expand_level >= 0 and self.level >= self.expand_level:
			return False
		if not self.loaded_children:
			return False
		return True

	def update_action(self) -> None:
		super().update_action()
		if self.direction_of_children is not self.direction and self.direction_of_children is not DIRECTION.NONE:
			# there are children which are updated in the opposite direction
			if self.action is ACTION.NONE:
				assert False
			elif self.action is ACTION.IGNORE:
				assert self.direction is DIRECTION.NONE
				assert self.state is not STATE.SAME
				# this can be STATE.MODIFIED_DIR (where direction is always NONE)
				# or one of NEW, DELETED, REPLACED_FILE_BY_DIRECTORY, REPLACED_DIRECTORY_BY_FILE
				# e.g. for NEW it's possible that the directory is not created but children are removed in src
				if self.direction_of_children is DIRECTION.SRC_TO_DST:
					self.action = ACTION.DIR_CHANGE_DESTINATION
				elif self.direction_of_children is DIRECTION.DST_TO_SRC:
					self.action = ACTION.DIR_CHANGE_SOURCE
				else:
					self.action = ACTION.DIR_CHANGE_BOTH
			elif self.action is ACTION.CREATE:
				assert self.type_src is TYPE.DIRECTORY
				assert self.type_dst is TYPE.NOT_EXISTING
				assert self.direction is DIRECTION.SRC_TO_DST
				self.action = ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN
			elif self.action is ACTION.DELETE:
				assert self.type_src is TYPE.NOT_EXISTING
				assert self.type_dst is TYPE.DIRECTORY
				assert self.direction is DIRECTION.SRC_TO_DST
				assert False, 'children cannot be updated in the opposite direction in this case'
			elif self.action is ACTION.UNDO_CREATE:
				assert self.type_src is TYPE.DIRECTORY
				assert self.type_dst is TYPE.NOT_EXISTING
				assert self.direction is DIRECTION.DST_TO_SRC
				assert False, 'children cannot be updated in the opposite direction in this case'
			elif self.action is ACTION.UNDO_DELETE:
				assert self.type_src is TYPE.NOT_EXISTING
				assert self.type_dst is TYPE.DIRECTORY
				assert self.direction is DIRECTION.DST_TO_SRC
				self.action = ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN

			elif self.action is ACTION.DIR_CHANGE_DESTINATION:
				self.action = ACTION.DIR_CHANGE_BOTH
			elif self.action is ACTION.DIR_CHANGE_SOURCE:
				self.action = ACTION.DIR_CHANGE_BOTH
			elif self.action is ACTION.CHANGE_DESTINATION_TYPE:
				self.action = ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN
			elif self.action is ACTION.CHANGE_SOURCE_TYPE:
				self.action = ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN

			else:
				assert False, self.action


	# ---------- setters ----------

	def set_direction_recursively(self, direction: DIRECTION, *, update_parent_now: bool = True) -> None:
		if update_parent_now:
			self.check_new_direction(direction)
		for child in self.children:
			child.set_direction_recursively(direction, update_parent_now=False)
		if self.state is not STATE.MODIFIED_DIR:
			if direction is DIRECTION.DEFAULT:
				direction = self.default_direction
			self.direction = direction
		self.update_direction()
		self.notify_direction_changed()
		if update_parent_now:
			self.update_parent_recursively()

	def toggle_direction(self) -> None:
		if self.state == STATE.MODIFIED_DIR:
			if self.direction_of_children is DIRECTION.SRC_TO_DST:
				self.set_direction_recursively(DIRECTION.DST_TO_SRC)
			else:
				self.set_direction_recursively(DIRECTION.SRC_TO_DST)
		else:
			super().toggle_direction()

	def toggle_ignore(self) -> None:
		if self.state == STATE.MODIFIED_DIR:
			if self.statistics[ACTION.IGNORE] > 0:
				self.unignore()
			else:
				self.ignore()
		else:
			super().toggle_ignore()


	# ---------- getters ----------

	def has_children(self) -> bool:
		return True

	def has_child_direction_been_changed(self) -> bool:
		return self.statistics.has_child_direction_been_changed


	# ---------- subclass specific interface ----------

	def set_expanded(self, value: bool) -> None:
		if not self.is_expanded and not self.children:
			self.update_children()
			self.update_direction() # to update statistics
		self.is_expanded = value


	# ---------- to string ----------

	def tostring(self, level: int) -> str:
		lines = [super().tostring(level)]

		level += 1
		for child in self.children:
			lines.append(child.tostring(level))

		return '\n'.join(lines)


class MetaNode(DirectoryComparisonNode):

	def __init__(self, config_id: typing.Optional[ConfigId] = None) -> None:
		if config_id is None:
			config_id = MultiConfig.default_config_id
		self.config_id = config_id
		self.parent   = None
		self.path_src = 'Source'
		self.path_dst = 'Destination'
		self.type_src = TYPE.DIRECTORY
		self.type_dst = TYPE.DIRECTORY
		self.state: STATE
		self.default_direction = DIRECTION.NONE
		self.direction = DIRECTION.NONE
		self.action: ACTION
		self.listener_direction_changed: typing.Optional[typing.Callable[[], None]] = None
		self.level = -1

	def load(self, paths: typing.Sequence[typing.Tuple[ConfigId, str, str]]) -> None:
		self.children = []
		for config_id, src, dst in paths:
			name = os.path.split(src)[0]
			self.children.append(ComparisonNode(name, src, dst, parent=self, config_id=config_id))

		self.loaded_children = True
		self.statistics = Statistics()
		self.update_state()
		self.update_direction()  # set direction, statistics and action

	def update_state(self) -> None:
		self.state = STATE.SAME if all(child.state == STATE.SAME for child in self.children) else STATE.MODIFIED_DIR

	def update_statistics(self) -> None:
		self.statistics.clear()
		self.state = STATE.SAME
		for child in self.children:
			self.statistics.add(child)
			if child.state is not STATE.SAME:
				self.state = STATE.MODIFIED_DIR

	def update(self) -> None:
		for child in self.children:
			child.update()
		self.update_state()
		self.update_statistics()


class Statistics(object):

	__slots__ = ('statistics', 'has_child_direction_been_changed', 'number_nodes_with_errors')


	def __init__(self) -> None:
		self.statistics: typing.Dict[ACTION, int] = dict()
		self.has_child_direction_been_changed = False
		self.number_nodes_with_errors = 0

	def clear(self) -> None:
		self.statistics = {}
		self.has_child_direction_been_changed = False
		self.number_nodes_with_errors = 0

	def add(self, other: ComparisonNode) -> None:
		if isinstance(other, DirectoryComparisonNode):
			for action, number in other.statistics.statistics.items():
				self.statistics[action] = self.statistics.get(action, 0) + number
			self.number_nodes_with_errors += other.statistics.number_nodes_with_errors

			if other.has_child_direction_been_changed():
				self.has_child_direction_been_changed = True

		action = other.action
		number = 1
		self.statistics[action] = self.statistics.get(action, 0) + number

		if other.error_src or other.error_dst:
			self.number_nodes_with_errors += 1

		if other.has_direction_been_changed():
			self.has_child_direction_been_changed = True


	ACTIONS_CHANGE_DESTINATION = (
		ACTION.CREATE,
		ACTION.DELETE,
		ACTION.UPDATE,
		ACTION.DOWNGRADE,
		ACTION.DIR_CHANGE_DESTINATION,
		ACTION.DIR_CHANGE_BOTH,
		ACTION.CHANGE_DESTINATION_TYPE,
		ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN,
		ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN,
	)
	ACTIONS_CHANGE_SOURCE = (
		ACTION.UNDO_CREATE,
		ACTION.UNDO_DELETE,
		ACTION.UNDO_UPDATE,
		ACTION.UNDO_DOWNGRADE,
		ACTION.DIR_CHANGE_SOURCE,
		ACTION.DIR_CHANGE_BOTH,
		ACTION.CHANGE_SOURCE_TYPE,
		ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN,
		ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN,
	)

	def get_direction(self) -> DIRECTION_OF_CHILDREN:
		changed_source = any(True for a in self.ACTIONS_CHANGE_SOURCE if self.statistics.get(a, 0) > 0)
		changed_destination = any(True for a in self.ACTIONS_CHANGE_DESTINATION if self.statistics.get(a, 0) > 0)
		if changed_destination and changed_source:
			return MIXED_DIRECTION.MIXED
		elif changed_destination:
			return DIRECTION.SRC_TO_DST
		elif changed_source:
			return DIRECTION.DST_TO_SRC
		else:
			return DIRECTION.NONE

	def __getitem__(self, key: ACTION) -> int:
		return self.statistics.get(key, 0)


def count_files(path: str) -> int:
	out = 0
	for fn in os.listdir(path):
		ffn = path + os.path.sep + fn
		if os.path.isdir(ffn):
			try:
				out += count_files(ffn)
			except PermissionError:
				pass
		else:
			out += 1
	return out


if __name__ == '__main__':
	src = r'test/src'
	dst = r'test/dst'
	tree = ComparisonNode(
		name     = os.path.split(src)[1],
		path_src = src,
		path_dst = dst)

	print('Tree: \n%s' % tree)
