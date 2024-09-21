import json
import logging
from typing import Dict
from zipfile import ZipFile

import numpy as np
import pandas as pd

from natug import structures
from natug.constants.directions import DOWN, UP
from natug.structures.domains import Domains
from natug.structures.points.point import PointStyles
from natug.utils import hex_to_rgb

logger = logging.getLogger(__name__)


class FileHandler:
    def __init__(self, runner: "Runner"):
        self.runner = runner

    def save(self, filename: str):
        """
        Save the current state of the program.
        """
        logger.debug(f"Saving program state to %s...", {filename})

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

            # Create a reference to the current double helices
            double_helices = self.runner.managers.double_helices.current

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
                items_by_type[structures.points.Nucleoside]
            )
            NEMids_df = structures.points.nemid.to_df(
                items_by_type[structures.points.NEMid]
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
            package.writestr(
                "strands/strands.csv",
                strands_df.to_csv(index=False),
            )

            package.mkdir("helices")
            # Repeat the same process that we just did for strands for double helices
            double_helices_json = double_helices.to_json()
            double_helices_json = json.dumps(double_helices_json, indent=4)
            package.writestr("helices/double_helices.json", double_helices_json)
            double_helices_df = structures.helices.double_helix.to_df(
                double_helices.double_helices
            )
            package.writestr(
                "helices/double_helices.csv",
                double_helices_df.to_csv(index=False),
            )
            helices_df = structures.helices.helix.to_df(tuple(double_helices.helices()))
            package.writestr(
                "helices/helices.csv",
                helices_df.to_csv(index=False),
            )

            logger.info("Saved program state to %s.", filename)

    def load(self, filename: str, clear_nucleic_acid_profiles: bool = True):
        """
        Load the current state of the program.

        Args:
            filename: The file to load a program state from.
            clear_nucleic_acid_profiles: Whether to clear the nucleic acid profiles from
                 the respective panel.
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
                        )
                    )
                    nucleic_acid_profiles[nucleic_acid_profile.name] = (
                        nucleic_acid_profile
                    )
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
                    hex_to_rgb(row["style:outline"].split(",")[0].strip()),
                    float(row["style:outline"].split(",")[1].strip().replace("px", "")),
                )
                styles = PointStyles(
                    symbol=row["style:symbol"],
                    size=row["style:size"],
                    rotation=row["style:rotation"],
                    fill=hex_to_rgb(row["style:fill"]),
                    outline=outline,
                )
                styles.state = row["style:state"]
                return styles

            # Load all the nucleosides
            with package.open("points/nucleosides.csv") as file:
                df = pd.read_csv(file)
                df["data:direction"] = df["data:direction"].map(
                    {"UP": UP, "DOWN": DOWN}
                )

                # Build Nucleoside objects from the dataframe rows
                for index, row in df.iterrows():
                    base = row["nucleoside:base"]
                    nucleoside = structures.points.nucleoside.Nucleoside(
                        uuid=row["uuid"],
                        x_coord=row["data:x_coord"],
                        z_coord=row["data:z_coord"],
                        angle=row["data:angle"],
                        direction=row["data:direction"],
                        domain=domains.domains()[row["data:domain"]],
                        base=base if isinstance(base, str) else None,
                        styles=row_to_point_styles(row),
                    )
                    items_by_uuid[row["uuid"]] = nucleoside

            # Load all individual NEMids
            with package.open("points/NEMids.csv") as file:
                df = pd.read_csv(file)
                df = df.where(pd.notnull(df), None)
                df["data:direction"] = df["data:direction"].map(
                    {"UP": UP, "DOWN": DOWN}
                )

                # First create all the NEMids without their juncmates, since we may
                # not be able to fetch certain juncmates (since we're creating NEMids
                # as we go)
                NEMids = np.empty(len(df), dtype=object)
                for index, row in df.iterrows():
                    juncmate = row.get("NEMid:juncmate")

                    # Create the NEMid object from the dataframe row
                    NEMid_ = structures.points.nemid.NEMid(
                        uuid=row["uuid"],
                        x_coord=row["data:x_coord"],
                        z_coord=row["data:z_coord"],
                        direction=row["data:direction"],
                        angle=row["data:angle"],
                        domain=domains.domains()[row["data:domain"]],
                        juncmate=juncmate,
                        junction=row["NEMid:junction"],
                        junctable=row["NEMid:junctable"],
                        styles=row_to_point_styles(row),
                    )
                    NEMids[index] = NEMid_
                    items_by_uuid[NEMid_.uuid] = NEMid_

                # Now change the juncmate uuids to actual NEMid objects
                for NEMid_ in NEMids:
                    if NEMid_.juncmate is not None:
                        NEMid_.juncmate = items_by_uuid[NEMid_.juncmate]

            # Load nick objects
            with package.open("points/nicks.csv") as file:
                df = pd.read_csv(file)
                nicks = []
                for index, row in df.iterrows():
                    nick = structures.points.nick.Nick(
                        uuid=row["uuid"],
                        original_item=items_by_uuid[row["data:original_item"]],
                    )
                    items_by_uuid[row["uuid"]] = nick
                    nicks.append(nick)

            # Load the Linkage objects
            with package.open("strands/linkages.csv") as file:
                df = pd.read_csv(file)
                df = df.where(pd.notnull(df), None)
                for index, row in df.iterrows():
                    items = [
                        structures.points.nucleoside.Nucleoside(
                            base=None if base == "X" else base
                        )
                        for base in row["data:sequence"]
                    ]

                    styles = structures.strands.linkage.LinkageStyles(
                        color=hex_to_rgb(row["style:color"]),
                        thickness=row["style:thickness"],
                        init_reset=False,
                    )

                    coord_one = tuple(map(float, row["data:coord_one"].split(", ")))
                    coord_two = tuple(map(float, row["data:coord_two"].split(", ")))

                    linkage = structures.strands.linkage.Linkage(
                        coord_one=coord_one,
                        coord_two=coord_two,
                        uuid=row["uuid"],
                        items=items,
                        inflection=row["data:inflection"],
                        styles=styles,
                    )
                    linkage.styles.linkage = linkage
                    linkage.styles.reset()

                    items_by_uuid[row["uuid"]] = linkage

            # Load each individual Strands
            with package.open("strands/strands.csv") as file:
                df = pd.read_csv(file)

                for index, row in df.iterrows():
                    items = [
                        items_by_uuid[uuid] for uuid in row["data:items"].split("; ")
                    ]

                    styles = structures.strands.strand.StrandStyles()
                    styles.color.from_str(row["style:color"], valuemod=hex_to_rgb)
                    styles.thickness.from_str(
                        str(row["style:thickness"]), valuemod=float
                    )
                    styles.highlighted = row["style:highlighted"]

                    strand = structures.strands.strand.Strand(
                        uuid=row["uuid"],
                        items=items,
                        name=row["name"],
                        styles=styles,
                        closed=row["data:closed"],
                    )
                    strand.styles.strand = strand
                    items_by_uuid[row["uuid"]] = strand

            # Load the Strands container
            with package.open("strands/strands.json") as file:
                loaded = json.load(file)
                strands = structures.strands.Strands(
                    name=loaded["name"],
                    uuid=loaded["uuid"],
                    nucleic_acid_profile=nucleic_acid_profile,
                    strands=[items_by_uuid[uuid] for uuid in loaded["data:strands"]],
                )
                strands.nicks = nicks

            # Build the strand by using the items in the main hash table
            for strand in strands:
                for item in strand:
                    item.strand = strand
                strand.strands = strands

            # Load the helices and double helices
            with package.open("helices/helices.csv") as file:
                df = pd.read_csv(file)
                for index, row in df.iterrows():
                    helix = structures.helices.Helix(
                        uuid=row["uuid"],
                        double_helix=row["data:double_helix"],  # Placeholder UUID
                        direction=UP if row["data:direction"] == "UP" else DOWN,
                    )
                    helix.data.x_coords = np.array(
                        tuple(map(float, row["data:x_coords"].split(";"))), dtype=float
                    )
                    helix.data.z_coords = np.array(
                        tuple(map(float, row["data:z_coords"].split(";"))), dtype=float
                    )
                    helix.data.angles = np.array(
                        tuple(map(float, row["data:angles"].split(";"))), dtype=float
                    )
                    helix.data.points = np.array(
                        tuple(
                            map(
                                lambda point: items_by_uuid[point],
                                row["data:points"].split(";"),
                            )
                        ),
                        dtype=object,
                    )
                    for i, point in enumerate(helix.data.points):
                        if isinstance(
                            point,
                            structures.points.nick.Nick,
                        ):
                            point.original_item.helix = helix
                            point.original_item.helical_index = i
                        else:
                            point.helix = helix
                            point.helical_index = i
                    assert isinstance(helix.data.x_coords[0], float)
                    assert len(helix.data.x_coords) > 0
                    items_by_uuid[row["uuid"]] = helix

            # Load the double helix objects
            with package.open("helices/double_helices.csv") as file:
                df = pd.read_csv(file)
                for index, row in df.iterrows():
                    double_helix = structures.helices.double_helix.DoubleHelix(
                        uuid=row["uuid"],
                        domain=domains.domains()[row["data:domain"]],
                        up_helix=items_by_uuid[row["data:up_helix"]],
                        down_helix=items_by_uuid[row["data:down_helix"]],
                        # Resizing the helices makes them the correct GenerationCount
                        # size. However, it also wipes all the current data in the
                        # helices. Since they should be the right size, we can skip
                        # this on-init resize.
                        resize_helices=False,
                    )
                    # assert (
                    #     len(double_helix.up_helix.data)
                    #     == sum(double_helix.up_helix.counts) * 2 - 1
                    # )
                    double_helix.up_helix.double_helix = double_helix
                    double_helix.down_helix.double_helix = double_helix
                    items_by_uuid[row["uuid"]] = double_helix

            # Load the overall DoubleHelices container for all the DoubleHelixes that
            # contain Helix objects
            with package.open("helices/double_helices.json") as file:
                loaded = json.load(file)
                listed_double_helices = []
                for uuid in loaded["items"]:
                    listed_double_helices.append(items_by_uuid[uuid])

                double_helices = structures.helices.DoubleHelices(
                    uuid=loaded["uuid"],
                    nucleic_acid_profile=nucleic_acid_profile,
                    double_helices=listed_double_helices,
                )
                items_by_uuid[loaded["uuid"]] = double_helices

            # Update the currently displayed nucleic acid profile and the possible
            # nucleic acid profiles to those found in the file
            try:
                self.runner.managers.nucleic_acid_profile.current.update(
                    nucleic_acid_profile
                )
            except AttributeError:
                self.runner.managers.nucleic_acid_profile.current = nucleic_acid_profile

            profile_manager = (
                self.runner.window.config.panel.nucleic_acid.profile_manager
            )
            if clear_nucleic_acid_profiles:
                for name, profile in tuple(profile_manager.profiles.items()):
                    profile_manager.delete(name, override=True)
            for name, profile in tuple(nucleic_acid_profiles.items()):
                profile_manager.save(name, override=True)
            profile_manager.dumper(nucleic_acid_profile)
            new_profile_name = filename.split()[-1]
            profile_manager.profile_chooser.setCurrentText(new_profile_name)

            # Update the program's current domains and strands to those found in the
            # file
            try:
                self.runner.managers.domains.current.update(domains)
            except AttributeError:
                self.runner.managers.domains.current = domains
            self.runner.managers.strands.current = strands
            self.runner.managers.double_helices.current = double_helices
            self.runner.window.config.panel.domains.dump_domains(domains)

            # Refresh the side view plot and the top view plot
            self.runner.window.side_view.refresh()
            self.runner.window.top_view.refresh()

            return lambda callbacks: [callback() for callback in callbacks]
