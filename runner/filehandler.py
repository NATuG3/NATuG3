import json

import logging
from typing import Dict
from zipfile import ZipFile

import pandas as pd

import structures.points.nucleoside
import structures.points.nemid
import structures.points.nick
import structures.points.nick
import structures.strands.linkage
import structures.profiles.nucleic_acid_profile
import structures.domains
import structures.helices
from structures.domains import Domains
from structures.points.point import PointStyles

logger = logging.getLogger(__name__)


class FileHandler:
    def __init__(self, runner: "Runner"):
        self.runner = runner

    def save(self, filename: str):
        """
        Save the current state of the program.
        """
        logger.debug(f"Saving program state to {filename}...")

        with ZipFile(filename, "w") as package:
            # Save the domains
            domains_df = self.runner.managers.domains.current.to_df()
            package.writestr("domains.csv", domains_df.to_csv())

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
            package.writestr(
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
            nicks_df = structures.points.nick.to_df(strands.nicks)
            linkages_df = structures.strands.linkage.to_df(
                items_by_type[structures.strands.linkage.Linkage]
            )

            # Create a directory for the points
            package.mkdir("points")
            package.mkdir("strands")

            # Save the various strand items to the file
            package.writestr("points/nucleosides.csv", nucleosides_df.to_csv())
            package.writestr("points/NEMids.csv", NEMids_df.to_csv())
            package.writestr("points/nicks.csv", nicks_df.to_csv())
            package.writestr("strands/linkages.csv", linkages_df.to_csv())

            # Save the strands themselves, and the Strands container object
            strands_json = strands.to_json()
            strands_json = json.dumps(strands_json, indent=4)
            package.writestr("strands/strands.json", strands_json)
            strands_df = structures.strands.strand.to_df(strands.strands)
            package.writestr("strands/strands.csv", strands_df.to_csv(index=False))

            package.mkdir("double_helices")
            # Save the double helices container's data to a file
            double_helices_json = strands.double_helices.to_json()
            double_helices_json = json.dumps(double_helices_json, indent=4)
            package.writestr("double_helices/double_helices.json", double_helices_json)

            # Save the actual double helices's data to a file
            double_helices_df = structures.helices.double_helix.to_df(
                strands.double_helices.double_helices
            )
            package.writestr(
                "double_helices/double_helices.csv",
                double_helices_df.to_csv(index=False),
            )

            logger.info("Saved program state to %s.", filename)

    def load(self, filename: str):
        """
        Load the current state of the program.
        """
        items_by_uuid = {}
        nucleic_acid_profiles: Dict[str, structures.NucleicAcidProfile] = {}
        domains: Domains
        double_helices: structures.helices.DoubleHelices
        strands: structures.strands.Strands

        with ZipFile(filename, "r") as package:
            with package.open("nucleic_acid_profiles.csv") as file:
                df = pd.read_csv(file)

                for row in df.iterrows():
                    row: Dict[str, object]

                    nucleic_acid_profile = (
                        structures.profiles.nucleic_acid_profile.NucleicAcidProfile(
                            name=row["name"],  # type: ignore
                            uuid=row["uuid"],  # type: ignore
                            D=row["D"],  # type: ignore
                            H=row["H"],  # type: ignore
                            g=row["g"],  # type: ignore
                            T=row["T"],  # type: ignore
                            B=row["B"],  # type: ignore
                            Z_c=row["Z_c"],  # type: ignore
                            Z_mate=row["Z_mate"],  # type: ignore
                            theta_s=row["theta_s"],  # type: ignore
                        )
                    )
                    nucleic_acid_profiles[
                        nucleic_acid_profile.name
                    ] = nucleic_acid_profile
                    items_by_uuid[row["uuid"]] = nucleic_acid_profile

            with package.open("domains.csv") as file:
                domains = structures.domains.Domains.from_df(
                    pd.read_csv(file), nucleic_acid_profile
                )
                for domain in domains.domains():
                    items_by_uuid[domain.uuid] = domain

            def row_to_point_styles(row: pd.Series) -> PointStyles:
                """
                Convert a row from the point styles dataframe to a PointStyle object.
                """
                return PointStyles(
                    symbol=row["styles:symbol"],  # type: ignore
                    size=row["styles:size"],  # type: ignore
                    rotation=row["styles:rotation"],  # type: ignore
                    fill=row["styles:fill"],  # type: ignore
                    outline=outline,  # type: ignore
                    state=row["styles:state"],  # type: ignore
                )

            with package.open("points/nucleosides.csv") as file:
                df = pd.read_csv(file)
                for row in df:
                    nucleoside = structures.points.nucleoside.Nucleoside(
                        uuid=row["uuid"],  # type: ignore
                        x_coord=row["data:x-coord"],  # type: ignore
                        z_coord=row["data:z-coord"],  # type: ignore
                        angle=row["data:angle"],  # type: ignore
                        base=row["data:base"],  # type: ignore
                        styles=row_to_point_styles(row),  # type: ignore
                    )
                    items_by_uuid[row["uuid"]] = nucleoside

            with package.open("points/NEMids.csv") as file:
                df = pd.read_csv(file)

                # First create all the NEMids without their juncmates, since we may
                # not be able to fetch certain juncmates (since we're creating NEMids
                # as we go)
                for row in df.iterrows():
                    outline = (
                        tuple(row["styles:outline"].split(",")[0].strip()),
                        float(row["styles:outline"].split(",")[1].strip()),
                    )

                    styles = PointStyles(
                        symbol=row["styles:symbol"],  # type: ignore
                        size=row["styles:size"],  # type: ignore
                        rotation=row["styles:rotation"],  # type: ignore
                        fill=row["styles:fill"],  # type: ignore
                        outline=outline,  # type: ignore
                        styles=row_to_point_styles(row),  # type: ignore
                    )

                    NEMid_ = structures.points.nemid.NEMid(
                        uuid=row["uuid"],  # type: ignore
                        x_coord=row["data:x-coord"],  # type: ignore
                        z_coord=row["data:z-coord"],  # type: ignore
                        angle=row["data:angle"],  # type: ignore
                        juncmate=None,
                        junction=row["NEMid:junction"],  # type: ignore
                        junctable=row["NEMid:junctable"],  # type: ignore
                        styles=styles,
                    )
                    items_by_uuid[row["uuid"]] = NEMid_

                # Then re-iterate through the dataframe and set the juncmates of the
                # NEMids that we just created
                for row in df.iterrows():
                    if row["NEMid:juncmate"] is not None:
                        items_by_uuid[row["uuid"]].juncmate = items_by_uuid[
                            row["NEMid:juncmate"]
                        ]

            with package.open("points/nicks.csv") as file:
                df = pd.read_csv(file)
                for row in df.iterrows():
                    nick = structures.points.nick.Nick(
                        uuid=row["uuid"],
                        previous_item=items_by_uuid[row["data:previous-item"]],
                        next_item=items_by_uuid[row["data:next-item"]],
                    )
                    items_by_uuid[row["uuid"]] = nick

            with package.open("strands/linkages.csv") as file:
                df = pd.read_csv(file)
                for row in df.iterrows():
                    items = [
                        structures.points.nucleoside.Nucleoside(base=row["base"])
                        for base in row["sequence"]
                    ]

                    styles = structures.strands.linkage.LinkageStyles(
                        color=row["styles:color"],  # type: ignore
                        width=row["styles:width"],  # type: ignore
                    )

                    linkage = structures.strands.linkage.Linkage(
                        uuid=row["uuid"],
                        items=items,
                        inflection=row["inflection"],  # type: ignore
                        basic_plot_points=row["data:plot_points"],  # type: ignore
                        styles=styles,
                    )
                    items_by_uuid[row["uuid"]] = linkage
