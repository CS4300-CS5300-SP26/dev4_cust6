from rest_framework import serializers
from .models import GradeReport, Card, CardCollection


class GradeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeReport
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class CardCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardCollection
        fields = '__all__'