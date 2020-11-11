from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Board

from shitchan.serializers import BoardSerializer


# BOARD_URL = reverse('shitchan:board-list')
MANAGE_BOARD_URL = reverse('shitchan:board-list')


def detail_url(pk):
    """Generate detail url for board"""
    return reverse('shitchan:board-detail', args=[pk])


def create_user(is_admin=False, **params):
    """Helper function to create a new user/superuser"""
    defaults = {
        'username': 'testuser',
        'email': 'test@gmail.com',
        'password': 'testpass'
    }
    defaults.update(**params)

    if is_admin:
        return get_user_model().objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin'
        )

    return get_user_model().objects.create_user(**defaults)


def create_payload(**params):
    """Helper function to create a new payload"""
    defaults = {
        'title': 'test board',
        'code': 'tb'
    }
    defaults.update(**params)

    return defaults


def create_board(user, **params):
    """Helper function to create a new board"""
    defaults = {
        'title': 'Test Board',
        'code': 'tb'
    }
    defaults.update(**params)

    return Board.objects.create(
        user=user, **defaults
    )


class BoardPublicApiTests(TestCase):
    """Test publicly board API (with anonymous user)"""

    def setUp(self):
        self.client = APIClient()

    def test_access_board_list_endpoint(self):
        """Test creating a new board in API"""
        admin_user = create_user(is_admin=True)
        create_board(user=admin_user)
        create_board(user=admin_user, title='political', code='pl')

        res = self.client.get(MANAGE_BOARD_URL)
        boards = Board.objects.all()
        serializer = BoardSerializer(boards, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class BoardPrivateApiTests(TestCase):
    """Test privately board API with user"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_create_board_not_allowed(self):
        """Test that create a board with user is not allowed"""
        payload = create_payload()

        res = self.client.post(MANAGE_BOARD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class BoardAdminApiTests(TestCase):
    """Test privately board API with admin user"""

    def setUp(self):
        self.client = APIClient()
        self.admin = create_user(is_admin=True)
        self.client.force_authenticate(user=self.admin)

    def test_create_board_successful(self):
        """Test that create board with admin user is successful"""
        payload = create_payload()

        res = self.client.post(MANAGE_BOARD_URL, payload)
        board = Board.objects.get(**res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(board.title, payload['title'])
        self.assertEqual(board.code, payload['code'])
        self.assertEqual(board.user, self.admin)

    def test_retrieve_board(self):
        """Test retrieving a board with admin user
        who created that board"""
        board = create_board(user=self.admin)
        url = detail_url(board.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], board.title)
        self.assertEqual(res.data['code'], board.code)

    def test_update_board(self):
        """Test updating a board with admin user
        who created that board"""
        board = create_board(user=self.admin)
        url = detail_url(board.id)
        payload = {
            'title': 'new board',
            'code': 'nb'
        }

        res = self.client.patch(url, payload)
        board.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(board.title, payload['title'])
        self.assertEqual(board.code, payload['code'])

    def test_delete_board(self):
        """Test delete a board with admin user
        who created that board"""
        payload = create_payload()
        board = create_board(user=self.admin, **payload)
        url = detail_url(board.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        is_exists = Board.objects.filter(
            title=payload['title'],
            code=payload['code'],
            user=self.admin
        ).exists()
        self.assertFalse(is_exists)
