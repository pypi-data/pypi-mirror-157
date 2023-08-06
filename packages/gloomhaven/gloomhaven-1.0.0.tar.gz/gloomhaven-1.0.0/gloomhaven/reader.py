import yaml

from .deck import GloomhavenDeck


def read_deck(file_path: str) -> GloomhavenDeck:
    """Read standardized yaml into a deck"""
    with open(file_path) as f:
        deck_dict = yaml.safe_load(f)
    return GloomhavenDeck(**deck_dict)
