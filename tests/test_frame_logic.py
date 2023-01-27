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
