import json

import logging
from contextlib import suppress
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
from structures.strands.strand import StrandStyle
from utils import hex_to_rgb

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

                for index, row in df.iterrows():
                    row: Dict[str, object]

                    nucleic_acid_profile = (
                        structures.profiles.nucleic_acid_profile.NucleicAcidProfile(
                            name=str(row["name"]),
                            uuid=str(row["uuid"]),
                            D=float(row["data:D"]),
                            H=float(row["data:H"]),
                            g=float(row["data:g"]),
                            T=int(row["data:T"]),
                            B=int(row["data:B"]),
                            Z_c=float(row["data:Z_c"]),
                            Z_mate=float(row["data:Z_mate"]),
                            theta_s=float(row["data:theta_s"]),
                        )
                    )
                    nucleic_acid_profiles[
                        nucleic_acid_profile.name
                    ] = nucleic_acid_profile
                    items_by_uuid[row["uuid"]] = nucleic_acid_profile

            nucleic_acid_profile = nucleic_acid_profiles["Restored"]

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
                outline = (
                    hex_to_rgb(str(row["style:outline"]).split(",")[0].strip()),
                    float(row["style:outline"].split(",")[1].strip().replace("px", "")),
                )

                styles = PointStyles(
                    symbol=row["style:symbol"],
                    size=int(row["style:size"]),
                    rotation=float(row["style:rotation"]),
                    fill=hex_to_rgb(str(row["style:fill"])),
                    outline=outline,
                )
                styles.state = row["style:state"]
                return styles

            with package.open("points/nucleosides.csv") as file:
                df = pd.read_csv(file)
                for index, row in df.iterrows():
                    nucleoside = structures.points.nucleoside.Nucleoside(
                        uuid=str(row["uuid"]),
                        x_coord=float(row["data:x-coord"]),
                        z_coord=float(row["data:z-coord"]),
                        angle=float(row["data:angle"]),
                        domain=domains.domains()[int(row["data:domain"])],
                        base=str(row["nucleoside:base"]),
                        styles=row_to_point_styles(row),
                    )
                    items_by_uuid[row["uuid"]] = nucleoside

            with package.open("points/NEMids.csv") as file:
                df = pd.read_csv(file)

                # First create all the NEMids without their juncmates, since we may
                # not be able to fetch certain juncmates (since we're creating NEMids
                # as we go)
                for index, row in df.iterrows():
                    NEMid_ = structures.points.nemid.NEMid(
                        uuid=str(row["uuid"]),
                        x_coord=float(row["data:x-coord"]),
                        z_coord=float(row["data:z-coord"]),
                        angle=float(row["data:angle"]),
                        domain=domains.domains()[int(row["data:domain"])],
                        juncmate=None,
                        junction=row["NEMid:junction"] == "TRUE",
                        junctable=row["NEMid:junctable"] == "TRUE",
                        styles=row_to_point_styles(row),
                    )
                    items_by_uuid[row["uuid"]] = NEMid_

                df.where(df.notnull(), None)

                # Then re-iterate through the dataframe and set the juncmates of the
                # NEMids that we just created
                for index, row in df.iterrows():
                    with suppress(KeyError):
                        items_by_uuid[row["uuid"]].juncmate = items_by_uuid[
                            row["NEMid:juncmate"]
                        ]

            with package.open("points/nicks.csv") as file:
                df = pd.read_csv(file)
                nicks = []
                for index, row in df.iterrows():
                    nick = structures.points.nick.Nick(
                        uuid=str(row["uuid"]),
                        original_item=items_by_uuid[str(row["data:original_item"])],
                        previous_item=items_by_uuid[str(row["data:previous_item"])],
                        next_item=items_by_uuid[str(row["data:next_item"])],
                    )
                    items_by_uuid[row["uuid"]] = nick
                    nicks.append(nick)

            with package.open("strands/linkages.csv") as file:
                df = pd.read_csv(file)
                for index, row in df.iterrows():
                    items = [
                        structures.points.nucleoside.Nucleoside(base=base)
                        for base in str(row["data:sequence"])
                    ]

                    styles = structures.strands.linkage.LinkageStyles(
                        color=hex_to_rgb(str(row["style:color"])),
                        thickness=int(row["style:thickness"]),
                    )

                    linkage = structures.strands.linkage.Linkage(
                        coord_one=str(row["data:coord_one"]).split(", ")[0],
                        coord_two=str(row["data:coord_two"]).split(", ")[-1],
                        uuid=str(row["uuid"]),
                        items=items,
                        inflection=row["data:inflection"],
                        styles=styles,
                    )

                    items_by_uuid[row["uuid"]] = linkage

            with package.open("strands/strands.csv") as file:
                df = pd.read_csv(file)
                for index, row in df.iterrows():
                    items = [
                        items_by_uuid[str(uuid)]
                        for uuid in str(row["data:items"]).split("; ")
                    ]

                    styles = structures.strands.strand.StrandStyles()
                    styles.color.from_str(str(row["style:color"]), valuemod=hex_to_rgb)
                    styles.thickness.from_str(
                        str(row["style:thickness"]), valuemod=float
                    )
                    styles.highlighted = row["style:highlighted"] == "TRUE"

                    items_by_uuid[row["uuid"]] = structures.strands.strand.Strand(
                        uuid=str(row["uuid"]),
                        items=items,
                        name=str(row["name"]),
                        styles=styles,
                        closed=row["data:closed"] == "TRUE",
                    )

            with package.open("strands/strands.json") as file:
                loaded = json.load(file)
                strands = structures.strands.Strands(
                    name=str(loaded["name"]),
                    uuid=str(loaded["uuid"]),
                    nucleic_acid_profile=nucleic_acid_profile,
                    strands=[
                        items_by_uuid[str(uuid)] for uuid in loaded["data:strands"]
                    ],
                )
                for strand in strands:
                    strand.strands = strands
                strands.nicks = nicks

            for strand in strands:
                for item in strand:
                    if isinstance(item, structures.points.point.Point):
                        item.strand = strand

            self.runner.managers.nucleic_acid_profile.current.update(
                nucleic_acid_profile
            )
            profile_manager = (
                self.runner.window.config.panel.nucleic_acid.profile_manager
            )
            for name, profile in tuple(profile_manager.profiles.items()):
                profile_manager.delete(name, override=True)
            for name, profile in tuple(nucleic_acid_profiles.items()):
                profile_manager.save(name, override=True)
            profile_manager.dumper(nucleic_acid_profile)
            new_profile_name = filename.split("/")[-1]
            profile_manager.profile_chooser.setCurrentText(new_profile_name)

            self.runner.managers.domains.current.update(domains)
            self.runner.window.config.panel.domains.table.dump_domains(domains)
            self.runner.window.config.panel.domains.table_refresh()
            self.runner.window.config.panel.domains.settings_refresh()

            self.runner.managers.strands.current = strands
            self.runner.window.side_view.refresh()
            self.runner.window.top_view.refresh()
