from .validators import *

from django.test import TestCase


class TaskValidators(TestCase):

    def testAcceptPng(self):
        f = open("submissions/files/test.png", "rb").read()
        self.assertTrue(png(f))

    def testRejectNonpng(self):
        f = open("submissions/files/test.gif", "rb").read()
        self.assertFalse(png(f))

    def testAcceptGif(self):
        f = open("submissions/files/test.gif", "rb").read()
        self.assertTrue(gif(f))

    def testRejectNonGif(self):
        f = open("submissions/files/test.png", "rb").read()
        self.assertFalse(gif(f))

    def testAcceptJpeg(self):
        f = open("submissions/files/test.jpeg", "rb").read()
        self.assertTrue(jpeg(f))

    def testRejectNonJpeg(self):
        f = open("submissions/files/test.gif", "rb").read()
        self.assertFalse(jpeg(f))
