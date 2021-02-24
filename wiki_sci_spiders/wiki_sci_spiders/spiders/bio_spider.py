import scrapy


class WikiScientistsBioSpider(scrapy.Spider):
    name = "wiki-sci-bio-spider"

    def __init__(self, **kwargs):
        """
        Initialize the bio spider that get the summary biography of each scientists
        :param kwargs:
            urls_file : the file containing names of the scientists
            debug : whether start debug mode
        """
        super(WikiScientistsBioSpider, self).__init__()
        self.urls = None
        if 'urls_file' not in kwargs.keys():
            raise ValueError('URL file not specified')
        urls_file = kwargs['urls_file']

        self.debug = False
        if 'debug' in kwargs.keys():
            self.debug = True if 'True' in kwargs['debug'] else False

        # Determine the type of scientists stored in the url file
        if 'math' in urls_file:
            self.scientist_type = 'math'
        elif 'phy' in urls_file:
            self.scientist_type = 'phy'
        else:
            raise TypeError('Unrecognized scientists type; must be Mathematicians or Physical Scientists')

        # whether to debug
        if not self.debug:
            with open(urls_file, 'r', encoding='utf-8') as f:
                self.urls = f.readlines()
        else:
            # if debug, select 3 types of wiki page
            self.urls = [
                'Eugene_Feenberg',
                'Albert_Einstein',
                'Ludwig_Zehnder'
            ]

        if self.urls is None:
            raise ValueError('URL file Not Valid')

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url='https://en.wikipedia.org/wiki/'+url, callback=self.parse)

    def parse(self, response):
        content = response.xpath('//*[@id="mw-content-text"]')
        name = response.url[len('https://en.wikipedia.org/wiki/'):]
        return {'content': content, 'name': name}
