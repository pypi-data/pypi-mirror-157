import argparse

from .scripts import add_meta
from .scripts import reset_file
from .scripts import create_database
from .generate_config import generate_config

parser = argparse.ArgumentParser(prog="CleanEmonAdmin",
                                 description="A set of useful admin-tools for the CleanEmon ecosystem")
subparsers = parser.add_subparsers(help="commands", dest="command")

# Create DB
create_db_parser = subparsers.add_parser("create-db")
create_db_parser.add_argument("name", help="the name of the new database")

# Export Config
export_config = subparsers.add_parser("export-config")
export_config.add_argument("section", nargs="?", choices=["db", "emon"],
                           help="default=all, db=CouchDB related, emon=EmonPi related")

# Add Meta Data
subparsers.add_parser("add-meta", help="Add custom meta-data to current database")

# Reset File
reset_date_parser = subparsers.add_parser("reset-date", help="Discard clean data and revert to primitive data")
reset_date_parser.add_argument("dates", nargs="*",
                               help="list of dates (YYYY-MM-DD) to be reset")
parser.add_argument("--no-safe", action="store_false", help="prompt before proceeding with critical actions")

args = parser.parse_args()
print(args)

if args.command == "create-db":
    create_database(args.name, no_prompt=args.no_safe)

elif args.command == "export-config":
    generate_config(section=args.section)

elif args.command == "add-meta":
    add_meta()

elif args.command == "reset-date":
    if args.dates:
        reset_file(args.dates, no_prompt=args.no_safe)
    else:
        print("You should provide at least one date")
