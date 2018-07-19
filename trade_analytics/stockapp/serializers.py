from rest_framework import serializers
from stockapp import models as md


class StockmetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = md.Stockmeta
        fields = ('id', 'Company', 'Symbol')
