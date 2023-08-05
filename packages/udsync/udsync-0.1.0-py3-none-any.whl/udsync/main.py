#!/usr/bin/env python3

'''
An interactive urwid based directory synchronizer
'''

__version__ = '0.1.0'

import argparse
import typing

from . import ui
from . import configfile


def list_backup_plans() -> None:
	for fn in ui.App.list_backup_plans():
		print(fn)


def print_version() -> None:
	print(__version__)


def main(args_list: typing.Optional[typing.Sequence[str]] = None) -> None:
	p = argparse.ArgumentParser(prog=configfile.Exporter.APP_NAME)
	p.add_argument('-v', '--version', action='store_true', help='show the version number and exit')
	p.add_argument('-l', '--list-backup-plans', action='store_true')
	p.add_argument('-e', '--edit-backup-plan')
	p.add_argument('-d', '--delete-backup-plan')
	p.add_argument('src', nargs='?')
	p.add_argument('dst', nargs='?')

	args = p.parse_args(args_list)
	if args.version:
		print_version()
		return
	elif args.list_backup_plans:
		list_backup_plans()
		return
	elif args.edit_backup_plan is not None:
		ui.App.edit_backup_plan(args.edit_backup_plan)
		return
	elif args.delete_backup_plan is not None:
		ui.App.delete_backup_plan(args.delete_backup_plan)
		return

	app = ui.App(args.src, args.dst)
	app.mainloop()


if __name__ == '__main__':
	main()
