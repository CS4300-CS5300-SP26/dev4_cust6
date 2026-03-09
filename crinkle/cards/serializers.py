from rest_framework import serializers
from .models import GradeReport, Card, CardCollection


class GradeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeReport
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    date_scanned = serializers.DateTimeField(format="%D %H:%M")

    class Meta:
        model = Card
        fields = ['user', 'name', 'date_scanned', 'grading_notes', 'picture_path', 'user_notes']


class CardCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardCollection
        fields = '__all__'
