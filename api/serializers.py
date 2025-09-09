
# ОПИСАНИЕ ВСЕХ ВВОДИМЫХ ПЕРЕМЕННЫХ. ДЛЯ ФОРМИРОВАНИЯ RAW_DATA

from rest_framework import serializers

#### для 1 спринта

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    fam = serializers.CharField(max_length=20, required=False, allow_blank=True)
    name = serializers.CharField(max_length=20, required=False, allow_blank=True)
    otc = serializers.CharField(max_length=20, required=False, allow_blank=True)

class CoordsSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    height = serializers.IntegerField(required=False, allow_null=True)

class LevelSerializer(serializers.Serializer):
    winter = serializers.CharField(max_length=5, required=False, allow_blank=True)
    spring = serializers.CharField(max_length=5, required=False, allow_blank=True)
    summer = serializers.CharField(max_length=5, required=False, allow_blank=True)
    autumn = serializers.CharField(max_length=5, required=False, allow_blank=True)

class ImageSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    img = serializers.FileField()

class SubmitDataSerializer(serializers.Serializer):
    beautyTitle = serializers.CharField(max_length=100, required=False, allow_blank=True)
    title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    other_titles = serializers.CharField(max_length=100, required=False, allow_blank=True)
    connect = serializers.CharField(max_length=500, required=False, allow_blank=True)
    user = UserSerializer()
    coords = CoordsSerializer()
    # level = LevelSerializer()
    images = ImageSerializer(many=True, required=True)


#### для 2 спринта


class PerevalDetailSerializer(serializers.Serializer):
    """Сериализатор для детального просмотра перевала"""
    id = serializers.IntegerField()
    beauty_title = serializers.CharField()
    title = serializers.CharField()
    other_titles = serializers.CharField()
    connect = serializers.CharField()
    add_time = serializers.DateTimeField()
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    status = serializers.CharField()
    date_added = serializers.DateTimeField()
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        images = []
        for pereval_image in obj.images.all():
            images.append({
                'title': pereval_image.image.title,
                'data': pereval_image.image.img
            })
        return images


class PerevalUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления перевала"""
    beauty_title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    other_titles = serializers.CharField(max_length=500, required=False, allow_blank=True)
    connect = serializers.CharField(max_length=500, required=False, allow_blank=True)
    coords = CoordsSerializer(required=False)
    level = LevelSerializer(required=False)
    images = ImageSerializer(many=True, required=False)


class PerevalListSerializer(serializers.Serializer):
    """Сериализатор для списка перевалов пользователя"""
    id = serializers.IntegerField()
    beauty_title = serializers.CharField()
    title = serializers.CharField()
    other_titles = serializers.CharField()
    connect = serializers.CharField()
    add_time = serializers.DateTimeField()
    coords = CoordsSerializer()
    level = LevelSerializer()
    status = serializers.CharField()
    date_added = serializers.DateTimeField()



