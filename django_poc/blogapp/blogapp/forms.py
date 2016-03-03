from django import forms
from captcha.fields import CaptchaField
from myblog.models import User

attrs_dict = {
    'class': 'form-control',
    'style': 'width:100%',
    'required': 'required',
}


class SignupForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the password is entered twice and matches,
    and that the email/username is not already taken.
    """

    first_name = forms.CharField(
        max_length=30,
        label='First Name',
        strip=True,
        widget=forms.TextInput(
            attrs=dict(
                attrs_dict,
                placeholder='First Name',
            )
        ),
        error_messages={'required': 'Please enter Firstname'}
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs=dict(
                attrs_dict,
                placeholder='Last Name',
            )
        ),
        strip=True,
        error_messages={'required': 'Please enter Lastname'}
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs=dict(
                attrs_dict,
                maxlength=200,
                placeholder='Email-id',
            )
        ),
        label='Email',
        strip=True,
        error_messages={'required': 'Please enter Email-id'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                attrs_dict,
                placeholder='Password',
            )
        ),
        label='Password',
        error_messages={'required': 'Please enter Password'}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                attrs_dict,
                placeholder='Confirm Password',
            )
        ),
        label='Confirm Password',
        error_messages={'required': 'Please enter Confirm Password'}
    )
    captcha = CaptchaField()


    def clean_confirm_password(self):
        """
        Validates the password & confirm password.

        """
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data

    def clean_email(self):
        """
        Validates the email is not already exists or not.

        """
        email = self.cleaned_data.get('email')
        if email != "":
            try:
                user = User.objects.get(email__exact=email)
            except User.DoesNotExist:
                return ""
            else:
                raise forms.ValidationError(u'The email-id already exists!')
        return self.cleaned_data
