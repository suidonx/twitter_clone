from django.contrib.auth import get_user_model, login
from django.contrib.sites.models import Site
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse

from posts.models import Tweet

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialApp

User = get_user_model()

signup_url = reverse("account_signup")
login_url = reverse("account_login")
tweet_url = reverse("posts:tweet_create")


class TestView(TestCase):
    # signupページでユーザーを作成し、Eメール確認も済にする
    def setUp(self):
        # test用にsocial appを作成
        site = Site.objects.get_current()

        github_app = SocialApp.objects.create(
            provider="github",
            name="GitHub",
            client_id="dummy",
            secret="dummy",
        )

        github_app.sites.add(site)

        # signupするアカウントを定義
        self.username = "testuser001"
        self.email = "test@example.com"
        self.password = "TESTdjango123"

    # サインアップ正常系のテスト
    def test_signup_success(self):
        res = self.client.post(
            signup_url,
            {
                "username": self.username,
                "email": self.email,
                "password1": self.password,
                "password2": self.password,
            },
        )

        # signupが成功したらメール確認ページへ遷移する
        self.assertRedirects(res, "/accounts/confirm-email/")

        # ユーザーが作成されていることを確認する
        self.assertEqual(User.objects.count(), 1)

    # サインアップ異常系のテスト
    def test_signup_password_error(self):
        res = self.client.post(
            signup_url,
            {
                "username": self.username,
                "email": self.email,
                "password1": self.password,
                "password2": "abcdefg",
            },
        )

        # signupが失敗したらsignupページに戻るか確認する
        self.assertEqual(res.request["PATH_INFO"], signup_url)

        # ユーザーが増えていないことを確認
        self.assertEqual(User.objects.count(), 0)

    # ログイン正常系のテスト
    def test_login_success(self):
        # ログイン用のtestuserを作成
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

        # メールを確認済みにする
        EmailAddress.objects.create(
            user=user,
            email=self.email,
            verified=True,
            primary=True,
        )

        # ログイン処理
        res = self.client.post(
            login_url,
            {
                "login": self.email,
                "password": self.password,
            },
        )

        # ログインの成功を確認する
        self.assertEqual(res.status_code, 302)

        # リダイレクト先がトップページであることを確認する
        self.assertRedirects(res, "/")

    # ログイン異常系のテスト
    def test_login_error(self):
        # ログイン用のtestuserを作成
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

        # メールを確認済みにする
        EmailAddress.objects.create(
            user=user,
            email=self.email,
            verified=True,
            primary=True,
        )

        # ログイン処理
        res = self.client.post(
            login_url,
            {
                "login": self.email,
                "password": "abcdefg",
            },
        )

        # ログイン失敗後、ログインページに戻ることを確認する
        self.assertEqual(res.request["PATH_INFO"], login_url)

    # ツイート正常系のテスト
    def test_tweet_success(self):
        # ログイン用のtestuserを作成
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

        # メールを確認済みにする
        EmailAddress.objects.create(
            user=user,
            email=self.email,
            verified=True,
            primary=True,
        )

        # testuserでログイン
        self.client.force_login(user)

        # ツイート処理
        res = self.client.post(
            tweet_url,
            {
                "content": "テストツイート",
            },
        )

        # ツイートが作成されていることを確認する
        self.assertEqual(Tweet.objects.count(), 1)

        # ツイート投稿後、元のページへredirectが起きているか確認する
        self.assertEqual(res.status_code, 302)

    # ツイート異常系のテスト
    def test_tweet_error(self):
        # ログイン用のtestuserを作成
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

        # メールを確認済みにする
        EmailAddress.objects.create(
            user=user,
            email=self.email,
            verified=True,
            primary=True,
        )

        # testuserでログイン
        self.client.force_login(user)

        # 141文字のツイートが送信できないことを確認する
        res = self.client.post(
            tweet_url,
            {
                "content": "test" * 141,
            },
        )

        # ツイートが作られていないことを確認する
        self.assertEqual(Tweet.objects.count(), 0)

        # ツイート失敗後、元のページへredirectが起きているか確認する
        self.assertEqual(res.status_code, 302)
