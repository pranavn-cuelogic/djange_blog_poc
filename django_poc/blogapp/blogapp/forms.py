from django import forms
from captcha.fields import CaptchaField
from myblog.models import User
from django.utils.translation import ugettext_lazy as _

attrs_dict = {
    'class': 'form-control',
    'style': 'width:100%',
    'required': 'required',
}


class UserForm(forms.Form):
    """
    Form for accessing the user table fields.

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
                placeholder=_('First Name'),
            )
        ),
        error_messages={'required': 'Please enter Firstname'}
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs=dict(
                attrs_dict,
                placeholder=_('Last Name'),
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
                placeholder=_('Email-id'),
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
                placeholder=_('Password'),
            )
        ),
        label='Password',
        error_messages={'required': 'Please enter Password'}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                attrs_dict,
                placeholder=_('Confirm Password',)
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


class UserProfileForm(forms.Form):
    """
    Form for accessing the userprofile table fields.

    Validates the user details before saving it to DB.
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

    phone_number = forms.CharField(
        max_length=10,
        label='Phone Number',
        strip=True,
        widget=forms.TextInput(
            attrs=dict(
                attrs_dict,
                placeholder='Phone Number',
            )
        ),
        error_messages={'required': 'Please enter Phone Number.'}
    )
    address = forms.CharField(
        widget=forms.Textarea(
            attrs=dict(
                style='display:block; width:100%'
            )
        ),
        label='Address',
        strip=True,
        error_messages={'required': 'Please enter Address'}
    )
    about_me = forms.CharField(
        widget=forms.Textarea(
            attrs=dict(
                style='display:block; width:100%'
            )
        ),
        label='About Me',
        strip=True,
        error_messages={'required': 'Please write something about urself'}
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserProfileForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.user.id).count():
            raise forms.ValidationError(u'Email address already exist!.')
        return email


class UploadUserPicForm(forms.Form):
    """
    Form for accessing the userprofile table fields.

    Validates the user details before saving it to DB.
    """
    photo = forms.FileField(
        widget=forms.FileField,
        label='Upload Field',
    )


class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                attrs_dict,
                placeholder='Password',
            )
        ),
        label='Password',
        error_messages={'required': 'Please enter your new Password'}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                attrs_dict,
                placeholder='Confirm Password',
            )
        ),
        label='Confirm Password',
        error_messages={'required': 'Please enter again'}
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_confirm_password(self):
        """
        Validates the password & confirm password.

        """
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data


class PostForm(forms.Form):

    CHOICES = [('publish', 'Publish'), ('draft', 'Draft')]

    title = forms.CharField(
        label='Title',
        widget=forms.TextInput(
            attrs=dict(
                attrs_dict,
                placeholder='Title'
            )
        ),
        error_messages={'required': 'Please enter title'}
    )

    body = forms.CharField(
        label='Body',
        widget=forms.Textarea(
            attrs=dict(
                attrs_dict
            )
        ),
        error_messages={'required': 'Please enter body'}
    )

    tags = forms.CharField(
        label='Tags',
        widget=forms.DateInput(
            attrs=dict(
                attrs_dict,
                placeholder='Tags'
            )
        ),
        error_messages={'required': 'Please enter tags'}
    )

    status = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect(
            attrs=dict(
                {'required': 'required', 'class': 'radiobutton'}
            )
        ),
        error_messages={'required': 'Please select status'}
    )
