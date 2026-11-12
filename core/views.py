from django.shortcuts import render


def home(request):
    """Render the public NutriFarm AI homepage."""

    return render(request, 'core/home.html')
