import time
import pandas as pd
from pathlib import Path
from functools import wraps
import json


def dump_to_file(dumpfolder="/tmp", filename="", fileformat="csv", timestamp=True):
    """Write output to 'path' in 'format' if output is
    a dataframe. If you want to specify the name of the
    output file then set a .name attribute on the
    dataframe.
    """

    def actual_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            if kwargs.get("filename"):
                filename = kwargs.get("filename")
            if kwargs.get("fileformat"):
                fileformat = kwargs.get("fileformat")

            if isinstance(args[0], pd.DataFrame) and getattr(args[0], "name", None):
                name = getattr(args[0], "name", None)
            elif filename:
                name = filename
            else:
                name = int(time.time())

            results = f(*args, **kwargs)
            if not Path(dumpfolder).exists():
                print(f"Path: {dumpfolder} does not exist")

            if isinstance(results, pd.DataFrame):
                # Create the filename
                if name and not timestamp:
                    dump_path = Path(dumpfolder, f"{name}.{fileformat}")
                elif name and timestamp:
                    dump_path = Path(
                        dumpfolder, f"{name}_{int(time.time())}.{fileformat}"
                    )
                else:
                    dump_path = Path(dumpfolder, f"{int(time.time())}.{fileformat}")

                # Write file
                if fileformat == "csv":
                    results.to_csv(dump_path)
                elif fileformat == "json":
                    results.to_json(dump_path)
                elif fileformat == "dict":
                    with dump_path.open("w") as file:
                        file.write(json.dumps(results.to_dict("records")))
            print(f"dump to: {dump_path}")
            return results

        return wrapper

    return actual_decorator
