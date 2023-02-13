import logging
from zipfile import ZipFile

import structures.points.nucleoside
import structures.points.nemid
import structures.points.nick
import structures.points.nick
import structures.strands.linkage
import structures.profiles.nucleic_acid_profile

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
            file.mkdir("nucleic_acid_profiles")
            file.mkdir("domains")
            file.mkdir("strands")
            file.mkdir("strands/points")

            # Save the nucleic acid profiles
            current_nucleic_acid_profile = (
                self.runner.managers.nucleic_acid_profile.current
            )
            current_nucleic_acid_profile.name = "Restored"
            structures.profiles.nucleic_acid_profile.export(
                [
                    current_nucleic_acid_profile,
                    *self.runner.managers.nucleic_acid_profile.profiles,
                ],
                None,
            )

            # Sort all the items by type
            items_by_type = {
                structures.points.Nucleoside: [],
                structures.points.NEMid: [],
                structures.points.nick.Nick: [],
                structures.strands.linkage.Linkage: [],
            }
            for item in self.runner.managers.strands.current.items():
                items_by_type[type(item)].append(item)

            # Some NEMids may not be included via strand.items, if they are nicks
            # that had the items removed. So, we'll add them manually.
            for nick in self.runner.managers.strands.current.nicks:
                items_by_type[structures.points.nemid.NEMid].append(nick.original_item)

            # Create dataframes of all the different types of strand items
            nucleoside_df = structures.points.nucleoside.export(
                items_by_type[structures.points.nucleoside.Nucleoside], None
            )
            NEMid_df = structures.points.nemid.export(
                items_by_type[structures.points.nemid.NEMid], None
            )
            nick_df = structures.points.nick.export(
                items_by_type[structures.points.nick.Nick], None
            )
            linkage_df = structures.strands.linkage.export(
                items_by_type[structures.strands.linkage.Linkage], None
            )

            # Save the dataframes to the zip file
            file.writestr("strands/points/nucleosides.csv", nucleoside_df.to_csv())
            file.writestr("strands/points/NEMids.csv", NEMid_df.to_csv())
            file.writestr("strands/points/nicks.csv", nick_df.to_csv())
            file.writestr("strands/linkages.csv", linkage_df.to_csv())

            logger.info("Saved program state to %s", filename)

    def load(self, filename: str):
        """
        Load the current state of the program.
        """
