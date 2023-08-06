"""All of tag-matcher's public/private functions"""


def match(query_str=None, tags=[]) -> bool:
    """
    Check if a tag query satisfies a list of tags.

    Parameters:
    - query_str: The tag query. For example,
    if you wanted to see if the list of tags has both "foo" and "bar",
    you would say "foo~bar". If you wanted to see if the list of tags has either
    "foo" or "bar", you would say "foo+bar". You can have an infinite combination of
    these two operators!
    - tags: The list of tags that you wish to query. This should be a list of strings.
    """
    _validate_args(query_str=query_str, tags=tags)
    if not query_str:
        return True
    elif "~" in query_str:
        return all(
            [
                match(query_str=tag_subquery_str, tags=tags)
                for tag_subquery_str in query_str.split("~")
            ]
        )
    elif "+" in query_str:
        return any(
            [
                match(query_str=tag_subquery_str, tags=tags)
                for tag_subquery_str in query_str.split("+")
            ]
        )
    elif any([query_str == tag for tag in tags]):
        return True
    return False


def _validate_args(query_str, tags):
    if type(tags) != list:
        raise AttributeError(
            f"tags arg must be of type `list` (received type was " f"`{type(tags)}`)"
        )
    if type(query_str) != str:
        raise AttributeError(
            f"query_str must be of type `str` (received type was "
            f"`{type(query_str)}`)"
        )
