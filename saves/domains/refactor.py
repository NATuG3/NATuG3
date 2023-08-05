import os
from contextlib import suppress

import pandas as pd

"""
Tool to port old csv formatted domains saves to the new format. The new format 
includes a "uuid" for each domain, and has slightly different column names.
"""


def main():
    # Iterate through all csv files in the active filepath
    for file in os.listdir():
        if file.endswith(".csv"):
            # For each file in the filepath, load the csv file into a pandas
            # dataframe and then make the needed changes to the dataframe to port it
            # to the new format.
            df = pd.read_csv(file)

            df = df.rename(
                columns={
                    "data:m": "data:m",
                    "data:left_helix_joints": "data:left_helix_joints",
                    "data:right_helix_joints": "data:right_helix_joints",
                    "data:left_helix_count": "data:up_helix_counts",
                    "data:other_helix_count": "data:down_helix_counts",
                    "data:symmetry": "data:symmetry",
                    "data:antiparallel": "data:antiparallel",
                }
            )

            # Remove the old uuid column if it exists and add a new one no matter what
            with suppress(KeyError):
                del df["uuid"]
            # df.insert(0, "uuid", [uuid1() for _ in range(len(df))])  # type: ignore

            # Save the dataframe as a csv file with the same name as the original file
            df.to_csv(file, index=False)

            # Print a message to the console to show that the file has been refactored
            print(f"Refactored {file}.")


if __name__ == "__main__":
    main()
