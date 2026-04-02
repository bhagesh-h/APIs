def to_camel_case(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase.
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
