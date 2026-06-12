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


class AdminProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        required=False,
        label='Tanggal Lahir',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    duty_start = forms.TimeField(
        required=False,
        label='Jam Masuk',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    duty_end = forms.TimeField(
        required=False,
        label='Jam Selesai',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )

    class Meta:
        from .models import AdminProfile
        model = AdminProfile
        fields = [
            'full_name', 'email', 'phone', 'birth_date', 'birth_place',
            'age', 'gender', 'department', 'position', 'supervisor',
            'duty_start', 'duty_end', 'memo_text',
        ]
        widgets = {
            'memo_text': forms.Textarea(attrs={'rows': 3}),
        }
