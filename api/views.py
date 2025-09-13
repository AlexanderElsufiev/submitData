
from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import * #PerevalAdded, PerevalUser, PerevalCoords, PerevalImage, PerevalImageAsIs
from django.utils import timezone
from .serializers import *  #SubmitDataSerializer, PerevalDetailSerializer, PerevalUpdateSerializer, PerevalListSerializer

class SubmitDataAPIView(APIView):
    """
    REST API endpoint для отправки данных горного перевала
    Использует Django ORM для записи в PostgreSQL

    POST /submitData/ — создать новую запись
    GET /submitData/?user__email=<email> — список записей пользователя
    """

    # ИЗ 1 СПРИНТА ЗАПИСЬ
    def post(self, request, *args, **kwargs):
        try:
            # Получаем вложенные данные пользователя
            user_data = request.data.get('user', {})

            # Создаем или получаем пользователя
            user, created = PerevalUser.objects.get_or_create(
                email=user_data.get('email', ''),
                defaults={
                    'phone': user_data.get('phone', ''),
                    'fam': user_data.get('fam', ''),
                    'name': user_data.get('name', ''),
                    'otc': user_data.get('otc', '')
                }
            )

            # Получаем вложенные данные координат
            coords_data = request.data.get('coords', {})

            # Создаем координаты
            coords = PerevalCoords.objects.create(
                latitude=coords_data.get('latitude', ''),
                longitude=coords_data.get('longitude', ''),
                height=coords_data.get('height', '')
            )

            # Получаем вложенные данные уровней сложности
            level_data = request.data.get('level', {})

            # Создаем основную запись перевала
            pereval = PerevalAdded.objects.create(
                beauty_title=request.data.get('beauty_title', ''),
                title=request.data.get('title', ''),
                other_titles=request.data.get('other_titles', ''),
                connect=request.data.get('connect', ''),
                add_time=timezone.now(), # add_time=datetime.now(), # замена для хорошего тестирования без предупреждений
                winter=level_data.get('winter', ''),
                spring=level_data.get('spring', ''),
                summer=level_data.get('summer', ''),
                autumn=level_data.get('autumn', ''),
                user=user,
                coords=coords,
                # level=level
            )

            # Обрабатываем изображения из массива images
            images_data = request.data.get('images', [])
            images_count = 0

            for image_data in images_data:
                if 'title' in image_data and 'data' in image_data:
                    # Создаем запись изображения в таблице pereval_images_as_is
                    image_as_is = PerevalImageAsIs.objects.create(
                        title=image_data['title'],
                        img=image_data['data']  # Предполагаем, что данные уже в hex формате
                    )

                    # Создаем связь между перевалом и изображением
                    PerevalImage.objects.create(
                        pereval=pereval,
                        image=image_as_is
                    )
                    images_count += 1

            if images_count == 0:
                # Если нет изображений, удаляем созданные записи
                pereval.delete()
                coords.delete()
                if created:  # Удаляем пользователя только если он был создан
                    user.delete()

                return Response(
                    {"error": "Необходимо загрузить хотя бы одно изображение"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                "message": "Данные успешно отправлены",
                "status": "success",
                "data": {
                    "id": pereval.id,
                    "title": f"{pereval.beauty_title} {pereval.title}",
                    "user": f"{user.fam} {user.name} {user.otc}",
                    "coords": f"Lat: {coords.latitude}, Lon: {coords.longitude}",
                    "images_count": images_count,
                    "add_time": pereval.add_time.strftime("%Y-%m-%d %H:%M:%S"), # добавка
                    "date_added": pereval.date_added.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": f"Ошибка при обработке данных: {str(e)}",
                "status": "error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ДЛЯ 2 СПРИНТА GET

    def get(self, request, *args, **kwargs):
        """GET /submitData/?user__email=<email> — список данных обо всех объектах пользователя"""
        try:
            email = request.query_params.get('user__email')

            if not email:
                return Response(
                    {"message": "Параметр user__email обязателен"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = PerevalUser.objects.get(email=email)
            except PerevalUser.DoesNotExist:
                return Response([], status=status.HTTP_200_OK)

            perevals = PerevalAdded.objects.filter(user=user).select_related('coords').order_by('-date_added')

            # СЕРИАЛИЗАТОР вместо ручного формирования
            serializer = PerevalListSerializer(perevals, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": f"Ошибка при получении списка: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubmitFormView(TemplateView):
    """
    Представление для отображения формы тестирования
    """
    template_name = 'api/submit_form.html'




#################################### для 2 спринта



class PerevalDetailUpdateAPIView(APIView):
    """
    GET /submitData/<id> — получить одну запись по id
    PATCH /submitData/<id> — отредактировать запись, если статус 'new'
    """

    def get(self, request, pk, *args, **kwargs):
        """GET /submitData/<id> — получить одну запись (перевал) по её id"""
        try:
            pereval = PerevalAdded.objects.select_related('user', 'coords').prefetch_related('images__image').get(pk=pk)

            # СЕРИАЛИЗАТОР вместо ручного формирования
            serializer = PerevalDetailSerializer(pereval)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except PerevalAdded.DoesNotExist:
            return Response(
                {"message": "Перевал не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": f"Ошибка при получении данных: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



    def patch(self, request, pk, *args, **kwargs):
        """PATCH /submitData/<id> — отредактировать существующую запись, если она в статусе new"""
        try:
            pereval = PerevalAdded.objects.select_related('user', 'coords').get(pk=pk)

            if pereval.status != 'new':
                return Response({
                    "state": 0,
                    "message": f"Запись нельзя редактировать, так как она имеет статус: {pereval.status}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # СЕРИАЛИЗАТОР для валидации
            serializer = PerevalUpdateSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({
                    "state": 0,
                    "message": f"Ошибка валидации данных: {serializer.errors}"
                }, status=status.HTTP_400_BAD_REQUEST)

            validated_data = serializer.validated_data

            # Обновляем основные поля
            for field in ['beauty_title', 'title', 'other_titles', 'connect']:
                if field in validated_data:
                    setattr(pereval, field, validated_data[field])

            # Обновляем уровни сложности
            if 'level' in validated_data:
                level_data = validated_data['level']
                for season in ['winter', 'spring', 'summer', 'autumn']:
                    if season in level_data:
                        setattr(pereval, season, level_data[season])

            # Обновляем координаты
            if 'coords' in validated_data:
                coords_data = validated_data['coords']
                for coord in ['latitude', 'longitude', 'height']:
                    if coord in coords_data:
                        setattr(pereval.coords, coord, coords_data[coord])
                pereval.coords.save()

            # Обновляем изображения
            if 'images' in validated_data:
                # Удаляем старые изображения
                old_images = pereval.images.all()
                for old_image in old_images:
                    old_image.image.delete()
                    old_image.delete()

                # Создаем новые изображения
                for image_data in validated_data['images']:
                    image_as_is = PerevalImageAsIs.objects.create(
                        title=image_data['title'],
                        img=image_data['data']
                    )
                    PerevalImage.objects.create(
                        pereval=pereval,
                        image=image_as_is
                    )

            # Обновляем время изменения

            pereval.date_added = timezone.now()
            pereval.save()

            return Response({
                "state": 1,
                "message": "Запись успешно обновлена"
            }, status=status.HTTP_200_OK)

        except PerevalAdded.DoesNotExist:
            return Response({
                "state": 0,
                "message": "Перевал не найден"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "state": 0,
                "message": f"Ошибка при обновлении записи: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






