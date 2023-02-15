from rest_framework.serializers import ChoiceField as DRFChoiceField
from rest_framework.serializers import DecimalField


class MoneyField(DecimalField):
    def __init__(self, coerce_to_string=None, max_value=None, min_value=20,
                 localize=False, rounding=None, **kwargs):
        super().__init__(22, 2, coerce_to_string,
                         max_value, min_value, localize, rounding, **kwargs)

    def to_representation(self, value):
        s = super().to_representation(value)
        return s.split('.')[0] if '.' in s else s


class ChoiceField(DRFChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)
