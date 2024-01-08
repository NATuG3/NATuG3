from unittest import TestCase

from structures.domains import Domains
from structures.profiles import NucleicAcidProfile


class TestDomains(TestCase):
    sample_nucleic_acid_profile = NucleicAcidProfile()

    def test_update(self):
        self.fail()

    def test_to_df(self):
        self.fail()

    def test_dummy(self):
        dummy_domains = Domains.dummy(TestDomains.sample_nucleic_acid_profile)
        self.assertEqual(dummy_domains.count, 2)
        self.assertEqual(len([subunit.domains for subunit in dummy_domains.subunits()]), 1)
        self.assertEqual(dummy_domains.domains(), dummy_domains.subunit.domains)

    def test_from_df(self):
        self.fail()

    def test_top_view(self):
        self.fail()

    def testClosed(self):
        self.fail()

    def test_subunit(self):
        self.fail()

    def test_count(self):
        self.fail()

    def test_subunits(self):
        self.fail()

    def test_domains(self):
        self.fail()

    def test_destroy_symmetry(self):
        self.fail()

    def test_invert(self):
        self.fail()
