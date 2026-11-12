from decimal import Decimal

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import FeedSample


class FeedSampleForm(forms.ModelForm):
    """Collect a farmer's sample data and validate numeric/date values."""

    sample_name = forms.CharField(max_length=100, label='Sample name or ID')
    collection_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    ph_value = forms.DecimalField(
        min_value=Decimal('0'),
        max_value=Decimal('14'),
        widget=forms.NumberInput(attrs={'min': '0', 'max': '14', 'step': '0.01'}),
    )
    moisture = forms.DecimalField(
        min_value=Decimal('0'),
        max_value=Decimal('100'),
        widget=forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.01'}),
    )
    temperature = forms.DecimalField(
        widget=forms.NumberInput(attrs={'step': '0.1'}),
        help_text='Enter degrees Celsius.',
    )
    smell = forms.ChoiceField(choices=(
        ('fresh', 'Fresh'),
        ('slightly_sour', 'Slightly sour'),
        ('strongly_sour', 'Strongly sour'),
        ('musty', 'Musty'),
        ('rotten', 'Rotten'),
        ('other', 'Other'),
    ))
    observations = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text='Optional notes about the sample.',
    )

    class Meta:
        model = FeedSample
        fields = (
            'sample_name',
            'feed_type',
            'collection_date',
            'ph_value',
            'moisture',
            'temperature',
            'smell',
            'mold_present',
            'observations',
        )
        widgets = {
            'feed_type': forms.Select(),
            'mold_present': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['collection_date'].initial = timezone.localdate()
        self.fields['temperature'].widget.attrs.update({
            'min': str(settings.SAMPLE_TEMPERATURE_MIN_C),
            'max': str(settings.SAMPLE_TEMPERATURE_MAX_C),
            'aria-describedby': 'id_temperature_helptext',
        })
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_collection_date(self):
        collection_date = self.cleaned_data['collection_date']
        if collection_date > timezone.localdate():
            raise forms.ValidationError('Collection date cannot be in the future.')
        return collection_date

    def clean_temperature(self):
        temperature = self.cleaned_data['temperature']
        minimum = Decimal(str(settings.SAMPLE_TEMPERATURE_MIN_C))
        maximum = Decimal(str(settings.SAMPLE_TEMPERATURE_MAX_C))
        if not minimum <= temperature <= maximum:
            raise forms.ValidationError(
                f'Temperature must be between {minimum}°C and {maximum}°C.'
            )
        return temperature


class FarmerRegistrationForm(UserCreationForm):
    """Create a Django user with a full name and email address."""

    full_name = forms.CharField(max_length=150, label='Full name')
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['full_name'].widget.attrs.update({'autocomplete': 'name'})
        self.fields['username'].widget.attrs.update({'autocomplete': 'username'})
        self.fields['email'].widget.attrs.update({'autocomplete': 'email'})
        self.fields['password1'].label = 'Password'
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].label = 'Confirm password'
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name'].strip()
        if not full_name:
            raise forms.ValidationError('Enter your full name.')
        return full_name

    def save(self, commit=True):
        user = super().save(commit=False)
        name_parts = self.cleaned_data['full_name'].split()
        user.first_name = name_parts[0]
        user.last_name = ' '.join(name_parts[1:])
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class FarmerLoginForm(AuthenticationForm):
    """Django's built-in username/password authentication form."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'username', 'autofocus': True}),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
