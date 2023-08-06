from django_actionable_messages.mixins import HERO_CARD, THUMBNAIL_CARD
from django_actionable_messages.msteams_cards.mixins import CardMixin


class HeroCard(CardMixin):
    card_type = HERO_CARD
    content_type = "application/vnd.microsoft.card.hero"


class ThumbnailCard(CardMixin):
    card_type = THUMBNAIL_CARD
    content_type = "application/vnd.microsoft.card.thumbnail"
