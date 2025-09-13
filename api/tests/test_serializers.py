
# ЗАПУСК ВСЕНХ ТЕСТОВ СРАЗУ = python manage.py test api.tests
# ЗАПУСК ОДНОГО ЭТОГО ТЕСТА = python manage.py test api.tests.test_serializers

from django.test import TestCase
from ..serializers import UserSerializer, CoordsSerializer, LevelSerializer, ImageSerializer, SubmitDataSerializer, StatusSerializer


class UserSerializerTest(TestCase):
    """Тесты сериализатора пользователя"""

    def test_valid_user_data(self):
        """Тест валидации корректных данных пользователя"""
        data = {
            'email': "test@example.com",
            'phone': "12345678910000",
            'fam' : "Фамилия",
            'name' : "Имя",
            'otc' : "Отчество"
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_empty_user_data(self):
        """Тест валидации пустых данных пользователя"""
        data = {}
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())  # Все поля необязательные


class CoordsSerializerTest(TestCase):
    """Тесты сериализатора координат"""

    def test_valid_coords_data(self):
        """Тест валидации корректных координат"""
        data = {
            'latitude': 30.1,
            'longitude': 60.1,
            'height': 10
        }
        serializer = CoordsSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_coords_with_null_values(self):
        """Тест координат с null значениями"""
        data = {
            'latitude': None,
            'longitude': None,
            'height': None
        }
        serializer = CoordsSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class LevelSerializerTest(TestCase):
    """Тесты сериализатора уровней сложности"""

    def test_valid_level_data(self):
        """Тест валидации уровней сложности"""
        data = {
            'winter': '2А',
            'spring': '1БББ',
            'summer': '1ААААА',
            'autumn': '1Б'
        }
        serializer = LevelSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class ImageSerializerTest(TestCase):
    """Тесты сериализатора изображений"""

    def test_valid_image_data(self):
        """Тест валидации изображения"""
        data = {
            'title': "Тест фото",
            'data': "fotofotofotofoto"
        }
        serializer = ImageSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_title(self):
        """Тест ошибки при отсутствии названия"""
        data = {
            'data': "fotofotofotofoto"
        }
        serializer = ImageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)


class SubmitDataSerializerTest(TestCase):
    """Тесты основного сериализатора для создания записи"""

    def test_valid_submit_data(self):
        """Тест валидации полных данных для создания"""
        data = {
            'beauty_title': "Питер",
            'title': "болото",
            'user': {
                'email': 'test@example.com',
                'fam': "Фамилия",
                'name': 'Имя'
            },
            'coords': {
                'latitude': 30.1,
                'longitude': 60.1,
                'height': 10
            },
            'level': {
                'winter': '1А',
                'summer': '1А'
            },
            'images': [
                {
                    'title': 'Фото 1',
                    'data': "fotofotofotofoto"
                }
            ]
        }
        serializer = SubmitDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_images(self):
        """Тест ошибки при отсутствии изображений"""
        data = {
            'title': 'Тест',
            'user': {'email': 'test@test.com'},
            'coords': {},
            'level': {}
        }
        serializer = SubmitDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('images', serializer.errors)





class StatusSerializerTest(TestCase):
    """Тесты валидации статусов"""

    def test_valid_invalid_status_choices(self):
        """Тест (ин)валидных статусов"""
        valid_statuses = ['new', 'pending', 'accepted', 'rejected']
        invalid_statuses = ['pending2', 'invalid', 'unknown', '','new1']

        for status in valid_statuses:
            data = {'status': status}
            serializer = StatusSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Статус {status} должен быть валидным")

        for status in invalid_statuses:
            data = {'status': status}
            serializer = StatusSerializer(data=data)
            self.assertFalse(serializer.is_valid(), f"Статус {status} должен быть невалидным")
            self.assertIn('status', serializer.errors)





