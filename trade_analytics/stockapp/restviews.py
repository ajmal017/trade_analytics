from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from rest_framework import permissions

from rest_framework import generics


from . import models as mds
from . import serializers as srl

#########################################################################
# using MIXINS
#########################################################################

class StockmetaList(generics.ListCreateAPIView):
    queryset = mds.Stockmeta.objects.all()
    serializer_class = srl.StockmetaSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class StockmetaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = mds.Stockmeta.objects.all()
    serializer_class = srl.StockmetaSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)



#########################################################################
# Class Based Views REST
#########################################################################

# class StockmetaList(APIView):
#     """
#     List all snippets, or create a new snippet.
#     """
#     def get(self, request, format=None):
#         snippets = mds.Stockmeta.objects.all()
#         serializer = srl.StockmetaSerializer(snippets, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = srl.StockmetaSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class StockmetaDetail(APIView):
#     """
#     Retrieve, update or delete a snippet instance.
#     """
#     def get_object(self, pk):
#         try:
#             return mds.Stockmeta.objects.get(pk=pk)
#         except mds.Stockmeta.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = srl.StockmetaSerializer(snippet)
#         return Response(serializer.data)

#     def put(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = srl.StockmetaSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



