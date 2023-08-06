from io import StringIO
import unittest
from unittest import TestCase
from random import choice

import pandas as pd
from pandas.testing import assert_index_equal

# from dataset import constants
from mavecore.validation import constants
from mavecore.validation.exceptions import ValidationError

# from ..factories import generate_hgvs, VariantFactory
from mavecore.validation.variant_validators import (
    validate_variant_json,
    validate_hgvs_string,
)


def generate_hgvs(prefix: str = "c") -> str:
    """Generates a random hgvs string from a small sample."""
    if prefix == "p":
        # Subset of 3-letter codes, chosen at random.
        amino_acids = [
            "Ala",
            "Leu",
            "Gly",
            "Val",
            "Tyr",
            "Met",
            "Cys",
            "His",
            "Glu",
            "Phe",
        ]
        ref = choice(amino_acids)
        alt = choice(amino_acids)
        return f"{prefix}.{ref}{choice(range(1, 100))}{alt}"
    else:
        alt = choice("ATCG")
        ref = choice("ATCG")
        return f"{prefix}.{choice(range(1, 100))}{ref}>{alt}"


class TestHGVSValidator(TestCase):
    """
    Tests the function :func:`validate_hgvs_string` to see if it is able
    to validate strings which do not comply with the HGVS standard for
    coding, non-coding and nucleotide variants and multi-variants.
    """

    def test_validation_error_not_str_or_bytes(self):
        with self.assertRaises(ValidationError):
            validate_hgvs_string([])

    def test_does_not_pass_enrich_wt_hgvs(self):
        with self.assertRaises(ValidationError):
            validate_hgvs_string("_wt")

    def test_does_not_pass_enrich_sy_hgvs(self):
        with self.assertRaises(ValidationError):
            validate_hgvs_string("_sy")

    def test_passes_multi(self):
        validate_hgvs_string("p.[Lys4Gly;Lys5Phe]", column="p")
        validate_hgvs_string("c.[1A>G;127_128delinsAGC]", column="nt")
        validate_hgvs_string("c.[1A>G;127_128delinsAGC]", column="splice")

    def test_error_invalid_hgvs(self):
        with self.assertRaises(ValidationError):
            validate_hgvs_string("c.ad", column="nt")

    def test_error_invalid_nt_prefix(self):
        with self.assertRaises(ValidationError):
            validate_hgvs_string("r.1a>g", column="nt")

        with self.assertRaises(ValidationError):
            validate_hgvs_string("c.1A>G", column="nt", splice_present=True)

    def test_error_invalid_splice_prefix(self):
        with self.assertRaises(ValidationError):
            validate_hgvs_string("r.1a>g", column="splice")

    def test_error_invalid_pro_prefix(self):
        with self.assertRaises(ValidationError):
            validate_hgvs_string("r.1a>g", column="p")

    def test_converts_bytes_to_string_before_validation(self):
        validate_hgvs_string(b"c.427A>G", column="splice")

    def test_return_none_for_null(self):
        for c in constants.null_values_list:
            self.assertIsNone(validate_hgvs_string(c, column="nt"))


class TestVariantJsonValidator(TestCase):
    """
    Tests the validator :func:`validate_variant_json` to check if the correct
    errors are thrown if an incorrectly formatted `dictionary` is set
    as a the `data` `JSONField` attribute of a :class:`..models.Variant`
    instance.
    """

    def test_validation_error_missing_score_data_key(self):
        data = {constants.variant_count_data: {}}
        with self.assertRaises(ValidationError):
            validate_variant_json(data)

    def test_validation_error_missing_count_data_key(self):
        data = {constants.variant_score_data: {}}
        with self.assertRaises(ValidationError):
            validate_variant_json(data)

    def test_validation_error_contains_unexpected_keys(self):
        data = {
            "extra": {},
            constants.variant_score_data: {},
            constants.variant_count_data: {},
        }
        with self.assertRaises(ValidationError):
            validate_variant_json(data)

    def test_validation_error_values_not_dict(self):
        data = {
            constants.variant_score_data: {},
            constants.variant_count_data: {},
        }
        for key in data.keys():
            data[key] = []
            with self.assertRaises(ValidationError):
                validate_variant_json(data)
            data[key] = {}
