from hestia_earth.utils.tools import flatten
from hestia_earth.utils.model import find_term_match

from hestia_earth.validation.utils import _filter_list_errors


def validate_linked_terms(cycle: dict, list_key: str, linked_key: str, linked_list_key: str, allow_empty=False):
    linked_nodes = cycle.get(linked_list_key, [])

    def validate(values: tuple):
        index, emission = values
        linked_items = emission.get(linked_key)
        return linked_items is None or any([
            find_term_match(linked_nodes, item.get('@id')) for item in (
                [linked_items] if isinstance(linked_items, dict) else linked_items
            )
        ]) or (
            {
                'level': 'warning',
                'dataPath': f".{list_key}[{index}]",
                'message': f"should add the linked {linked_list_key} to the cycle",
                'params': {
                    'term': emission.get('term', {}),
                    'expected': linked_items
                }
            } if allow_empty and len(linked_nodes) == 0 else {
                'level': 'error',
                'dataPath': f".{list_key}[{index}]",
                'message': f"must add the linked {linked_list_key} to the cycle",
                'params': {
                    'term': emission.get('term', {}),
                    'expected': linked_items
                }
            }
        )

    return _filter_list_errors(flatten(map(validate, enumerate(cycle.get(list_key, [])))))
