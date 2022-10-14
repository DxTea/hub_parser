import unittest
from parser import check_pages_in_db


class TestCheckPagesInDb(unittest.TestCase):
    def test_check_extract_pages(self):
        pages = [('1', 1), ('2', 2), ('3', 3), ('15', 4), ('16', 5), ("17", 6)]
        db_links = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
        true_pages = [('15', 4), ('16', 5), ("17", 6)]
        self.assertEqual(check_pages_in_db(pages, db_links), true_pages)  # add assertion here

    def test_check_no_new_pages(self):
        pages = [('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ("6", 6)]
        db_links = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
        true_pages = []
        self.assertEqual(check_pages_in_db(pages, db_links), true_pages)  # add assertion here

    def test_check_new_pages(self):
        pages = [('15', 1), ('16', 2), ('17', 3), ('18', 4), ('19', 5), ("20", 6)]
        db_links = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
        true_pages = [('15', 1), ('16', 2), ('17', 3), ('18', 4), ('19', 5), ("20", 6)]
        self.assertEqual(check_pages_in_db(pages, db_links), true_pages)  # add assertion here


if __name__ == '__main__':
    unittest.main()
