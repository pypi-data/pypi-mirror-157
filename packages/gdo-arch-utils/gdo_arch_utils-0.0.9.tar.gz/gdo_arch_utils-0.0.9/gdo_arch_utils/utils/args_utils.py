import argparse
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


class ArgsUtils:
    @staticmethod
    def get_parsed_args(args_dict):
        logger.info("Loading args..")
        parser = argparse.ArgumentParser(description="")
        for args_name, args_properties in args_dict.items():
            ArgsUtils._add_arg_to_parser(
                parser=parser,
                args_name=args_name,
                args_properties=args_properties,
            )

        return parser.parse_args()

    @staticmethod
    def _add_arg_to_parser(parser, args_name, args_properties):
        args_properties_keys = args_properties.keys()
        match args_properties_keys:
            case args_properties_keys if "nargs" in args_properties_keys:
                parser.add_argument(
                    args_name, nargs=args_properties["nargs"]
                )
            case args_properties_keys if "default" in args_properties_keys:
                parser.add_argument(
                    args_name,
                    type=args_properties["type"],
                    required=args_properties["required"],
                    default=args_properties["default"],
                )
            case args_properties_keys if "type" in args_properties_keys:
                parser.add_argument(
                    args_name,
                    type=args_properties["type"],
                    required=args_properties["required"],
                )
