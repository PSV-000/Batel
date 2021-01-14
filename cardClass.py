class Card:
    def __init__(self, game, cardName, setName, edition, condition, language):
        self.game = game # e.g. MTG/YGO/PKMN
        self.cardName = cardName
        self.setName = setName
        self.edition = edition
        self.condition = condition
        self.language = language
        self.prices = []
