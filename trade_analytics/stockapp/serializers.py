from rest_framework import serializers
from stockapp import models as md


# class StockmetaSerializer(serializers.Serializer):
#    id = serializers.IntegerField(read_only=True)
#    Company = serializers.CharField(required=False, allow_blank=True, max_length=100)
#    Symbol = serializers.CharField(required=True, allow_blank=False, max_length=6)
#
#   
#
#    def create(self, validated_data):
#        """
#        Create and return a new `Snippet` instance, given the validated data.
#        """
#        return md.Stockmeta.objects.create(**validated_data)
#
#    def update(self, instance, validated_data):
#        """
#        Update and return an existing `Snippet` instance, given the validated data.
#        """
#        instance.Company = validated_data.get('Company', instance.Company)
#        instance.Symbol = validated_data.get('Symbol', instance.Symbol)
#        instance.save()
#        return instance


class StockmetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = md.Stockmeta
        fields = ('id', 'Company', 'Symbol')