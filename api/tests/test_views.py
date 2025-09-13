
# ЗАПУСК ВСЕНХ ТЕСТОВ СРАЗУ = python manage.py test api.tests
# ЗАПУСК ОДНОГО ЭТОГО ТЕСТА = python manage.py test api.tests.test_views


from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import PerevalAdded, PerevalUser, PerevalCoords
import json
# from datetime import datetime
from django.utils import timezone


class SubmitDataAPIViewTest(TestCase):
    """Тесты для SubmitDataAPIView"""

    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'beauty_title' : "Питер",
            'title' : "болото",
            'other_titles' : "другое название",
            'connect' : "между ладогой и морем",
            "user": {
                "email": "api@test.com",
                'phone': "12345678910000",
                'fam': "Фамилия",
                'name': "Имя",
                'otc': "Отчество"
            },
            "coords": {
                "latitude": 30.1,
                "longitude": 60.1,
                "height": 10
            },
            "level": {
                "winter": "2А",
                "spring": "1Б",
                "summer": "1А",
                "autumn": "1Б"
            },
            "images": [
                {
                    "title": "Тест фото1",
                    "data": "fotofotofotofoto"
                },
                {
                    "title": "Тест фото2",
                    "data": "fotofotofotofotofoto"
                }
            ]
        }

    def test_post_success(self):
        """Тест успешного создания записи"""
        response = self.client.post(
            reverse('api:submit_data_api'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('id', data['data'])

    def test_post_no_images_error(self):
        """Тест ошибки при отсутствии изображений"""
        payload = self.valid_payload.copy()
        payload['images'] = []

        response = self.client.post(
            reverse('api:submit_data_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_by_email_success(self):
        """Тест получения списка перевалов по email"""
        # Создаем запись
        self.client.post(
            reverse('api:submit_data_api'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        # Получаем список
        response = self.client.get(
            reverse('api:submit_data_api'),
            {'user__email': 'api@test.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # print(f'data={data}')
        self.assertEqual(len(data), 1)

    def test_get_missing_email_error(self):
        """Тест ошибки при отсутствии параметра email"""
        response = self.client.get(reverse('api:submit_data_api'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("Параметр user__email обязателен", data['message'])

    def test_get_nonexistent_user(self):
        """Тест получения списка для несуществующего пользователя"""
        response = self.client.get(
            reverse('api:submit_data_api'),
            {'user__email': 'nonexistent@test.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])


class PerevalDetailUpdateAPIViewTest(TestCase):
    """Тесты для PerevalDetailUpdateAPIView"""

    def setUp(self):
        self.client = APIClient()
        self.user = PerevalUser.objects.create(
            email="test@test.com",
            fam="Фамилия",
            name="Имя"
        )
        self.coords = PerevalCoords.objects.create(
            latitude=30.0,
            longitude=60.0,
            height=10
        )
        self.pereval = PerevalAdded.objects.create(
            beauty_title="Питер",
            title="болото",
            # add_time=datetime.now(),
            add_time=timezone.now(),
            winter="1А",
            summer="1Б",
            user=self.user,
            coords=self.coords
        )

    def test_get_detail_success(self):
        """Тест получения детальной информации о перевале"""
        response = self.client.get(
            reverse('api:pereval_detail_update', kwargs={'pk': self.pereval.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['title'], "болото")
        self.assertEqual(data['user']['email'], "test@test.com")

    def test_get_detail_not_found(self):
        """Тест получения несуществующего перевала"""
        response = self.client.get(
            reverse('api:pereval_detail_update', kwargs={'pk': 999})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_success(self):
        """Тест успешного обновления перевала"""
        update_data = {
            "beauty_title": "Питер утонул",
            "coords": {
                "height": -10
            }
        }

        response = self.client.patch(
            reverse('api:pereval_detail_update', kwargs={'pk': self.pereval.id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # print(f'data={data}') #  data={'state': 1, 'message': 'Запись успешно обновлена'}
        self.assertEqual(data['state'], 1)

    def test_patch_wrong_status(self):
        """Тест ошибки обновления при неподходящем статусе"""
        self.pereval.status = 'accepted'
        self.pereval.save()

        update_data = {"title": "болото2"}
        response = self.client.patch(
            reverse('api:pereval_detail_update', kwargs={'pk': self.pereval.id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['state'], 0)

    def test_patch_not_found(self):
        """Тест обновления несуществующего перевала"""
        response = self.client.patch(
            reverse('api:pereval_detail_update', kwargs={'pk': 999}),
            data=json.dumps({"title": "Тест"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class SubmitFormViewTest(TestCase):
    """Тесты для SubmitFormView"""
    def test_form_view_renders(self):
        """Тест отображения submit_form.html формы - проверка на содержание некоей строки, содержащейся в  html """
        response = self.client.get(reverse('api:submit_form'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестирование API отправки данных в ФСТР')



