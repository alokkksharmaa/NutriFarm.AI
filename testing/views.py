from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .assessment import assess_sample
from .forms import FarmerLoginForm, FarmerRegistrationForm, FeedSampleForm
from .models import FeedSample, TestResult


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


@login_required
def sample_detail(request: HttpRequest, sample_id: int) -> HttpResponse:
    """Show a sample only to its owner."""

    sample = get_object_or_404(
        FeedSample.objects.select_related('test_result'),
        pk=sample_id,
        farmer=request.user,
    )
    return render(request, 'testing/sample_detail.html', {'sample': sample})


@login_required
@require_POST
def evaluate_sample(request: HttpRequest, sample_id: int) -> HttpResponse:
    """Evaluate one owned sample and create or update its single result."""

    sample = get_object_or_404(FeedSample, pk=sample_id, farmer=request.user)
    assessment = assess_sample(sample)
    TestResult.objects.update_or_create(
        sample=sample,
        defaults={**assessment, 'tested_at': timezone.now()},
    )
    messages.success(request, 'The sample assessment has been saved.')
    return redirect('testing:sample_result', sample_id=sample.pk)


@login_required
def sample_result(request: HttpRequest, sample_id: int) -> HttpResponse:
    """Display an assessment only for a sample owned by the current farmer."""

    sample = get_object_or_404(
        FeedSample.objects.select_related('test_result'),
        pk=sample_id,
        farmer=request.user,
    )
    try:
        result = sample.test_result
    except TestResult.DoesNotExist:
        result = None
    return render(
        request,
        'testing/sample_result.html',
        {'sample': sample, 'result': result},
    )


@login_required
def sample_create(request: HttpRequest) -> HttpResponse:
    """Validate and save a sample owned by the logged-in farmer."""

    form = FeedSampleForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        sample = form.save(commit=False)
        sample.farmer = request.user
        sample.save()
        messages.success(request, 'Your sample was saved successfully.')
        return redirect('testing:sample_detail', sample_id=sample.pk)

    return render(request, 'testing/sample_form.html', {'form': form})


@login_required
def sample_history(request: HttpRequest) -> HttpResponse:
    """List only the samples submitted by the logged-in farmer."""

    samples = FeedSample.objects.filter(farmer=request.user).select_related('test_result')
    return render(request, 'testing/sample_history.html', {'samples': samples})


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Render the project's friendly 404 page when DEBUG is disabled."""

    return render(request, '404.html', status=404)


def register(request: HttpRequest) -> HttpResponse:
    """Validate and create a farmer account using Django's User model."""

    if request.user.is_authenticated:
        return redirect('testing:dashboard')

    form = FarmerRegistrationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your farmer account has been created.')
        return redirect('testing:dashboard')

    return render(request, 'testing/register.html', {'form': form})


def farmer_login(request: HttpRequest) -> HttpResponse:
    """Authenticate a farmer and establish a Django session."""

    if request.user.is_authenticated:
        return redirect('testing:dashboard')

    form = FarmerLoginForm(
        request,
        data=request.POST if request.method == 'POST' else None,
    )
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('testing:dashboard')

    return render(request, 'testing/login.html', {'form': form})


@require_POST
def farmer_logout(request: HttpRequest) -> HttpResponse:
    """End the current authentication session."""

    logout(request)
    return redirect('core:home')


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Show counts and recent samples belonging to the signed-in farmer."""

    samples = FeedSample.objects.filter(farmer=request.user).select_related('test_result')
    context = {
        'farmer_name': request.user.get_full_name() or request.user.username,
        'total_samples': samples.count(),
        'total_tested': TestResult.objects.filter(sample__farmer=request.user).count(),
        'recent_samples': samples[:5],
    }
    return render(request, 'testing/dashboard.html', context)
