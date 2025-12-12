from django.db import IntegrityError, DataError
from django.test import TestCase

from accounts.models import CustomUser


class TestUserModel(TestCase):
    # emailのunique制約のテスト
    def test_email_unique(self):
        CustomUser.objects.create(
            username="alice1",
            email="alice@example.com",
            phone_number="09011112222",
            birth_of_date="2000-1-1",
            account_id="test001a",
        )

        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                username="alice2",
                email="alice@example.com",
                phone_number="09011112222",
                birth_of_date="2000-1-1",
                account_id="test001b",
            )

    # uniqueではないemailは登録できるか
    def test_email_not_unique(self):
        bob1 = CustomUser.objects.create(
            username="bob1",
            email="bob@example.com",
            phone_number="07011112222",
            birth_of_date="2000-1-1",
            account_id="test002a",
        )

        bob2 = CustomUser.objects.create(
            username="bob2",
            email="bob2@example.com",
            phone_number="07011112222",
            birth_of_date="2000-1-1",
            account_id="test002b",
        )

        self.assertNotEqual(bob1.email, bob2.email)

    # phone_numberのmax_length制約のテスト
    def test_phone_number_max_length(self):
        with self.assertRaises(DataError):
            CustomUser.objects.create(
                username="charlie1",
                email="charlie1@example.com",
                phone_number="1" * 16,
                birth_of_date="2000-1-1",
                account_id="test003",
            )

    # phone_numberの文字数が既定文字数のときデータ登録できるか
    def test_phone_number_not_max_length(self):
        charlie = CustomUser.objects.create(
            username="charlie2",
            email="charlie2@example.com",
            phone_number="1" * 15,
            birth_of_date="2000-1-1",
            account_id="test004",
        )

        self.assertEqual(15, len(charlie.phone_number))

    # account_idのunique制約のテスト
    def test_account_id_unique(self):
        CustomUser.objects.create(
            username="david1",
            email="david@example.com",
            phone_number="09011112222",
            birth_of_date="2000-1-1",
            account_id="test005a",
        )

        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                username="david2",
                email="david@example.com",
                phone_number="09011112222",
                birth_of_date="2000-1-1",
                account_id="test005b",
            )

    # account_idがuniqueではない時データ登録できるか
    def test_account_id_not_unique(self):
        eve1 = CustomUser.objects.create(
            username="eve1",
            email="eve1@example.com",
            phone_number="09011112222",
            birth_of_date="2000-1-1",
            account_id="test006a",
        )

        eve2 = CustomUser.objects.create(
            username="eve2",
            email="eve2@example.com",
            phone_number="09011112222",
            birth_of_date="2000-1-1",
            account_id="test006b",
        )

        self.assertNotEqual(eve1.account_id, eve2.account_id)
