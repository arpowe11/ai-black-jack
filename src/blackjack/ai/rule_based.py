"""Rule-based strategy (notebook's get_ai_action_v2), using simplified basic-strategy rules."""

from blackjack.ai.base import Action, GameState


class RuleBasedStrategy:
    def decide(self, state: GameState) -> Action:
        score, dealer = state.score, state.dealer_value

        # Soft hand (usable ace): can't bust on one more card, so be aggressive.
        if state.usable_ace:
            if score <= 17:
                return Action.HIT
            if score == 18:
                return Action.HIT if dealer >= 9 else Action.STAND
            return Action.STAND

        # Hard hand.
        if score >= 17:
            return Action.STAND
        if score <= 11:
            return Action.HIT
        if score == 12:
            return Action.STAND if 4 <= dealer <= 6 else Action.HIT
        # 13-16: stand only when the dealer shows a weak card (2-6).
        return Action.STAND if 2 <= dealer <= 6 else Action.HIT
