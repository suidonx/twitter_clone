from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class ProfileEditForm(forms.ModelForm):
    class Meta:
        fields = [
            "username",
            "icon_image",
            "header_image",
            "self_introduction",
            "place",
            "website",
            "birth_of_date",
        ]
        help_texts = {
            "birth_of_date": "YYYY-MM-DD形式で入力してください。",
        }

        labels = {
            "username": "ユーザーネーム",
            "icon_image": "アイコン画像",
            "header_image": "ヘッダー画像",
            "self_introduction": "自己紹介",
            "place": "場所",
            "website": "ウェブサイト",
            "birth_of_date": "生年月日",
        }
        model = CustomUser
        widgets = {
            "username": forms.TextInput(
                attrs={"placeholder": "ユーザー名"},
            ),
            "icon_image": forms.FileInput(),
            "header_image": forms.FileInput(),
            "self_introduction": forms.Textarea(
                attrs={"placeholder": "自己紹介"},
            ),
            "place": forms.TextInput(
                attrs={"placeholder": "場所"},
            ),
            "website": forms.TextInput(
                attrs={"placeholder": "ウェブサイト"},
            ),
            "birth_of_date": forms.TextInput(
                attrs={
                    "placeholder": "YYYY-MM-DD",
                    "class": "is_invalid",
                },
            ),
        }
