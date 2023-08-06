# wsq_parser (Scraping python pkg)

# Example №1:

```python
from wsq_parser import Parser


class EliteParser(Parser):
    def parse(self):
        self.log("123", 0)


if __name__ == '__main__':
    EliteParser("https://google.com/", 1)

```