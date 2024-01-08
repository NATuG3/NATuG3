from unittest import TestCase

import pandas as pd

from structures.domains import Domains, Subunit, Domain
from structures.profiles import NucleicAcidProfile


class TestDomains(TestCase):
    sample_nucleic_acid_profile = NucleicAcidProfile()

    def test_update(self):
        domains = Domains.dummy()
        self.assertEqual(domains.subunit.domains[0].theta_m_multiple, 4)

        new_domains = Domains.dummy()
        new_domains.subunit.domains[0].theta_m_multiple += 1
        self.assertEqual(new_domains.subunit.domains[0].theta_m_multiple, 5)

        self.assertNotEqual(
            domains.subunit.domains[0].theta_m_multiple,
            new_domains.subunit.domains[0].theta_m_multiple,
        )
        domains.update(new_domains)
        self.assertEqual(domains.subunit.domains[0].theta_m_multiple, 5)

    def test_to_df(self):
        domains = Domains.dummy()
        domains = domains.to_df().to_dict()

        expected = {
            "data:m": [4, 4],
            "data:left_helix_joints": ["UP", "UP"],
            "data:right_helix_joints": ["UP", "UP"],
            "data:up_helix_counts": ["1&1&1", "1&1&1"],
            "data:down_helix_counts": ["1&1&1", "1&1&1"],
            "data:symmetry": [1, None],
            "data:antiparallel": [False, None],
            "uuid": [None, None],
        }
        expected = pd.DataFrame(expected)
        expected = expected.to_dict()

        domains["uuid"] = expected["uuid"]

        self.assertEqual(str(domains), str(expected))

    def test_dummy(self):
        dummy_domains = Domains.dummy()
        self.assertEqual(dummy_domains.count, 2)
        self.assertEqual(
            len([subunit.domains for subunit in dummy_domains.subunits()]), 1
        )
        self.assertEqual(dummy_domains.domains(), dummy_domains.subunit.domains)

    def test_from_df(self):
        domains_df = pd.read_csv("../../saves/domains/hexagon.csv")
        domains = Domains.from_df(domains_df, self.sample_nucleic_acid_profile)

        self.assertEqual(domains.count, 6)
        self.assertEqual(domains.symmetry, 1)
        self.assertTrue(domains.antiparallel)
        self.assertTrue(domains.closed())

        for i in range(domains.count):
            domain = domains.subunit.domains[i]

            self.assertEqual(domain.theta_m_multiple, 7)

            self.assertEqual(domain.left_helix_joint, i % 2)
            self.assertEqual(domain.right_helix_joint, i % 2)

            self.assertEqual(domain.up_helix_count.to_str(), "0-60-0")
            self.assertEqual(domain.down_helix_count.to_str(), "0-60-0")

    def test_top_view(self):
        domains_df = pd.read_csv("../../saves/domains/hexagon.csv")
        domains = Domains.from_df(domains_df, self.sample_nucleic_acid_profile)
        top_view_coords = domains.top_view()

        def round_coord(coord):
            return round(coord, 3)

        self.assertEqual(round_coord(top_view_coords[0][0]), -1.1)
        self.assertEqual(round_coord(top_view_coords[0][1]), 1.905)
        self.assertEqual(round_coord(top_view_coords[1][0]), 0)
        self.assertEqual(round_coord(top_view_coords[1][1]), 0)
        self.assertEqual(round_coord(top_view_coords[2][0]), 2.2)
        self.assertEqual(round_coord(top_view_coords[2][1]), 0)
        self.assertEqual(round_coord(top_view_coords[3][0]), 3.3)
        self.assertEqual(round_coord(top_view_coords[3][1]), 1.905)
        self.assertEqual(round_coord(top_view_coords[4][0]), 2.2)
        self.assertEqual(round_coord(top_view_coords[4][1]), 3.811)
        self.assertEqual(round_coord(top_view_coords[5][0]), 0)
        self.assertEqual(round_coord(top_view_coords[5][1]), 3.811)
        self.assertEqual(round_coord(top_view_coords[6][0]), -1.1)
        self.assertEqual(round_coord(top_view_coords[6][1]), 1.905)
        self.assertEqual(round_coord(top_view_coords[7][0]), 0)
        self.assertEqual(round_coord(top_view_coords[7][1]), 0)

    def testClosed(self):
        for should_close in ("hexagon", "star", "triangle"):
            domains_df = pd.read_csv(f"../../saves/domains/{should_close}.csv")
            domains = Domains.from_df(domains_df, self.sample_nucleic_acid_profile)
            self.assertTrue(domains.closed())

        domains_df = pd.read_csv(f"../../saves/domains/heart.csv")
        domains = Domains.from_df(domains_df, self.sample_nucleic_acid_profile)
        self.assertFalse(domains.closed())

        domains = Domains.dummy()
        self.assertFalse(domains.closed())

    def test_subunit(self):
        domains = Domains.dummy()

        self.assertEqual(domains.subunit.domains[0].theta_m_multiple, 4)
        self.assertEqual(domains.subunit.domains[1].theta_m_multiple, 4)
        self.assertEqual(len(domains.subunit.domains), 2)

        self.assertIsInstance(domains.subunit, Subunit)
        self.assertIsInstance(domains.subunit.domains, list)
        self.assertIsInstance(domains.subunit.domains[0], Domain)

    def test_count(self):
        domains = Domains.dummy()
        self.assertEqual(domains.count, 2)

        domains = Domains.dummy(theta_m_multiples=[4, 2, 4, 2])
        self.assertEqual(domains.count, 4)

        domains = Domains.dummy(theta_m_multiples=[4, 2, 4, 2, 4, 2])
        self.assertEqual(domains.count, 6)

    def test_subunits(self):
        domains = Domains.dummy()
        self.assertEqual(len(domains.subunits()), 1)

        domains = Domains.dummy(theta_m_multiples=[4, 2, 4, 2])
        self.assertEqual(len(domains.subunits()), 1)

        domains = Domains.dummy(theta_m_multiples=[4, 2, 4, 2, 4, 2], symmetry=2)
        self.assertEqual(len(domains.subunits()), 2)

    def test_domains(self):
        domains = Domains.dummy()
        self.assertEqual(len(domains.domains()), 2)

        domains = Domains.dummy(theta_m_multiples=[4, 2, 4, 22])
        self.assertEqual(len(domains.domains()), 4)
        self.assertEqual(domains.domains()[0].theta_m_multiple, 4)
        self.assertEqual(domains.domains()[1].theta_m_multiple, 2)
        self.assertEqual(domains.domains()[2].theta_m_multiple, 4)
        self.assertEqual(domains.domains()[3].theta_m_multiple, 22)

        domains = Domains.dummy(theta_m_multiples=[4, 2, 4, 2, 4, 2], symmetry=6)
        self.assertEqual(len(domains.domains()), 36)

    def test_destroy_symmetry(self):
        domains = Domains.dummy(theta_m_multiples=[4, 2], symmetry=2)
        self.assertEqual(domains.symmetry, 2)
        with_symmetry_array = domains.domains()

        def assert_correct_pattern(array):
            self.assertEqual(array[0].theta_m_multiple, 4)
            self.assertEqual(array[1].theta_m_multiple, 2)
            self.assertEqual(array[2].theta_m_multiple, 4)
            self.assertEqual(array[3].theta_m_multiple, 2)

        # Assert that the domains are symmetric with 2-fold symmetry
        self.assertEqual(len(with_symmetry_array), 4)
        assert_correct_pattern(with_symmetry_array)

        # Destroy the symmetry
        domains.destroy_symmetry()
        without_symmetry_array = domains.domains()

        # Assert that the domains are no longer symmetric, but still are the same
        self.assertEqual(len(without_symmetry_array), 4)
        self.assertEqual(domains.symmetry, 1)
        assert_correct_pattern(without_symmetry_array)
