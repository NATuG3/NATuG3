import json

import logging
from zipfile import ZipFile

import structures.points.nucleoside
import structures.points.nemid
import structures.points.nick
import structures.points.nick
import structures.strands.linkage
import structures.profiles.nucleic_acid_profile
import structures.domains
import structures.helices

logger = logging.getLogger(__name__)


class FileHandler:
    def __init__(self, runner: "Runner"):
        self.runner = runner

    def save(self, filename: str):
        """
        Save the current state of the program.
        """
        logger.debug(f"Saving program state to {filename}...")

        with ZipFile(filename, "w") as file:
            # Save the domains
            domains_df = self.runner.managers.domains.current.to_df()
            file.writestr("domains.csv", domains_df.to_csv())

            # Save the nucleic acid profiles
            nucleic_acid_profiles_df = [
                self.runner.managers.nucleic_acid_profile.current
            ]
            # Save the current nucleic acid profile
            nucleic_acid_profiles_df[-1].name = "Restored"
            # Add all the other nucleic acid profiles except the previously restored one
            for (
                nucleic_acid_profile
            ) in self.runner.managers.nucleic_acid_profile.profiles.values():
                if (nucleic_acid_profile.name != "Restored") and (
                    nucleic_acid_profile not in nucleic_acid_profiles_df
                ):
                    nucleic_acid_profiles_df.append(nucleic_acid_profile)
            # Export the nucleic acid profiles to a dataframe
            nucleic_acid_profiles_df = structures.profiles.nucleic_acid_profile.to_df(
                nucleic_acid_profiles_df
            )
            # Save the dataframe to the zip file
            file.writestr(
                "nucleic_acid_profiles.csv", nucleic_acid_profiles_df.to_csv()
            )

            # Create a reference to the current strands
            strands = self.runner.managers.strands.current

            # Sort all the items by type
            items_by_type = {
                structures.points.Nucleoside: [],
                structures.points.NEMid: [],
                structures.points.nick.Nick: [],
                structures.strands.linkage.Linkage: [],
            }
            for item in strands.items():
                items_by_type[type(item)].append(item)

            # Some NEMids may not be included via strand.items, if they are nicks
            # that had the items removed. So, we'll add them manually.
            for nick in strands.nicks:
                items_by_type[structures.points.nemid.NEMid].append(nick.original_item)

            # Create dataframes of all the different types of strand items
            nucleosides_df = structures.points.nucleoside.to_df(
                items_by_type[structures.points.nucleoside.Nucleoside]
            )
            NEMids_df = structures.points.nemid.to_df(
                items_by_type[structures.points.nemid.NEMid]
            )
            nicks_df = structures.points.nick.to_df(
                items_by_type[structures.points.nick.Nick]
            )
            linkages_df = structures.strands.linkage.to_df(
                items_by_type[structures.strands.linkage.Linkage]
            )

            # Create a directory for the points
            file.mkdir("points")

            # Save the various strand items to the file
            file.writestr("points/nucleosides.csv", nucleosides_df.to_csv())
            file.writestr("points/NEMids.csv", NEMids_df.to_csv())
            file.writestr("points/nicks.csv", nicks_df.to_csv())
            file.writestr("points/linkages.csv", linkages_df.to_csv())

            file.mkdir("strands")
            # Save the strands themselves, and the Strands container object
            strands_json = strands.to_json()
            strands_json = json.dumps(strands_json, indent=4)
            file.writestr("strands/strands.json", strands_json)
            strands_df = structures.strands.strand.to_df(strands.strands)
            file.writestr("strands/strands.csv", strands_df.to_csv(index=False))

            file.mkdir("double_helices")
            # Save the double helices container's data to a file
            double_helices_json = strands.double_helices.to_json()
            double_helices_json = json.dumps(double_helices_json, indent=4)
            file.writestr("double_helices/double_helices.json", double_helices_json)

            # Save the actual double helices's data to a file
            double_helices_df = structures.helices.double_helix.to_df(
                strands.double_helices.double_helices
            )
            file.writestr(
                "double_helices/double_helices.csv",
                double_helices_df.to_csv(index=False),
            )

            logger.info("Saved program state to %s.", filename)

    def load(self, filename: str):
        """
        Load the current state of the program.
        """
