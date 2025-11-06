"""
TOON (Token-Oriented Object Notation) encoder for Contextinator.

Converts JSON structures to compact TOON format, saving 40-60% tokens.
"""

from typing import Any, Dict, List, Union


def encode_value(value: Any, key: str = "") -> str:
    """
    Encode a single value to TOON format.
    
    Args:
        value: Value to encode
        key: Optional key name for context
        
    Returns:
        TOON-encoded string
    """
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Only quote if contains special chars
        if any(c in value for c in [',', ':', '[', ']', '{', '}', ' ']):
            return f'"{value}"'
        return value
    elif isinstance(value, list):
        return encode_list(value, key)
    elif isinstance(value, dict):
        return encode_dict(value, key)
    return str(value)


def encode_list(items: List[Any], key: str = "") -> str:
    """
    Encode list to TOON format: key[n]: item1,item2,item3
    
    Args:
        items: List to encode
        key: Key name for the list
        
    Returns:
        TOON-encoded list string
    """
    if not items:
        return f"{key}[0]:" if key else "[]"
    
    # Simple values - compact format
    if all(isinstance(item, (str, int, float, bool)) for item in items):
        encoded_items = [encode_value(item) for item in items]
        if key:
            return f"{key}[{len(items)}]: {','.join(encoded_items)}"
        return ','.join(encoded_items)
    
    # Complex values - line by line
    result = []
    for i, item in enumerate(items):
        if isinstance(item, dict):
            result.append(f"{key}[{i}]: {encode_dict(item)}")
        else:
            result.append(f"{key}[{i}]: {encode_value(item)}")
    return '\n'.join(result)


def encode_dict(obj: Dict[str, Any], prefix: str = "") -> str:
    """
    Encode dictionary to TOON format with dot notation.
    
    Args:
        obj: Dictionary to encode
        prefix: Prefix for nested keys
        
    Returns:
        TOON-encoded dictionary string
    """
    if not obj:
        return "{}"
    
    lines = []
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # Nested object - flatten with dot notation
            lines.append(encode_dict(value, full_key))
        elif isinstance(value, list):
            # List - use compact array notation
            lines.append(encode_list(value, full_key))
        else:
            # Simple value
            lines.append(f"{full_key}: {encode_value(value)}")
    
    return '\n'.join(lines)


def toon_encode(data: Union[Dict, List], root_key: str = "data") -> str:
    """
    Main TOON encoding function.
    
    Args:
        data: Data structure to encode (dict or list)
        root_key: Root key name for the structure
        
    Returns:
        TOON-encoded string
        
    Example:
        >>> data = {"tags": ["jazz", "chill", "lofi"], "count": 3}
        >>> print(toon_encode(data))
        tags[3]: jazz,chill,lofi
        count: 3
    """
    if isinstance(data, dict):
        return encode_dict(data)
    elif isinstance(data, list):
        return encode_list(data, root_key)
    else:
        return encode_value(data)


__all__ = ['toon_encode']
