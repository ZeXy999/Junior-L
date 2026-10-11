from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def stars(value, max_stars=5):
    """Render a numeric rating as filled/empty stars."""
    try:
        rating = float(value)
    except (TypeError, ValueError):
        return ""
    full = max(0, min(int(max_stars), int(round(rating))))
    return mark_safe(
        f'<span class="stars" title="{rating:.1f} out of {max_stars}">'
        f'{"\u2605" * full}<span class="off">{"\u2605" * (int(max_stars) - full)}</span></span>'
    )


@register.simple_tag(takes_context=True)
def qs_replace(context, **kwargs):
    """Return the current query string with the given parameters replaced."""
    params = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            params.pop(key, None)
        else:
            params[key] = value
    return params.urlencode()
