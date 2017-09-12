
"""Benchmark tool
"""


import argparse
from argparse import RawTextHelpFormatter
import pkg_resources


class Benchmark(object):
    def __init__(self):
        self.subcommands = {}
        for ep in pkg_resources.iter_entry_points("benchmarktool"):
            self.subcommands[ep.name] = ep.load()

    def _main(self, args):
        cmdname = args.command[0]
        cmdclass = self.subcommands.get(cmdname, None)
        if cmdclass is None:
            parser.error("Unknown subcommand %s" % cmdname)
        else:
            cmd = cmdclass(args.commandargs)
            try:
                return cmd.main()
            except RuntimeError as exc:
                return -1

    def subcommandHelp(self):
        text = ["Available subcommands:\n",
                ]
        for subc in sorted(self.subcommands.items()):
            text.append("{0: <12} {1}".format(subc[0], subc[1].__doc__))
        return "\n".join(text)


def main():
    bm = Benchmark()
    global parser
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument("command", nargs=1, help="Run a the specified subcommand. {}".format(bm.subcommandHelp()))
    parser.add_argument("commandargs", nargs=argparse.REMAINDER, help="Argument list for the command to run.")
    # Grab the self.args from argv
    args = parser.parse_args()
    return bm._main(args)
