from analytics_automated.validators import *

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

    def testAcceptValidPDB(self):
        f = open("submissions/files/1iar.pdb", "rb").read()
        self.assertTrue(pdb_file(f))

    def testRegjectInvalidPDB(self):
        f = open("submissions/files/5ptpA.fasta", "rb").read()
        self.assertFalse(pdb_file(f))

    def testAcceptFasta(self):
        f = open("submissions/files/5ptpA.fasta", "rb").read()
        self.assertTrue(seq(f))

    def testRejectNoSeq(self):
        f = open("submissions/files/5ptpA_noseq.fasta", "rb").read()
        self.assertFalse(seq(f))

    def testRejectEmpty(self):
        f = open("submissions/files/empty.fasta", "rb").read()
        self.assertFalse(seq(f))

    def testRejectNucleotide(self):
        f = open("submissions/files/nucleotide.fasta", "rb").read()
        self.assertFalse(seq(f))

    def testRejectBadSeq(self):
        f = open("submissions/files/5ptpA_badseq.fasta", "rb").read()
        self.assertFalse(seq(f))

    def testAcceptMSA(self):
        f = open("submissions/files/5ptpA_msa.fasta", "rb").read()
        self.assertTrue(seq(f))

    def testRejectBadMSA(self):
        f = open("submissions/files/5ptpA_badmsa.fasta", "rb").read()
        self.assertFalse(seq(f))

    def testRejectBadHeaderMSA(self):
        f = open("submissions/files/5ptpA_badmultipleheader.fasta", "rb").read()
        self.assertFalse(seq(f))

    def testRejectMSAWithBadChar(self):
        f = open("submissions/files/5ptpA_badcharmsa.fasta", "rb").read()
        self.assertFalse(seq(f))
