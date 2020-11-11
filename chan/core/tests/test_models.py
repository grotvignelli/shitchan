import datetime

from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


SAMPLE_EMAIL = 'test@gmail.com'
SAMPLE_USERNAME = 'testuser'
SAMPLE_PASS = 'testpass'


class ModelTests(TestCase):
    """Test custom user model for user objects in db"""

    def test_create_user_successful(self):
        """
        Test create a new user with required fields:
        * Email
        * Username
        (with default avatar)
        """
        user = get_user_model().objects.create_user(
            email=SAMPLE_EMAIL,
            username=SAMPLE_USERNAME,
            password=SAMPLE_PASS
        )

        is_exists = get_user_model().objects.filter(
            email=SAMPLE_EMAIL,
            username=SAMPLE_USERNAME,
        ).exists()
        default_avatar_name = 'uploads/defaults/default.png'

        self.assertTrue(is_exists)
        self.assertEqual(user.email, SAMPLE_EMAIL)
        self.assertEqual(user.username, SAMPLE_USERNAME)
        self.assertEqual(user.avatar.name, default_avatar_name)
        self.assertTrue(user.check_password(SAMPLE_PASS))

    def test_create_user_with_dob(self):
        """Test create a new user with date of birth"""
        dob = datetime.date(1992, 12, 25)
        user = get_user_model().objects.create_user(
            email=SAMPLE_EMAIL,
            username=SAMPLE_USERNAME,
            date_of_birth=dob,
            password=SAMPLE_PASS
        )

        self.assertEqual(user.date_of_birth, dob)

    @patch('uuid.uuid4')
    def test_avatar_file_name(self, mock_uuid):
        """Test that image is saved in correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.avatar_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/avatar/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

    def test_create_user_invalid_email(self):
        """Test create a new user without email is raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                username=SAMPLE_USERNAME,
                password=SAMPLE_PASS
            )

    def test_create_user_invalid_username(self):
        """Test create a new user without username is raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=SAMPLE_EMAIL,
                username=None,
                password=SAMPLE_PASS
            )

    def test_create_user_email_normalize(self):
        """Test create user email get normalized"""
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user(
            email=email,
            username=SAMPLE_USERNAME,
            password=SAMPLE_PASS
        )

        self.assertEqual(user.email, email.lower())

    def test_create_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email=SAMPLE_EMAIL,
            username=SAMPLE_USERNAME,
            password=SAMPLE_PASS
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    # ** SHITCHAN MODEL TESTS **


class ShitchanModelTests(TestCase):
    """Tests for Shitchan model in the database"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username=SAMPLE_USERNAME,
            email=SAMPLE_EMAIL,
            password=SAMPLE_PASS
        )
        self.admin = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='testpass'
        )
        self.board = models.Board.objects.create(
            title='test board',
            code='tb',
            user=self.admin
        )

    def test_create_board(self):
        """Test creating a board in the database"""
        title = 'political'
        code = 'pl'
        board = models.Board.objects.create(
            title=title, code=code, user=self.admin
        )
        is_exists = models.Board.objects.filter(
            title=title, code=code, user=self.admin
        ).exists()

        self.assertEqual(str(board), title)
        self.assertTrue(is_exists)

    def test_create_thread(self):
        """Test creating a thread in the database"""
        title = 'test thread'
        content = 'Neque porro quisquam est qui dolorem ipsum quia \
                   dolor sit amet, consectetur, adipisci velit...'
        thread = models.Thread.objects.create(
            title=title,
            content=content,
            user=self.user,
            board=self.board
        )
        is_exists = models.Thread.objects.filter(
            user=self.user,
            title=title
        ).exists()

        self.assertTrue(is_exists)
        self.assertEqual(str(thread), title)
