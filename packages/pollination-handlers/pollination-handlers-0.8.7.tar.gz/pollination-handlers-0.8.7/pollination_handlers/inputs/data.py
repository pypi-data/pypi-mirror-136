"""Handlers to convert inputs that accept ladybug data collections."""
import json

from ladybug.datacollection import BaseCollection


def value_or_data_to_str(value):
    """Translate a single numerical value or data collection into a string.

    Args:
        value: Either a single numerical value, a data collection.

    Returns:
        str -- string version of the number or JSON array string of data
            collection values.
    """
    if isinstance(value, str):
        if value != 'None':
            try:  # first check to see if it's a valid number
                float(value)
            except ValueError:  # maybe it's a while JSON array of numbers
                loaded_data = json.loads(value)
                assert isinstance(loaded_data, list), \
                    'Data string must be either a number or an array.'
    elif isinstance(value, (float, int)):
        value = str(value)
    elif isinstance(value, BaseCollection):
        start_values = ['{0:.3f}'.format(v) for v in value.values]
        final_values = []
        for v in start_values:
            new_v = v.rstrip('0') 
            new_v = '{}0'.format(new_v) if new_v.endswith('.') else new_v
            final_values.append(new_v)
        value = str(final_values).replace('\'', '')
    else:
        raise ValueError(
            'Excpected a single number or a data collection. Not {}.'.format(type(value))
        )
    return value
