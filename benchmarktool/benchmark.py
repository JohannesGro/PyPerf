
"""Benchmark tool
"""
import argparse
import sys

import pkg_resources


class Benchmark(object):
    """Class for loading the console scripts and providing a CLI interface."""

    def __init__(self):
        self.subcommands = {}
        # get console scripts
        for ep in pkg_resources.iter_entry_points("benchmarktool"):
            self.subcommands[ep.name] = ep.load()

    def _main(self, args):
        cmdname = args.__dict__.pop('command', None)
        cmdclass = self.subcommands.get(cmdname, None)
        if cmdclass is None:
            parser.error("Unknown subcommand %s" % cmdname)
        else:
            cmd = cmdclass(args)
            try:
                return cmd.main()
            except RuntimeError as exc:
                print(exc)


def main():
    bm = Benchmark()
    global parser
    parser = argparse.ArgumentParser(description=__doc__)
    # create a subparser for the subcommands
    subparsers = parser.add_subparsers(help='Available subcommands')
    # create a argparser for each subcommand/console script
    for subc in sorted(bm.subcommands.items()):
        # add parser with name and description
        command = subparsers.add_parser(subc[0], description=subc[1].__doc__)
        # set command for operation call
        command.set_defaults(command=subc[0])
        # iterate through the list of parameter of the console script and add these parameter
        # to the current arg parser.
        for action in subc[1].parser._actions:
            if type(action) == argparse._StoreAction or type(action) == argparse._StoreTrueAction:
                command._add_action(action)
    # Grab the self.args from argv
    args = parser.parse_args()
    return bm._main(args)
