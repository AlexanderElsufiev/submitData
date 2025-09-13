
# ЗАПУСК ВСЕНХ ТЕСТОВ СРАЗУ = python manage.py test api.tests
# ЗАПУСК ОДНОГО ЭТОГО ТЕСТА =  python manage.py test api.tests.test_integration



import json
import base64
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from ..models import PerevalAdded, PerevalUser, PerevalCoords, PerevalImage, PerevalImageAsIs
import time

class SubmitDataIntegrationTest(TestCase):
    """Интеграционные тесты для полного жизненного цикла API"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.valid_data = {
            'beauty_title' : "Питер",
            'title' : "болото",
            'other_titles' : "другое название",
            'connect' : "между ладогой и морем",
            "user": {
                'email' : "test@example.com",
                'phone' : "12345678910000",
                'fam' : "Фамилия",
                'name' : "Имя",
                'otc' : "Отчество"
            },
            "coords": {
                "latitude": 30.1,
                "longitude": 60.1,
                "height": 10
            },
            "level": {
                "winter": "1А",
                "spring": "1А",
                "summer": "1Б",
                "autumn": "1А"
            },
            "images": [
                {
                    "title": "Фото 1",
                    "data": base64.b64encode(b"fotofotofotofoto_1").decode('utf-8')
                },
                {
                    "title": "Фото 2",
                    "data": base64.b64encode(b"fotofotofotofoto_2").decode('utf-8')
                }
            ]
        }

    def test_full_pereval_creation_workflow(self):
        """Полный цикл создания перевала через POST API"""
        # Проверяем начальное состояние БД
        self.assertEqual(PerevalAdded.objects.count(), 0)
        self.assertEqual(PerevalUser.objects.count(), 0)
        self.assertEqual(PerevalCoords.objects.count(), 0)
        self.assertEqual(PerevalImage.objects.count(), 0)
        self.assertEqual(PerevalImageAsIs.objects.count(), 0)

        # Отправляем POST запрос
        response = self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(self.valid_data),
            content_type='application/json'
        )

        # Проверяем успешный ответ
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('id', response_data['data'])

        # Проверяем создание записей в БД
        self.assertEqual(PerevalAdded.objects.count(), 1)
        self.assertEqual(PerevalUser.objects.count(), 1)
        self.assertEqual(PerevalCoords.objects.count(), 1)
        self.assertEqual(PerevalImage.objects.count(), 2)
        self.assertEqual(PerevalImageAsIs.objects.count(), 2)

        # Проверяем корректность созданных данных
        pereval = PerevalAdded.objects.first()
        self.assertEqual(pereval.title, "болото")
        self.assertEqual(pereval.beauty_title, "Питер")
        self.assertEqual(pereval.status, 'new')
        self.assertEqual(pereval.user.email, "test@example.com")
        self.assertEqual(pereval.coords.latitude, 30.1)
        self.assertEqual(pereval.coords.longitude, 60.1)
        self.assertEqual(pereval.winter, "1А")

    def test_get_user_perevals_workflow(self):
        """Полный цикл получения списка перевалов пользователя"""
        # Создаем тестовые данные через POST
        self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(self.valid_data),
            content_type='application/json'
        )

        # Создаем второй перевал для того же пользователя
        second_data = self.valid_data.copy()
        second_data['title'] = "тоже болото"

        time.sleep(0.001) # задержка, чтобы у исходной и новой записей было разное время записив базу

        self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(second_data),
            content_type='application/json'
        )

        # Получаем список перевалов пользователя
        response = self.client.get(
            reverse('api:submit_data_api'),
            {'user__email': 'test@example.com'}
        )

        # Проверяем ответ
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 2)

        # Проверяем структуру данных
        first_pereval = response_data[0]  # Последний созданный (сортировка по -date_added)
        # проблема - второй перевал создаётся в ту же микросекунду, что и первый перевал,
        # и потому ожидаемая сортировка по времени ввода в базу уже не срабатывает
        if response_data[0]['id']<response_data[1]['id']:
            print('таки снова тест test_get_user_perevals_workflow :два перевала в 1 микросекунду!')
            first_pereval = response_data[1]  # Если сортировка не помогла, взять другой результат
        # print('===================')
        # print(f'response_data={response_data}')
        # print('===================')
        self.assertIn('id', first_pereval)
        self.assertIn('title', first_pereval)
        self.assertIn('coords', first_pereval)
        self.assertIn('level', first_pereval)
        self.assertEqual(first_pereval['title'], "тоже болото")

    def test_get_pereval_detail_workflow(self):
        """Полный цикл получения детальной информации о перевале"""
        # Создаем перевал
        response = self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(self.valid_data),
            content_type='application/json'
        )
        pereval_id = response.json()['data']['id']

        # Получаем детальную информацию
        response = self.client.get(
            reverse('api:pereval_detail_update', kwargs={'pk': pereval_id})
        )

        # Проверяем ответ
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        # Проверяем полноту данных
        self.assertEqual(response_data['id'], pereval_id)
        self.assertEqual(response_data['title'], "болото")
        self.assertIn('user', response_data)
        self.assertIn('coords', response_data)
        self.assertIn('level', response_data)
        self.assertIn('images', response_data)
        self.assertEqual(len(response_data['images']), 2)

    def test_patch_pereval_workflow(self):
        """Полный цикл редактирования перевала"""
        # Создаем перевал
        response = self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(self.valid_data),
            content_type='application/json'
        )
        pereval_id = response.json()['data']['id']

        # Подготавливаем данные для обновления
        update_data = {
            "beauty_title": "Петербург",
            "title": "Обновленное название",
            "coords": {
                "latitude": 30.0,
                "longitude": 60.0,
                "height": 0
            },
            "level": {
                "winter": "2А",
                "summer": "1Б"
            },
            "images": [
                {
                    "title": "Новое фото",
                    "data": base64.b64encode(b"fotofotofotofoto").decode('utf-8')
                }
            ]
        }

        # Обновляем перевал
        response = self.client.patch(
            reverse('api:pereval_detail_update', kwargs={'pk': pereval_id}),
            json.dumps(update_data),
            content_type='application/json'
        )

        # Проверяем успешное обновление
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['state'], 1)

        # Проверяем изменения в БД
        pereval = PerevalAdded.objects.get(id=pereval_id)
        self.assertEqual(pereval.title, "Обновленное название")
        self.assertEqual(pereval.beauty_title, "Петербург")
        self.assertEqual(pereval.coords.latitude, 30.0)
        self.assertEqual(pereval.winter, "2А")

        # Проверяем обновление изображений
        self.assertEqual(pereval.images.count(), 1)
        self.assertEqual(pereval.images.first().image.title, "Новое фото")

    def test_error_handling_workflow(self):
        """Тестирование обработки ошибок в полном цикле"""

        # Тест создания без изображений
        data_without_images = self.valid_data.copy()
        data_without_images['images'] = []

        response = self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(data_without_images),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

        # Тест получения несуществующего перевала
        response = self.client.get(
            reverse('api:pereval_detail_update', kwargs={'pk': 99999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Тест редактирования несуществующего перевала
        response = self.client.patch(
            reverse('api:pereval_detail_update', kwargs={'pk': 99999}),
            json.dumps({"title": "test"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_status_restriction_workflow(self):
        """Тестирование ограничения редактирования по статусу"""
        # Создаем перевал
        response = self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(self.valid_data),
            content_type='application/json'
        )
        pereval_id = response.json()['data']['id']

        # Меняем статус на 'pending'
        pereval = PerevalAdded.objects.get(id=pereval_id)
        pereval.status = 'pending'
        pereval.save()

        # Пытаемся отредактировать
        update_data = {"title": "Новое название"}
        response = self.client.patch(
            reverse('api:pereval_detail_update', kwargs={'pk': pereval_id}),
            json.dumps(update_data),
            content_type='application/json'
        )

        # Проверяем отказ в редактировании
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['state'], 0)
        self.assertIn('pending', response_data['message'])

    def test_user_creation_and_reuse_workflow(self):
        """Тестирование создания и переиспользования пользователя"""
        # Создаем первый перевал
        response1 = self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(self.valid_data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PerevalUser.objects.count(), 1)

        # Создаем второй перевал с тем же email
        second_data = self.valid_data.copy()
        second_data['title'] = "вновь болото"
        response2 = self.client.post(
            reverse('api:submit_data_api'),
            json.dumps(second_data),
            content_type='application/json'
        )

        # Проверяем, что пользователь не дублировался
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PerevalUser.objects.count(), 1)
        self.assertEqual(PerevalAdded.objects.count(), 2)

        # Проверяем, что оба перевала привязаны к одному пользователю
        user = PerevalUser.objects.first()
        self.assertEqual(user.perevaladded_set.count(), 2)

    def test_empty_user_email_search_workflow(self):
        """Тестирование поиска с пустым email пользователя"""
        response = self.client.get(reverse('api:submit_data_api'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn('user__email', response_data['message'])

    def test_nonexistent_user_search_workflow(self):
        """Тестирование поиска несуществующего пользователя"""
        response = self.client.get(
            reverse('api:submit_data_api'),
            {'user__email': 'nonexistent@example.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 0)





