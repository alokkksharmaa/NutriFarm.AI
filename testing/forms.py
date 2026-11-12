from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class FarmerRegistrationForm(UserCreationForm):
    """Create a Django user with a full name and email address."""

    full_name = forms.CharField(max_length=150, label='Full name')
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('full_name', 'username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
