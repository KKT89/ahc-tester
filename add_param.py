import os
import sys
import argparse
import json
import config as config_module

def main(config):
    parser = argparse.ArgumentParser(
        description="Script to add or update a parameter in a JSON file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands: add or delete")

    # Subparser for the 'add' command
    # Positional arguments: name, type, lower_bound, upper_bound, value (all required)
    add_parser = subparsers.add_parser("add", help="Add or update a parameter")
    add_parser.add_argument("name", type=str, help="Parameter name (e.g., TEMP0)")
    add_parser.add_argument("type", type=str, choices=["int", "float"], help="Parameter type (int or double)")
    add_parser.add_argument("lower", type=str, help="Lower bound for the parameter")
    add_parser.add_argument("upper", type=str, help="Upper bound for the parameter")
    add_parser.add_argument("value", type=str, help="Parameter value")

    # Subparser for the 'delete' command
    delete_parser = subparsers.add_parser("delete", help="Delete a parameter")
    delete_parser.add_argument("name", type=str, help="Parameter name to delete")

    args = parser.parse_args()
    WORK_DIR = config["work_dir"]
    PARAM_FILE = os.path.join(WORK_DIR, config["param_json_file"])

    # パラメータファイルを読み込む
    if os.path.exists(PARAM_FILE):
        with open(PARAM_FILE, "r") as f:
            params = json.load(f)
    else:
        params = {}

    if args.command == "delete":
        if args.name in params:
            del params[args.name]
            with open(PARAM_FILE, "w") as f:
                json.dump(params, f, indent=4)
        else:
            print(f"Error: Parameter '{args.name}' does not exist.")
    elif args.command == 'add':
        if args.type == "int":
            try:
                args.lower = int(args.lower)
                args.upper = int(args.upper)
                args.value = int(args.value)
            except ValueError:
                print("Error: lower, upper, and value must be integers.")
                sys.exit(1)
        else:
            try:
                args.lower = float(args.lower)
                args.upper = float(args.upper)
                args.value = float(args.value)
            except ValueError:
                print("Error: lower, upper, and value must be floating-point numbers.")
                sys.exit(1)

        if args.lower > args.upper:
            print("Error: lower must be less than upper.")
            sys.exit(1)
        if args.value < args.lower or args.value > args.upper:
            print("Error: value must be between lower and upper.")
            sys.exit(1)

        # パラメータを追加または更新
        params[args.name] = {
            "type": args.type,
            "lower": args.lower,
            "upper": args.upper,
            "value": args.value,
            "used": True
        }

        # パラメータをファイルに書き込む
        with open(PARAM_FILE, "w") as f:
            json.dump(params, f, indent=4)


if __name__ == "__main__":
    config = config_module.load_config()
    main(config)
