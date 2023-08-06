from django.core.serializers.json import DjangoJSONEncoder
from django.utils import translation
from django.utils.functional import Promise


class EncoderMixin:
    def __init__(self, *args, **kwargs):
        self.lang_code = kwargs.pop("lang_code", None)
        super().__init__(*args, **kwargs)


class BaseEncoder(EncoderMixin, DjangoJSONEncoder):
    """
    Everything that DjangoJSONEncoder can handle and translations with selected language
    """

    def default(self, o):
        if isinstance(o, Promise):
            with translation.override(self.lang_code):
                return translation.gettext(o)
        return super().default(o)
