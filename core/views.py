from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """Render the public landing page."""

    template_name = 'core/home.html'
