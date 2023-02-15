from datetime import timedelta

from django.utils.translation import ngettext


def daterange(start, days_type, goal=12):
    days = []
    count = 0
    while len(days) < goal:
        next_date = start + timedelta(days=count)
        if next_date.weekday() in days_type:
            days.append(next_date)
        count += 1
    return days


def get_description(serializer):
    description = ''
    for field, value in serializer.validated_data.items():
        old_value = getattr(serializer.instance, field)
        if old_value == value:
            continue

        if description:
            description += f'\n{field}: {old_value} -> {value}'
            continue
        description = f'Изменены поля:\n' \
                      f'{field}: {old_value} -> {value}'

    return description


def verbose_timedelta(delta):
    final_text = ''
    separator = ', '
    d = delta.days
    if d:
        final_text = ngettext('%(day)d day', '%(day)d days', d) % {'day': d} + separator
    h, s = divmod(delta.seconds, 3600)
    if h:
        final_text += ngettext('%(hour)d hour', '%(hour)d hours', h) % {'hour': h} + separator
    m, s = divmod(s, 60)
    if s:
        m += 1
    if m:
        final_text += ngettext('%(m)d minute', '%(m)d minutes', m) % {'m': m}
    return final_text
