from django import forms
from django.contrib import messages
from django.core.validators import RegexValidator

from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "電話番号"}),
        validators=[RegexValidator(r"\d{10,15}", "10~15桁の数字を入力してください")],
    )

    birth_of_date = forms.DateField(
        input_formats=["%Y%m%d"],
        required=False,
        widget=forms.DateInput(attrs={"placeholder": "YYYYMMDD"}),
    )

    def signup(self, request, user):
        user.phone_number = self.cleaned_data["phone_number"]
        user.birth_of_date = self.cleaned_data["birth_of_date"]
        user.save()
        messages.add_message(request, messages.SUCCESS, "サインアップに成功しました")

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super().save(request)

        # Add your own processing here.

        # You must return the original result.
        return user
