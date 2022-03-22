from django.core.cache import cache
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from api.models import Package, PackagePermission, Booking, DeletedData
from api.utils import create_access_token, auth_header
from api.utils import group_has_perm, user_has_group_perm

class PackageViewSetTestCase(APITestCase):
    def test_only_logged_in_users_can_view_packages(self):
        response = self.client.get('/api/v1/packages/')
        self.assertEqual(response.status_code, 401)

        user = User.objects.create(username='user')
        token = create_access_token(user)
        response = self.client.get(
            '/api/v1/packages/', **auth_header(token)
        )
        self.assertEqual(response.status_code, 200)

        token.scope = 'packages'
        token.save()
        response = self.client.get(
            '/api/v1/packages/', **auth_header(token)
        )
        self.assertEqual(response.status_code, 403)

class PackagePermissionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user')
        self.auth_user = auth_header(create_access_token(self.user))
        self.package = Package.objects.create(category='a', name='package', price=0.0, rating='medium', tour_length=1)
        self.other_user = User.objects.create(username='other_user')
        self.auth_other_user = auth_header(create_access_token(self.other_user))
        self.other_package = Package.objects.create(category='a', name='other_package', price=1.0, rating='medium', tour_length=1)
        PackagePermission.set_can_write(self.user, self.package)
        PackagePermission.set_can_write(self.other_user, self.other_package)

    def test_user_cannot_write_other_users_packages(self):
        self.assertTrue(PackagePermission.can_write(self.user, self.package))
        self.assertFalse(PackagePermission.can_write(self.user, self.other_package))

    def test_user_cannot_access_other_users_packages(self):
        response = self.client.get(
            '/api/v1/packages/{}/'.format(self.package.id),
            **self.auth_user
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.package.id)
        self.assertCountEqual(
            response.data.keys(),
            [
                'id', 'category', 'name', 'promo', 'price',
                'tour_length', 'rating', 'start'
            ]
        )

        response = self.client.get(
            '/api/v1/packages/{}/'.format(self.other_package.id),
            **self.auth_user
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            '/api/v1/packages/{}/'.format(self.other_package.id),
            **self.auth_other_user
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.other_package.id)

class ValidationTestCase(APITestCase):
    def test_invalid_start_date_returns_error(self):
        user = User.objects.create(username='user')
        auth = auth_header(create_access_token(user))
        data = {
            'category': 'tour',
            'name': 'Example',
            'promo': 'promo',
            'price': 12.34,
            'tour_length': 1,
            'rating': 'easy',
            'start': '01/01/2019',
        }
        response = self.client.post('/api/v1/packages/', data, **auth)
        self.assertEqual(response.status_code, 400)
        self.assertRegex(response.data['start'][0], 'wrong format')

        data['start'] = '2019-01-01'
        response = self.client.post('/api/v1/packages/', data, **auth)
        self.assertEqual(response.status_code, 201)

class BookingPerObjectPermissionTestCase(APITestCase):
    def setUp(self):
        self.package = Package.objects.create(
            category='a', name='package',
            price=0.0, rating='medium', tour_length=1
        )

        self.user = User.objects.create(username='user', email='user@localhost')
        self.auth_user = auth_header(create_access_token(self.user))

        self.other_user = User.objects.create(username='other_user', email='other_user@localhost')
        self.auth_other_user = auth_header(create_access_token(self.other_user))

    def test_update_booking(self):
        booking = Booking(
            package=self.package,
            start=timezone.now(),
            name='Adventure',
            email_address=self.user.email
        )
        booking.save()

        self.assertTrue(
            self.user.has_perm('api.change_booking', booking)
        )

        self.assertFalse(
            self.other_user.has_perm('api.change_booking', booking)
        )

        url = '/api/v1/bookings/{}/'.format(booking.id)
        data = { 'name': 'Updated Adventure' }

        response = self.client.patch(url, data, **self.auth_user)
        self.assertEqual(response.status_code, 200)

        response = self.client.patch(url, data, **self.auth_other_user)
        self.assertEqual(response.status_code, 403)
