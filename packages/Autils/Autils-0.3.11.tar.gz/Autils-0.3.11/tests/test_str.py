import unittest
from autils import String


class Str(unittest.TestCase):

    def test_gen(self):
        self.assertEqual(len(String.generate(16)), 16)

    def test_gen_digits(self):
        print(String.generate_digits(16))

    def test_gen_strs(self):
        print(String.generate_strs(32))

    def test_alphabet_number(self):
        self.assertEqual(String.get_alphabet_number("Z"), 26)


if __name__ == "__main__":
    unittest.main()
