from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CitizenRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label='Full Name',
        widget=forms.TextInput(attrs={'placeholder': 'John Doe'}),
    )
    email = forms.EmailField(
        required=True,
        label='Email Address',
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = User
        # username acts as ID / NIK Number in the UI
        fields = ('first_name', 'username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
