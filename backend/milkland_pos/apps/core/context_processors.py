from apps.core.models import BusinessSettings


def business_settings(request):
    settings = BusinessSettings.get_settings()
    return {'business': settings}
