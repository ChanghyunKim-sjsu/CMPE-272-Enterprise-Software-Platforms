"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Pagination Utilities
Description: Parses GitHub Link pagination headers.
"""


def parse_link_header(link_header: str | None) -> dict[str, str]:
    """Parse a GitHub Link header into relation-to-URL mappings."""

    if not link_header:
        return {}

    links = {}

    for part in link_header.split(","):
        sections = part.strip().split(";")

        if len(sections) < 2:
            continue

        url = sections[0].strip()

        if url.startswith("<") and url.endswith(">"):
            url = url[1:-1]

        for section in sections[1:]:
            section = section.strip()

            if section.startswith('rel="') and section.endswith('"'):
                relation = section[5:-1]
                links[relation] = url

    return links
