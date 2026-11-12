from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render


def about(request: HttpRequest) -> HttpResponse:
    """Show information about the NutriFarm AI project."""

    return render(request, 'testing/about.html')


def features(request: HttpRequest) -> HttpResponse:
    """Show the platform's planned features."""

    return render(request, 'testing/features.html')


def contact(request: HttpRequest) -> HttpResponse:
    """Render the contact page and demonstrate basic GET/POST handling."""

    if request.method == 'POST':
        return HttpResponse(
            'Contact form submission is not implemented yet.',
            status=501,
            content_type='text/plain; charset=utf-8',
        )

    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])

    return render(request, 'testing/contact.html')


def sample_detail(request: HttpRequest, sample_id: int) -> HttpResponse:
    """Display a positive sample ID supplied by the URL."""

    if sample_id < 1:
        raise Http404('Sample IDs must be positive integers.')

    return render(request, 'testing/sample_detail.html', {'sample_id': sample_id})


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Render the project's friendly 404 page when DEBUG is disabled."""

    return render(request, '404.html', status=404)
