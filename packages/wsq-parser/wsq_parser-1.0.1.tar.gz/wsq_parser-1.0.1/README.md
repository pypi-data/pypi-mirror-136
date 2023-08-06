# wsq_parser (Scraping python pkg)

# Example №1:

```python
from wsq_parser import Parser


class ExampleParser(Parser):
    def parse(self):
        self.log("Getting example soup", 0) # Logging events [info]
        example_page_soup = self.get_page(self.URL) # Got soup for url 


if __name__ == '__main__':
    ExampleParser("https://example.com/", 1)

```
### Another examples:
#### [ParserMejor](https://github.com/WenzzyX/ParserMejor), [ParserElite](https://github.com/WenzzyX/ParserElite)