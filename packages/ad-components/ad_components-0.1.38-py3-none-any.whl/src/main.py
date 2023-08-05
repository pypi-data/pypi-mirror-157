#!/usr/bin/env python3
import logging
import pkg_resources
from argparse import ArgumentParser, HelpFormatter

from storage import upload, download
from version import __version__ as component_version


LOGGING_FORMAT = (
    "[%(asctime)s] %(name)s [%(levelname)7s] (%(filename)s:%(lineno)s) --- %(message)s"
)

logger = logging.getLogger(f"Storage Component Main")

STORAGE_FUNCTION_MAP = {"download": download, "upload": upload}


class CustomHelpFormatter(HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)

        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)

        return ", ".join(action.option_strings) + " " + args_string


def process_arguments():
    """
    Defining and parsing the command-line arguments
    """

    parser = ArgumentParser(
        description="Storage Access reusable component.",
        formatter_class=lambda prog: CustomHelpFormatter(prog),
    )

    subparsers = parser.add_subparsers(dest="component", help='components utilities.')

    storage_parser = subparsers.add_parser('storage', help='storage Access reusable component.')
    # Add Common actions
    storage_parser.add_argument(
        "action", choices=STORAGE_FUNCTION_MAP.keys(), help="action to be performed on data."
    )

    action_arguments = storage_parser.add_argument_group("action arguments")
    action_arguments.add_argument(
        "--src",
        "-r",
        metavar="PATH",
        type=str,
        required=True,
        help="path of file to perform action on.",
    )
    action_arguments.add_argument(
        "--dest",
        "-d",
        metavar="PATH",
        type=str,
        required=True,
        help="object's desired full path in the destination.",
    )
    action_arguments.add_argument(
        "--binding",
        "-b",
        metavar="NAME",
        type=str,
        default="s3-state",
        help="the name of the binding as defined in the components.",
    )

    dapr_arguments = storage_parser.add_argument_group("dapr arguments")
    dapr_arguments.add_argument(
        "--timeout",
        "-t",
        metavar="SEC",
        type=int,
        default=300,
        help="value in seconds we should wait for sidecar to come up.",
    )

    # Generic configurations
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="run the script in debug mode.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Storage Component {component_version} \n (Dapr: {pkg_resources.get_distribution('dapr').version})",
    )

    return parser.parse_args(), parser


def main():
    args, parser = process_arguments()

    logging_kwargs = {"format": LOGGING_FORMAT}
    if args.verbose:
        logging_kwargs["level"] = logging.DEBUG

    logging.basicConfig(**logging_kwargs)

    if args.component == "storage":
        if args.action not in STORAGE_FUNCTION_MAP.keys():
            parser.error(f"Unrecognized action or not implemented: {args.action}")

        logger.debug(f"Invoking '{args.action}' action on '{args.binding}' S3 binding...")

        action = STORAGE_FUNCTION_MAP[args.action]
        action(
            args.src,
            args.dest,
            binding_name=args.binding,
            timeout=args.timeout,
        )
    else:
        parser.error(f"Unrecognized component or not implemented: {args.component}")


if __name__ == "__main__":
    exit(main())
