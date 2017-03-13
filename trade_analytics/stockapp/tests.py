from django.test import TestCase
from . import models as md

class StockmetaTestCase(TestCase):
    def setUp(self):
        md.Stockmeta.objects.create(name="lion", sound="roar")
        md.Stockmeta.objects.create(name="cat", sound="meow")

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        lion = md.Stockmeta.objects.get(name="lion")
        cat = md.Stockmeta.objects.get(name="cat")
        self.assertEqual(lion.speak(), 'The lion says "roar"')
        self.assertEqual(cat.speak(), 'The cat says "meow"')