import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('csv_to_json', Path(__file__).parents[1] / 'scripts/csv_to_json.py')
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


class CsvToJson(unittest.TestCase):
    def convert(self, content, **options):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory)/'in.csv', Path(directory)/'out.json'
            source.write_bytes(content)
            converter.convert_csv_to_json(source, output, **options)
            return json.loads(output.read_text())

    def test_text_and_quoted_special_characters(self):
        self.assertEqual(self.convert('name,code,note\r\n"Áda",001,"say ""hi""\nagain"\r\n'.encode()),
                         [{'name':'Áda','code':'001','note':'say "hi"\nagain'}])

    def test_delimiters_and_formatting(self):
        for delimiter in [';', '\t', '|']:
            self.assertEqual(self.convert(f'a{delimiter}b\n1{delimiter}2\n'.encode(), indent=0), [{'a':'1','b':'2'}])
        self.assertEqual(self.convert(b'a:b\n1:2\n', delimiter=':'), [{'a':'1','b':'2'}])

    def test_empty_bom_and_header_only(self):
        self.assertEqual(self.convert(b''), [])
        self.assertEqual(self.convert(b'\xef\xbb\xbfa,b\n'), [])

    def test_invalid_inputs_preserve_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory)/'in.csv', Path(directory)/'out.json'
            for content in [b'a,a\n1,2\n', b'a,b\n1\n', b'a,b\n"unclosed,2', b'a,b\n\xff,2']:
                source.write_bytes(content); output.write_bytes(b'original')
                self.assertEqual(converter.main([str(source),str(output)]), 1)
                self.assertEqual(output.read_bytes(), b'original')

    def test_size_limit(self):
        with self.assertRaisesRegex(ValueError, 'maximum bytes'):
            self.convert(b'a,b\n1,2\n', maximum_bytes=4)


if __name__ == '__main__':
    unittest.main()
