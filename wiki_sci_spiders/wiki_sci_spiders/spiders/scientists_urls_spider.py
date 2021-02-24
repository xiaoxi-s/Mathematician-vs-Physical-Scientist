import os
import scrapy

from scrapy.selector import Selector


def _get_urls_from_name_href_list(name_href_list, response):
    urls = []
    for i, name_href in enumerate(name_href_list):
        url = response.urljoin(name_href_list[i].css('li a::attr(href)').getall()[0]) + '\n'

        # remove inaccessible urls
        if url.startswith('https://en.wikipedia.org/w/index.php?title='):
            continue

        url = url[len('https://en.wikipedia.org/wiki/'):]
        urls.append(url)

    return urls


class WikiMathURLSpider(scrapy.Spider):
    name = "wiki-math-url"

    have_multi_header = {
        'https://en.wikipedia.org/wiki/List_of_quantitative_analysts': True,
        'https://en.wikipedia.org/wiki/List_of_statisticians': True,
        'https://en.wikipedia.org/wiki/List_of_logicians': True,
        'https://en.wikipedia.org/wiki/List_of_geometers': True,
        'https://en.wikipedia.org/wiki/List_of_actuaries': True,
        'https://en.wikipedia.org/wiki/List_of_game_theorists': False,
        'https://en.wikipedia.org/wiki/List_of_mathematical_probabilists': False
    }
    num_of_headers_to_ignore = {
        'https://en.wikipedia.org/wiki/List_of_quantitative_analysts': 1,
        'https://en.wikipedia.org/wiki/List_of_statisticians': 2,
        'https://en.wikipedia.org/wiki/List_of_logicians': 2,
        'https://en.wikipedia.org/wiki/List_of_geometers': 2,
        'https://en.wikipedia.org/wiki/List_of_actuaries': 1,
        'https://en.wikipedia.org/wiki/List_of_game_theorists': 1,
        'https://en.wikipedia.org/wiki/List_of_mathematical_probabilists': 1
    }

    start_urls = [
        'https://en.wikipedia.org/wiki/List_of_quantitative_analysts',
        'https://en.wikipedia.org/wiki/List_of_statisticians',
        'https://en.wikipedia.org/wiki/List_of_logicians',
        'https://en.wikipedia.org/wiki/List_of_geometers',
        'https://en.wikipedia.org/wiki/List_of_actuaries',
        'https://en.wikipedia.org/wiki/List_of_game_theorists',
        'https://en.wikipedia.org/wiki/List_of_mathematical_probabilists'
    ]

    def __init__(self, url_file_name=None):
        super(WikiMathURLSpider, self).__init__()
        if url_file_name is None:
            self.url_file_name = 'math_urls.txt'
        else:
            self.url_file_name = url_file_name

    def parse(self, response):
        url = response.url

        if self.have_multi_header[url]:
            self._parse_multi_header(response)
        else:
            self._parse_single_header(response)

    def _parse_multi_header(self, response):
        url = response.url
        content = response.xpath('//*[@id="mw-content-text"]/div[1]').get()
        headers = response.xpath('//*[@id="mw-content-text"]/div[1]/h2').getall()

        # locate the list of scientists based on start and end
        start_header = headers[0]
        header_to_be_removed_from = headers[-self.num_of_headers_to_ignore[url]]
        content = content[content.find(start_header): content.find(header_to_be_removed_from)]

        content = Selector(text=content)
        classified_name_href_list = content.css('ul').getall()
        urls = []
        for i, name_href_list in enumerate(classified_name_href_list):
            name_href_list = Selector(text=name_href_list).css('li')
            urls = urls + _get_urls_from_name_href_list(name_href_list, response)

        with open(self.url_file_name, 'a+', encoding='utf-8') as f:
            f.writelines(urls)

    def _parse_single_header(self, response):
        url = response.url
        content = response.xpath('//*[@id="mw-content-text"]/div[1]').get()
        headers = response.xpath('//*[@id="mw-content-text"]/div[1]/h2').getall()

        # locate the list of scientists based on start and end
        header_to_be_removed_from = headers[-self.num_of_headers_to_ignore[url]]

        # as there is no scientists appearing in any h2 header, start from 0
        content = content[0: content.find(header_to_be_removed_from)]
        content = Selector(text=content)
        name_href_list = content.css('ul')

        # list of mathematical probabilist is special because of the box
        if url == 'https://en.wikipedia.org/wiki/List_of_mathematical_probabilists':
            # the third ul is what we need
            name_href_list = content.css('ul').getall()[2]

            name_href_list = Selector(text=name_href_list).css('li')
            urls = _get_urls_from_name_href_list(name_href_list, response)
            with open(self.url_file_name, 'a+', encoding='utf-8') as f:
                f.writelines(urls)
        else:
            name_href_list = name_href_list.css('li')
            urls = _get_urls_from_name_href_list(name_href_list, response)
            with open(self.url_file_name, 'a+', encoding='utf-8') as f:
                f.writelines(urls)


class WikiPhysicalSciURLSpider(scrapy.Spider):
    name = "wiki-phy-sci-url"
    start_urls = ['https://en.wikipedia.org/wiki/List_of_physicists']

    # Victor_Twersky - not included

    def __init__(self, url_file_name=None):
        super(WikiPhysicalSciURLSpider, self).__init__()
        if url_file_name is None:
            self.url_file_name = 'phy_sci_urls.txt'
        else:
            self.url_file_name = url_file_name

    def parse(self, response):
        classified_name_href_list = response.xpath('//*[@id="mw-content-text"]/div[1]/ul').getall()
        # the last one is external link - useless
        classified_name_href_list = classified_name_href_list[0:-1]
        urls = []
        for i, name_href_list in enumerate(classified_name_href_list):
            name_href_list = Selector(text=name_href_list).css('li')
            urls = urls + _get_urls_from_name_href_list(name_href_list, response)

        with open(self.url_file_name, 'a+', encoding='utf-8') as f:
            f.writelines(urls)
