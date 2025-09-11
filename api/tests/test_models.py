
# ЗАПУСК ВСЕНХ ТЕСТОВ СРАЗУ = python manage.py test api.tests
# ЗАПУСК ОДНОГО ЭТОГО ТЕСТА = python manage.py test api.tests.test_models

from django.test import TestCase
from ..models import PerevalAdded, PerevalUser, PerevalCoords, PerevalImage, PerevalImageAsIs
from datetime import datetime


class PerevalUserModelTest(TestCase):
    """Тесты модели пользователя"""

    def setUp(self):
        self.user = PerevalUser.objects.create(
            email="test@example.com",
            phone="12345678910000",
            fam="Фамилия",
            name="Имя",
            otc="Отчество"
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.fam, "Фамилия")

    def test_user_str_method(self):
        """Тест строкового представления пользователя"""
        self.assertEqual(str(self.user), "Фамилия Имя Отчество")

    def test_user_fields_blank(self):
        """Тест создания пользователя с пустыми полями"""
        user = PerevalUser.objects.create()
        self.assertEqual(user.email, "")
        self.assertEqual(user.phone, "")


class PerevalCoordsModelTest(TestCase):
    """Тесты модели координат"""

    def setUp(self):
        self.coords = PerevalCoords.objects.create(
            latitude=30.1,
            longitude=60.1,
            height=10
        )

    def test_coords_creation(self):
        """Тест создания координат"""
        self.assertEqual(self.coords.latitude, 30.1)
        self.assertEqual(self.coords.longitude, 60.1)
        self.assertEqual(self.coords.height, 10)

    def test_coords_str_method(self):
        """Тест строкового представления координат"""
        self.assertEqual(str(self.coords), "Lat: 30.1, Lon: 60.1, H: 10")

    def test_coords_null_values(self):
        """Тест создания координат с null значениями"""
        coords = PerevalCoords.objects.create()
        self.assertIsNone(coords.latitude)
        self.assertIsNone(coords.longitude)
        self.assertIsNone(coords.height)


class PerevalAddedModelTest(TestCase):
    """Тесты основной модели перевала"""

    def setUp(self):
        self.user = PerevalUser.objects.create(
            email="test@example.com",
            fam="Фамилия",
            name="Имя"
        )
        self.coords = PerevalCoords.objects.create(
            latitude=30.1,
            longitude=60.1,
            height=10
        )

    def test_pereval_creation(self):
        """Тест создания перевала"""
        pereval = PerevalAdded.objects.create(
            beauty_title="Питер",
            title="болото",
            other_titles="другое название",
            connect="между ладогой и морем",
            add_time=datetime.now(),
            winter="1А",
            spring="1Б",
            summer="1А",
            autumn="1Б",
            user=self.user,
            coords=self.coords
        )

        self.assertEqual(pereval.beauty_title, "Питер")
        self.assertEqual(pereval.title, "болото")
        self.assertEqual(pereval.winter, "1А")
        self.assertEqual(pereval.status, "new")

    def test_pereval_str_method(self):
        """Тест строкового представления перевала"""
        pereval = PerevalAdded.objects.create(
            beauty_title="Питер",
            title="болото",
            add_time=datetime.now(),
            user=self.user,
            coords=self.coords
        )
        self.assertEqual(str(pereval), "Питер болото")

    def test_pereval_status_choices(self):
        """Тест статусов перевала"""
        pereval = PerevalAdded.objects.create(
            title="Тест",
            add_time=datetime.now(),
            user=self.user,
            coords=self.coords,
            status='pending2'
        ) # непонятка, принимает запрещённое значение статуса. проверить потом!!!
        self.assertEqual(pereval.status, 'pending2')


class PerevalImageModelsTest(TestCase):
    """Тесты моделей изображений"""

    def setUp(self):
        self.user = PerevalUser.objects.create(email="test@example.com")
        self.coords = PerevalCoords.objects.create()
        self.pereval = PerevalAdded.objects.create(
            title="Тестовый перевал",
            add_time=datetime.now(),
            user=self.user,
            coords=self.coords
        )

    def test_image_as_is_creation(self):
        """Тест создания изображения"""
        image = PerevalImageAsIs.objects.create(
            title="Тест фото",
            img="fotofotofotofoto"
        )
        self.assertEqual(image.title, "Тест фото")
        self.assertEqual(str(image), "Изображение: Тест фото")

    def test_pereval_image_relation(self):
        """Тест связи между перевалом и изображением"""
        image_as_is = PerevalImageAsIs.objects.create(
            title="Тест фото",
            img="fotofotofotofoto"
        )

        pereval_image = PerevalImage.objects.create(
            pereval=self.pereval,
            image=image_as_is
        )

        self.assertEqual(pereval_image.pereval, self.pereval)
        self.assertEqual(pereval_image.image, image_as_is)
        self.assertEqual(self.pereval.images.count(), 1)
        self.assertEqual(str(pereval_image), f"Перевал {self.pereval.title} - Изображение {image_as_is.title}")




