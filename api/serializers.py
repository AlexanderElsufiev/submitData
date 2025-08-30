
# ОПИСАНИЕ ВСЕХ ВВОДИМЫХ ПЕРЕМЕННЫХ. ДЛЯ ФОРМИРОВАНИЯ RAW_DATA

from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    fam = serializers.CharField(max_length=20, required=False, allow_blank=True)
    name = serializers.CharField(max_length=20, required=False, allow_blank=True)
    otc = serializers.CharField(max_length=20, required=False, allow_blank=True)

class CoordsSerializer(serializers.Serializer):
    latitude = serializers.CharField(max_length=10, required=False, allow_blank=True)
    longitude = serializers.CharField(max_length=10, required=False, allow_blank=True)
    height = serializers.CharField(max_length=10, required=False, allow_blank=True)

class LevelSerializer(serializers.Serializer):
    winter = serializers.CharField(max_length=5, required=False, allow_blank=True)
    summer = serializers.CharField(max_length=5, required=False, allow_blank=True)
    autumn = serializers.CharField(max_length=5, required=False, allow_blank=True)
    spring = serializers.CharField(max_length=5, required=False, allow_blank=True)

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
    level = LevelSerializer()
    images = ImageSerializer(many=True, required=True)

