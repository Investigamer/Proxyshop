import unittest
from proxyshop.frame_logic import *

class Test_frame_logic(unittest.TestCase):
    def test_fix_color_pair(self):
        self.assertEqual(fix_color_pair("WU"), "WU", "Correct order untouched")
        self.assertEqual(fix_color_pair("UW"), "WU", "Incorrect order fixed")
        self.assertEqual(fix_color_pair("WUBRG"), None, "Incorrect # of color identities detected (!=2)")
        
    def test_fix_color_triple(self):
        self.assertEqual(fix_color_triple("UBR"), "UBR", "Correct order untouched")
        self.assertEqual(fix_color_triple("RUB"), "UBR", "Incorrect order fixed")
        self.assertEqual(fix_color_triple("W"), None, "Incorrect # of color identities detected (<3)")
        self.assertEqual(fix_color_triple("WUBRG"), None, "Incorrect # of color identities detected (>3)")

    def test_fix_color_quadrouple(self):
        self.assertEqual(fix_color_quadrouple("UBRG"), "UBRG", "Correct order untouched")
        self.assertEqual(fix_color_quadrouple("GRBU"), "UBRG", "Incorrect order fixed")
        self.assertEqual(fix_color_quadrouple("W"), None, "Incorrect # of color identities detected (<4)")
        self.assertEqual(fix_color_quadrouple("WUBRG"), None, "Incorrect # of color identities detected (>4)")

    def test_fix_color_quintouples(self):
        self.assertEqual(fix_color_quintouple("WUBRG"), "WUBRG", "Correct order untouched")
        self.assertEqual(fix_color_quintouple("GRBUW"), "WUBRG", "Incorrect order fixed")
        self.assertEqual(fix_color_quintouple("W"), None, "Incorrect # of color identities detected (<5)")