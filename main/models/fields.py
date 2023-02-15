from django.db.models import DecimalField


class MoneyField(DecimalField):
    def __init__(self, verbose_name=None, name=None, decimal_places=2, **kwargs):
        self.min_value = 0
        kwargs['decimal_places'] = decimal_places
        super().__init__(verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': 0}
        defaults.update(kwargs)
        return super().formfield(**defaults)
