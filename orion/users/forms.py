from django import forms

from users.models import User


class DateInput(forms.DateInput):
    input_type = 'date'


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'birth_year', 'bio', 'avatar']
        widgets = {
            'birth_year': DateInput,
        }


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
