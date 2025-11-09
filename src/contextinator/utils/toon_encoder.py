"""
TOON (Token-Oriented Object Notation) encoder for Contextinator.

Wrapper around the official toon-format library.
Converts JSON structures to compact TOON format, saving 40-60% tokens.
"""

from typing import Any, Dict, List, Union

try:
    from toon_format import encode as _toon_encode
    TOON_AVAILABLE = True
except ImportError:
    TOON_AVAILABLE = False


def toon_encode(data: Union[Dict, List, Any]) -> str:
    """
    Encode data to TOON format using the official toon-format library.
    
    Args:
        data: Data structure to encode (dict, list, or primitive)
        
    Returns:
        TOON-encoded string
        
    Example:
        >>> data = {"tags": ["jazz", "chill", "lofi"], "count": 3}
        >>> print(toon_encode(data))
        tags[3]: jazz,chill,lofi
        count: 3
        
    Raises:
        ImportError: If toon-format library is not installed
    """
    if not TOON_AVAILABLE:
        raise ImportError(
            "toon-format library not installed. "
            "Install with: pip install toon-format==0.9.0b1"
        )
    
    return _toon_encode(data)


__all__ = ['toon_encode']
