"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - Pagination
Description: Tests GitHub Link header parsing utilities.
"""

from app.pagination import parse_link_header


def test_parse_multiple_link_relations():
    """Parse next and last links from a GitHub Link header."""

    header = (
        '<https://api.github.com/repos/test/issues?page=2>; rel="next", '
        '<https://api.github.com/repos/test/issues?page=5>; rel="last"'
    )

    result = parse_link_header(header)

    assert result["next"].endswith("page=2")
    assert result["last"].endswith("page=5")


def test_parse_empty_link_header():
    """An absent Link header should return an empty dictionary."""

    result = parse_link_header(None)

    assert result == {}


def test_parse_previous_and_first_links():
    """Parse previous and first pagination relations."""

    header = (
        '<https://api.github.com/repos/test/issues?page=2>; rel="prev", '
        '<https://api.github.com/repos/test/issues?page=1>; rel="first"'
    )

    result = parse_link_header(header)

    assert result["prev"].endswith("page=2")
    assert result["first"].endswith("page=1")
