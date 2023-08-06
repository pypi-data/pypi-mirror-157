import idutils

from mavecore.validation.exceptions import ValidationError
from mavecore.validation.utilities import is_null


def validate_sra_identifier(identifier):
    """
    Validates whether the identifier is a valid SRA identifier.

    Parameters
    __________
    identifier: str
        The identifier to be validated.

    Raises
    ______
    ValidationError
        If the identifier is not a valid SRA identifier.
    """
    if not (
        idutils.is_sra(identifier)
        or idutils.is_bioproject(identifier)
        or idutils.is_geo(identifier)
        or idutils.is_arrayexpress_array(identifier)
        or idutils.is_arrayexpress_experiment(identifier)
    ):
        raise ValidationError(
            f"'{identifier} is not a valid SRA, GEO, ArrayExpress or BioProject "
            "accession."
        )


def validate_keyword(kw):
    """
    This function validates whether or not the kw parameter is valid by
    checking that it is a string that is not null. If kw is null
    or is not a string, an error is raised.

    Parameters
    __________
    kw : str
        The keyword to be validated.

    Raises
    ______
    ValidationError
        If the kw argument is not a valid string.
    """
    if is_null(kw) or not isinstance(kw, str):
        raise ValidationError(
            f"'{kw}' not a valid keyword. Keywords must be valid strings."
        )


def validate_pubmed_identifier(identifier):
    """
    Validates whether the identifier is a valid PubMed identifier.

    Parameters
    __________
    identifier: str
        The identifier to be validated.

    Raises
    ______
    ValidationError
        If the identifier is not a valid PubMed identifier.
    """
    if not idutils.is_pmid(identifier):
        raise ValidationError(f"'{identifier} is not a valid PubMed identifier.")


def validate_doi_identifier(identifier):
    """
    Validates whether the identifier is a valid DOI identifier.

    Parameters
    __________
    identifier: str
        The identifier to be validated.

    Raises
    ______
    ValidationError
        If the identifier is not a valid DOI identifier.
    """
    if not idutils.is_doi(identifier):
        raise ValidationError(f"'{identifier}' is not a valid DOI.")


def validate_ensembl_identifier(identifier):
    """
    Validates whether the identifier is a valid Ensembl identifier.

    Parameters
    __________
    identifier: str
        The identifier to be validated.

    Raises
    ______
    ValidationError
        If the identifier is not a valid Ensembl identifier.
    """
    if not idutils.is_ensembl(identifier):
        raise ValidationError(f"'{identifier}' is not a valid Ensembl accession.")


def validate_uniprot_identifier(identifier):
    """
    Validates whether the identifier is a valid UniProt identifier.

    Parameters
    __________
    identifier: str
        The identifier to be validated.

    Raises
    ______
    ValidationError
        If the identifier is not a valid UniProt identifier.
    """
    if not idutils.is_uniprot(identifier):
        raise ValidationError(f"'{identifier}' is not a valid UniProt accession.")


def validate_refseq_identifier(identifier):
    """
    Validates whether the identifier is a valid RefSeq identifier.

    Parameters
    __________
    identifier: str
        The identifier to be validated.

    Raises
    ______
    ValidationError
        If the identifier is not a valid RefSeq identifier.
    """
    if not idutils.is_refseq(identifier):
        raise ValidationError(f"'{identifier}' is not a valid RefSeq accession.")


def validate_genome_identifier(identifier):
    """
    Validates whether the identifier is a valid genome identifier.

    Parameters
    __________
    identifier: str
        The identifier to be validated.

    Raises
    ______
    ValidationError
        If the identifier is not a valid genome identifier.
    """
    if not idutils.is_genome(identifier):
        raise ValidationError(
            f"'{identifier}' is not a valid GenBank or RefSeq genome assembly."
        )


def validate_keyword_list(values):
    """
    This function takes a list of keyword values and validates that each one is valid.
    A valid keyword is a non-null string. The validate_keyword function will raise an
    ValidationError if any of the keywords are invalid.

    Parameters
    __________
    values : list[str]
        The list of values to be validated.
    """
    for value in values:
        if not is_null(value):
            validate_keyword(value)


def validate_pubmed_list(values):
    """
    Validates whether each identifier in a list of identifiers (values) is a valid PubMed identifier.

    Parameters
    __________
    identifier: List[str]
        The list of identifiers to be validated.

    Raises
    ______
    ValidationError
        If at least one of the identifiers is not a valid PubMed identifier.
    """
    for value in values:
        if not is_null(value):
            validate_pubmed_identifier(value)


def validate_sra_list(values):
    """
    Validates whether each identifier in a list of identifiers (values) is a valid SRA identifier.

    Parameters
    __________
    identifier: List[str]
        The list of identifiers to be validated.

    Raises
    ______
    ValidationError
        If at least one of the identifiers is not a valid SRA identifier.
    """
    for value in values:
        if not is_null(value):
            validate_sra_identifier(value)


def validate_doi_list(values):
    """
    Validates whether each identifier in a list of identifiers (values) is a valid DOI identifier.

    Parameters
    __________
    identifier: List[str]
        The list of identifiers to be validated.

    Raises
    ______
    ValidationError
        If at least one of the identifiers is not a valid DOI identifier.
    """
    for value in values:
        if not is_null(value):
            validate_doi_identifier(value)


def validate_ensembl_list(values):
    """
    Validates whether each identifier in a list of identifiers (values) is a valid Ensembl identifier.

    Parameters
    __________
    identifier: List[str]
        The list of identifiers to be validated.

    Raises
    ______
    ValidationError
        If at least one of the identifiers is not a valid Ensemble identifier.
    """
    for value in values:
        if not is_null(value):
            validate_ensembl_identifier(value)


def validate_refseq_list(values):
    """
    Validates whether each identifier in a list of identifiers (values) is a valid RefSeq identifier.

    Parameters
    __________
    identifier: List[str]
        The list of identifiers to be validated.

    Raises
    ______
    ValidationError
        If at least one of the identifiers is not a valid RefSeq identifier.
    """
    for value in values:
        if not is_null(value):
            validate_refseq_identifier(value)


def validate_uniprot_list(values):
    """
    Validates whether each identifer in a list of identifiers (values) is a valid UniProt identifier.

    Parameters
    __________
    identifier: List[str]
        The list of identifiers to be validated.

    Raises
    ______
    ValidationError
        If at least one of the identifiers is not a valid UniProt identifier.
    """
    for value in values:
        if not is_null(value):
            validate_uniprot_identifier(value)
