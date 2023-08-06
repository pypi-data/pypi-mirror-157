import random
from typing import Any, Generator, List, Set, Tuple, Union

from gloomhaven.mod_applier import ModDeckApplier

from .constants import DEFAULT_DECK, RESET_LIST


class GloomhavenDeck:

    RESET_SET = set(RESET_LIST)

    def __init__(
        self,
        cards: List[str] = None,
        name: str = None,
        shuffle: bool = True,
        mod_applier: ModDeckApplier = None,
    ):
        # map in values
        self.card_list = cards if cards else DEFAULT_DECK
        self.name = name if name else "<default name>"
        if mod_applier is None:
            self.mod_applier = ModDeckApplier(self.mod_fn_factory)
            self._build_modifier_fns()
        else:
            self.mod_applier = mod_applier

        # create copy
        self.current_deck = [*self.card_list]
        if shuffle:
            self._shuffle_deck()

        # error checking
        if all([self._is_continue_card(card) for card in self.card_list]):
            raise ValueError("Invalid deck: contains all continue cards.")

    @staticmethod
    def mod_fn_factory(mod: str):
        def apply_mod(x):
            return x + int(mod) if (x + int(mod)) >= 0 else 0

        return apply_mod

    @staticmethod
    def _is_continue_card(card: str):
        return card[0] == "c"

    @staticmethod
    def _parse_attack_continue_card(card: str):
        return card[1:]

    @staticmethod
    def _parse_effects(card: str):
        return card.split(";")[1:]

    @staticmethod
    def _parse_non_effects(card: str):
        return card.split(";")[0]

    def _build_modifier_fns(self):
        # build default ones
        self.mod_applier["Miss"] = lambda x: 0
        self.mod_applier["2x"] = lambda x: 2 * x

        # generate mod fns
        for card in set(self.card_list):
            if card not in ["Miss", "2x"] and not self._is_continue_card(card):
                base_card = self._parse_non_effects(card)
                self.mod_applier[base_card] = self.mod_fn_factory(base_card)

    def _shuffle_deck(self):
        random.shuffle(self.current_deck)

    def _reset_deck(self):
        self.current_deck = [*self.card_list]

    def _draw_card(self) -> str:
        return self.current_deck.pop()

    def remove_card(self, card: str) -> bool:
        """Remove a card from the card list"""
        for idx, c in enumerate(self.card_list):
            if c == card:
                _ = self.card_list.pop(idx)
                self._reset_deck()
                return True
        return False

    def add_card(self, card: str) -> bool:
        """Add a card to the card list"""
        self.card_list.append(card)
        self._build_modifier_fns()
        self._reset_deck()
        return True

    def draw(self) -> str:
        """Draw card based on playing rules"""
        # if deck is empty reset and shuffle
        if not self.current_deck:
            self._reset_deck()
            self._shuffle_deck()

        # draw card
        return self._draw_card()

    def get_attacks(self, base_attacks: List[int]) -> List[Tuple[int, Set[str]]]:
        """Get a final attack values from a list of base attacks

        Args:
            - base_attacks: int value for base attack value
        """

        rets = []
        _reset = False

        for attack_dmg in base_attacks:

            card = self.draw()
            total_effects = set()

            # card draw loop
            while True:

                # decide if deck needs to be reset
                if card in self.RESET_SET:
                    _reset = True

                # parse card
                base_card, effects = self._parse_non_effects(card), self._parse_effects(
                    card
                )
                _ = [total_effects.add(e) for e in effects]

                if self._is_continue_card(card):
                    base_card = self._parse_attack_continue_card(base_card)
                    attack_dmg = self.mod_applier[base_card](attack_dmg)
                    card = self.draw()
                else:
                    attack_dmg = self.mod_applier[base_card](attack_dmg)
                    break  # don't draw anymore

            # add to return
            rets.append((attack_dmg, total_effects))

        if _reset:
            self._reset_deck()
            self._shuffle_deck()

        return rets

    def simulate(
        self,
        base_attacks: Union[List[List[int]], Generator[List[int], Any, Any]],
        fresh: bool = True,
    ) -> List[int]:
        if fresh:
            self._reset_deck()
            self._shuffle_deck()

        res = []
        for attacks in base_attacks:
            res.append(self.get_attacks(attacks))
        return res

    def copy(self):
        new_deck = GloomhavenDeck(
            cards=[*self.card_list],
            mod_applier=self.mod_applier,
            name=f"{self.name}_copy",
        )
        new_deck.current_deck = [*self.current_deck]
        return new_deck

    def __repr__(self):
        return "\n".join(
            [
                self.name,
                f"Cards: {', '.join(self.card_list)}",
                f"Current Deck: {', '.join(reversed(self.current_deck))}",
            ]
        )

    def __str__(self):
        return self.__repr__()
