from django.test import TestCase

from analytics_automated.models import Backend

class CategoryMethodTests(TestCase):

    cat = Category(name='test',views=-1, likes=0)
                cat.save()
                self.assertEqual((cat.views >= 0), True)
