import datetime
import tempfile
import os
import shutil

from unittest.mock import patch
from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIClient


SIGNUP_USER_URL = reverse('user:signup')


def create_payload(**params):
    defaults = {
        'email': 'test@gmail.com',
        'username': 'testuser',
        'password': 'testpass'
    }
    defaults.update(**params)

    return defaults


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test publicly user API"""

    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        directory = 'uploads/avatar'
        path = os.path.join(settings.MEDIA_ROOT, directory)

        shutil.rmtree(path, ignore_errors=True)

    def test_create_user_successful(self):
        """Test creating a new user in API is successful"""
        payload = create_payload()

        res = self.client.post(SIGNUP_USER_URL, payload)
        user = get_user_model().objects.get(
            email=payload['email'],
            username=payload['username']
        )
        default_avatar_name = 'uploads/defaults/default.png'

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.email, payload['email'])
        self.assertEqual(user.username, payload['username'])
        self.assertEqual(user.avatar.name, default_avatar_name)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_with_dob(self):
        """Test creating a new user in API with date of birth"""
        payload = create_payload(
            date_of_birth=datetime.date(1992, 12, 25),
        )

        res = self.client.post(SIGNUP_USER_URL, payload)
        user = get_user_model().objects.get(
            email=payload['email'],
            username=payload['username']
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.date_of_birth, payload['date_of_birth'])

    @patch('uuid.uuid4')
    def test_create_user_with_avatar(self, mock_uuid):
        """Test creating a new user in API with avatar"""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            uuid = 'test-uuid'
            mock_uuid.return_value = uuid

            image = Image.new('RGB', (100, 100))
            image.save(ntf, format='JPEG')
            ntf.seek(0)

            payload = create_payload(avatar=ntf)
            res = self.client.post(
                SIGNUP_USER_URL, payload, format='multipart'
            )
            user = get_user_model().objects.get(
                email=payload['email'],
                username=payload['username']
            )
            filepath = os.path.join(
                '/chan/' + settings.MEDIA_ROOT,
                f'uploads/avatar/{uuid}.jpg'
            )

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertIn('avatar', res.data)
            self.assertEqual(user.avatar.path, filepath)

    def test_create_user_with_default_avatar(self):
        """Test that creating a new user without upload avatar will
        got default avatar"""
        pass

    def test_create_user_invalid_email(self):
        """Test creating a new user with invalid payload
        (email blank)"""
        payload = create_payload(email='')

        res = self.client.post(SIGNUP_USER_URL, payload)
        is_exists = get_user_model().objects.filter(
            email=payload['email'],
            username=payload['username']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(is_exists)

    def test_create_user_invalid_username(self):
        """Test creating a new user with invalid payload
        (email blank)"""
        payload = create_payload(username='')

        res = self.client.post(SIGNUP_USER_URL, payload)
        is_exists = get_user_model().objects.filter(
            email=payload['email'],
            username=payload['username']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(is_exists)

    def test_create_with_exists_user(self):
        """Test creating a new user with existing user
        raises 400 status code"""
        payload = create_payload()
        create_user(**payload)

        res = self.client.post(SIGNUP_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_password_too_short(self):
        """Test creating a new user with password less than 6 character
        raises 400 status code"""
        payload = create_payload(password='wr')

        res = self.client.post(SIGNUP_USER_URL, payload)
        is_exists = get_user_model().objects.filter(
            email=payload['email'],
            username=payload['username']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(is_exists)
