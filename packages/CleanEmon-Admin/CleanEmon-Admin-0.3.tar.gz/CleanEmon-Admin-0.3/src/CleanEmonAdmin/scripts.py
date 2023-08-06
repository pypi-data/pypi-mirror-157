from typing import Dict
import os
import json

from CleanEmonCore import CONFIG_FILE
from CleanEmonCore.models import EnergyData
from CleanEmonCore.CouchDBAdapter import CouchDBAdapter

from CleanEmonBackend.lib.DBConnector import fetch_data, send_data

from . import __path__

adapter = CouchDBAdapter(CONFIG_FILE)


def get_static_file(filename):
    return os.path.join(__path__[0], "static", filename)


def _prompt_meta() -> Dict:
    data = {}
    while True:
        key = input("Type something to create a new field or press <enter> to end this process: ")
        if not key:
            break

        value = input(f"Value for {key}: ")
        data[key] = value

    return data


def add_meta():
    while True:
        print("Meta-data Prompt...")

        data = _prompt_meta()
        print(json.dumps(data, indent=4))

        ans = input("Are those meta-data correct? [y/n] ")
        if not ans or ans in "nN":
            "Aborting meta-data..."
        elif ans in "yY":
            name = adapter.create_raw_document("meta", initial_data=data)
            if name:
                print("Meta-data where uploaded successfully!")
            else:
                print("Couldn't upload meta-data, probably due to a name conflict.")
                print(f"Please make sure there is no other meta-data file already uploaded on {adapter.db}")
            break
        else:
            print("Invalid option. Aborting meta-data...")


def _reset_file(date: str):
    print(f"Working on {date}")

    print("Fetching old data...")
    data = fetch_data(date, from_cache=False)

    print("Cleaning data...")
    clean_energy_data = []
    for record in data.energy_data:

        # Do not "clean" the records with no original_timestamp. Just use them straight away.
        if "original_timestamp" not in record:
            clean_energy_data.append(record)

        else:
            # Do not use this record if its "original_timestamp" value is null.
            # It doesn't belong to the original dataset
            if not record["original_timestamp"]:
                continue

            # Clean the record and use it
            else:
                # Copy all values except for the predicted ones (pred_*)
                clean_record = {key: value for key, value in record.items() if "pred_" not in key}

                # Exchange "original_timestamp" with "timestamp" if there is such distinction, and delete the
                # unneeded one
                if "original_timestamp" in clean_record:
                    clean_record["timestamp"] = clean_record["original_timestamp"]
                    del clean_record["original_timestamp"]

                clean_energy_data.append(clean_record)

    new_data = EnergyData(date, clean_energy_data)

    print("Updating CouchDB...")
    send_data(date, new_data)
    print("Done")


def reset_file(*dates: str, no_prompt=False):
    if not no_prompt:
        print(f"You are working on database: {adapter.db}")

    for date in dates:
        if no_prompt:
            ans = True
        else:
            ans = input(f"Proceed with {date}? (<enter>: no) ")

        if ans:
            _reset_file(date)
        else:
            break


def create_database(name: str, no_prompt=False):
    if not no_prompt:
        ans = True
    else:
        print(f"You are working on database: {adapter.db}")
        ans = input(f"Create database named \"{name}\"? (<enter>: no) ")

    if ans:
        if adapter.create_database(name):
            adapter.db = name
            print("Database has been successfully created!")
            print("Please update manually the config file to reflect the changes")

            views_file = get_static_file("design.api.json")
            with open(views_file, "r") as f_in:
                views = json.load(f_in)
            adapter.create_raw_document("_design/api", initial_data=views)
            print("Views have been successfully initialized!")
        else:
            print("Couldn't create the specified database")
    else:
        print("Aborting...")
        return
