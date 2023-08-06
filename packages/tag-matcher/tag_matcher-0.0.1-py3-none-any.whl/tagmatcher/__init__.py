def match(query_str=None, tags=[]) -> bool:
    _validate_args(query_str=query_str, tags=tags)
    if not query_str:
        return True
    elif "~" in query_str:
        if all(
                [
                    match(query_str=tag_subquery_str, tags=tags)
                    for tag_subquery_str in query_str.split("~")
                ]
        ):
            return True
    elif "+" in query_str:
        if any(
                [
                    match(query_str=tag_subquery_str, tags=tags)
                    for tag_subquery_str in query_str.split("+")
                ]
        ):
            return True
    elif any([query_str == tag for tag in tags]):
        return True
    return False


def _validate_args(query_str, tags):
    if type(tags) != list:
        raise AttributeError(f"tags arg must be of type `list` (received type was "
                             f"`{type(tags)}`)")
    if type(query_str) != str:
        raise AttributeError(f"query_str must be of type `str` (received type was "
                             f"`{type(query_str)}`)")