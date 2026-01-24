from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


from selenium import webdriver
from selenium.webdriver.common.by import By

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialApp

User = get_user_model()


class BaseStaticLiveServerTestCase(StaticLiveServerTestCase):
    """
    Selenium を用いた E2E テストで使用するクラス。

    Attributes:
        driver (selenium.webdriver): テスト用のブラウザドライバ。
    """

    host = "web"  # ✅️ Djangoアプリのコンテナ名

    # fixturesの設定は任意
    fixtures = ["accounts/fixtures/socialapp.json"]  # 外部認証サービスを使用した例

    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # super() は最初に記述
        cls.driver = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=webdriver.ChromeOptions(),
        )
        cls.driver.implicitly_wait(10)  # 読み込みの待機時間

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()  # super() は最後に記述

    # signupするアカウント情報を定義
    username = "testuser001"
    email = "test@example.com"
    password = "TESTdjango123"

    def create_testuser(self):

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

    def login(self):

        # loginページにアクセス
        self.driver.get(f"{self.live_server_url}/accounts/login/")

        # データを入力
        self.driver.find_element(By.NAME, "login").send_keys(self.email)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)

        # 送信ボタンをクリック
        self.driver.find_element(By.TAG_NAME, "button").click()

        # ログインが成功しているか確認する
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/")


class TestSignupSuccess(BaseStaticLiveServerTestCase):

    def test_signup_success(self):

        # signupページにアクセス
        self.driver.get(f"{self.live_server_url}/accounts/signup/")

        # データを入力
        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "email").send_keys(self.email)
        self.driver.find_element(By.NAME, "password1").send_keys(self.password)
        self.driver.find_element(By.NAME, "password2").send_keys(self.password)

        # 送信ボタンまで下にスクロール
        self.driver.execute_script("window.scrollBy(0, 300);")

        # 送信ボタンをクリック
        button = self.driver.find_element(By.TAG_NAME, "button")
        self.driver.execute_script("arguments[0].click();", button)

        # メール確認ページへ遷移することを確認する
        self.assertEqual(
            self.driver.current_url, f"{self.live_server_url}/accounts/confirm-email/"
        )


class TestSignupError(BaseStaticLiveServerTestCase):
    def test_signup_error(self):

        # signupページにアクセス
        self.driver.get(f"{self.live_server_url}/accounts/signup/")

        # バリデーションで通らないパスワードを入力
        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "email").send_keys(self.email)
        self.driver.find_element(By.NAME, "password1").send_keys("password")
        self.driver.find_element(By.NAME, "password2").send_keys("password")

        # 送信ボタンまで下にスクロール
        self.driver.execute_script("window.scrollBy(0, 300);")

        # 送信ボタンをクリック
        button = self.driver.find_element(By.TAG_NAME, "button")
        self.driver.execute_script("arguments[0].click();", button)

        # サインアップページへ戻ることを確認する
        self.assertEqual(
            self.driver.current_url, f"{self.live_server_url}/accounts/signup/"
        )


class TestLoginSuccess(BaseStaticLiveServerTestCase):
    def test_login_success(self):

        # ログイン用ユーザーの作成
        self.create_testuser()

        # loginページにアクセス
        self.driver.get(f"{self.live_server_url}/accounts/login/")

        # データを入力
        self.driver.find_element(By.NAME, "login").send_keys(self.email)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)

        # 送信ボタンをクリック
        self.driver.find_element(By.TAG_NAME, "button").click()

        # トップページへ遷移することを確認する
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/")


class TestLoginError(BaseStaticLiveServerTestCase):
    def test_login_error(self):

        # ログイン用ユーザーの作成
        self.create_testuser()

        # loginページにアクセス
        self.driver.get(f"{self.live_server_url}/accounts/login/")

        # データを入力
        self.driver.find_element(By.NAME, "login").send_keys(self.email)
        self.driver.find_element(By.NAME, "password").send_keys("password")

        # 送信ボタンをクリック
        self.driver.find_element(By.TAG_NAME, "button").click()

        # ログインページへ遷移することを確認する
        self.assertEqual(
            self.driver.current_url, f"{self.live_server_url}/accounts/login/"
        )


class TestTweetSuccess(BaseStaticLiveServerTestCase):
    def test_tweet_success(self):
        # - ログイン処理 -
        # ログイン用のtestuserを作成
        self.create_testuser()

        # ログインする
        self.login()

        # トップページへ遷移することを確認する
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/")

        # - ツイート処理 -
        # ツイートを入力
        tweet_content = "testツイート"
        self.driver.find_element(By.NAME, "content").send_keys(tweet_content)

        # 送信ボタンをクリック
        self.driver.find_element(By.CSS_SELECTOR, ".form-content-post button").click()

        # ツイートできているか確認
        tweet = self.driver.find_elements(By.CLASS_NAME, "tweet-text")
        self.assertEqual(tweet[0].text, tweet_content)

    def test_tweet_validation(self):
        # - ログイン処理 -
        # ログイン用のtestuserを作成
        self.create_testuser()

        # ログインする
        self.login()

        # - ツイート処理 -
        # バリデーションで通らないツイートを入力
        self.driver.find_element(By.NAME, "content").send_keys("X" * 150)

        # 送信ボタンをクリック
        self.driver.find_element(By.CSS_SELECTOR, ".form-content-post button").click()

        # 141字以降は入力されず140字でツイートが入力されることを確認
        tweet = self.driver.find_element(By.CLASS_NAME, "tweet-text")
        self.assertEqual(len(tweet.text), 140)


class TestTweetError(BaseStaticLiveServerTestCase):
    def test_tweet_none(self):

        # - ログイン処理 -
        # ログイン用のtestuserを作成
        self.create_testuser()

        # ログインする
        self.login()

        # ツイートを入力せずに送信ボタンをクリック
        self.driver.find_element(By.CSS_SELECTOR, ".form-content-post button").click()

        # エラーのflash messageが出るか確認する
        error_message = "ポスト内容がありません"

        flash_message = self.driver.find_element(
            By.CSS_SELECTOR, ".list-unstyled.alert.alert-warning"
        )
        self.assertIn(error_message, flash_message.text)
