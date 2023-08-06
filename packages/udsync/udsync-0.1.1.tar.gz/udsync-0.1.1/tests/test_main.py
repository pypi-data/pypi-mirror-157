#!/usr/bin/env pytest

import enum

from udsync import main
from udsync import config

# the setup of other tests clear this dict so I need to save the values before any tests run
config_instances = tuple(config.Config.instances.values())

def test_all_types_used_for_configs_have_names() -> None:
	for c in config_instances:
		t = c.type
		if t == list:
			t = c.item_type
		if t in config.ConfigExporter.primitive_types:
			continue
		if issubclass(t, enum.Enum):
			continue
		assert hasattr(t, 'type_name'), c.key
