import os
import sqlite3

from w3lib.html import remove_tags
from itemadapter import ItemAdapter
from scrapy.selector import Selector
from scrapy.exceptions import DropItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class RemoveHeadAndTailPipeline:
    def __init__(self):
        # no info box
        super(RemoveHeadAndTailPipeline, self).__init__()
        self.log_urls_no_content_path = 'log'
        self.log_urls_no_content_name = 'log_urls_with_no_content.txt'
        self.log_urls_no_content = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        """
        Open file that records dropped items
        :param spider: the bio-spider
        :return: None
        """

        no_content_file_path_name = os.path.join(self.log_urls_no_content_path, self.log_urls_no_content_name)
        self.log_urls_no_content = open(no_content_file_path_name, 'w', encoding='utf-8')

    def process_item(self, item, spider):
        content = item['content']

        info_card = content.css('table.infobox.biography.vcard').get()

        # if info card comes after the short bio
        if info_card is not None:
            # try to remove all after info box
            temp_content = self.remove_all_after(content, info_card)

            # if there is a paragraph before info box, then info card comes after the short bio
            tentative_paragraphs = temp_content.css('p').getall()
            if len(tentative_paragraphs) != 0:
                short_description = self.generate_paragraph(temp_content)
                # if the description is not empty
                if len(short_description) != 0:
                    item['content'] = short_description
                    return item
            else:
                # otherwise the info card must be removed as a header
                content = self.remove_all_before_inclusive(content, info_card)

        table_of_content = content.css('div.toclimit-4').get()

        # remove detailed info
        if table_of_content is not None:
            # if there is a table of content
            content = self.remove_all_after(content, table_of_content)
        else:
            # otherwise, see if there is a header at level 2
            header_level_two = content.css('h2').get()
            if header_level_two is not None:
                # if there is a header at level 2, remove all after the header
                content = self.remove_all_after(content, header_level_two)

        short_description = self.generate_paragraph(content)

        if len(short_description) == 0:
            self.log_urls_no_content.write('https://en.wikipedia.org/wiki/' + item['name'] + '\n')
            raise DropItem('Wiki page of {} does not have content'.format(item['name']))

        item['content'] = short_description

        return item

    def remove_all_after(self, content, locator):
        content_str = content.get()

        ind_of_locator = content_str.find(locator)
        content_str = content_str[0: ind_of_locator]
        content = Selector(text=content_str)

        return content

    def remove_all_before_inclusive(self, content, locator):
        content_str = content.get()

        ind_of_start = content_str.find(locator) + len(locator)
        content_str = content_str[ind_of_start:]
        content = Selector(text=content_str)

        return content

    def remove_exact_locator(self, content, locator):
        content_str = content.get()

        content_str = content_str.replace(locator, '')
        content = Selector(text=content_str)

        return content

    def generate_paragraph(self, content):
        # generate paragraphs of the short bio
        paragraphs = content.css('p').getall()
        for i, p in enumerate(paragraphs):
            paragraphs[i] = remove_tags(p)

        # concatenate strings in the paragraphs list
        short_description = ''.join(p for p in paragraphs)
        short_description = short_description.strip()

        return short_description

    def close_spider(self, spider):
        """
        close the file
        :param spider: bio spider
        :return: None
        """
        self.log_urls_no_content.close()


class StoreInSQLitePipeline:
    collection_name = 'scrapy_items'

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.table_name = None

    def open_spider(self, spider):
        """
        Set up the connection to the database
        :param spider: spider
        :return: None
        """
        try:
            self.connection = sqlite3.connect('..\\database\\name_vs_bio.db')
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print('Connection to database fails')
            raise e
        if spider.debug:
            self.table_name = 'test'
        else:
            sci_type = spider.scientist_type
            self.table_name = 'mathematicians' if sci_type == 'math' else 'physical_sci'

        self.cursor.execute('CREATE TABLE IF NOT EXISTS mathematicians (\
                                    name VARCHAR(128), \
                                    discription VARCHAR(2048),\
                                    primary key (name)\
                                    )')

        self.cursor.execute('CREATE TABLE IF NOT EXISTS physical_sci (\
                            name VARCHAR(128), \
                            discription VARCHAR(2048),\
                            primary key (name)\
                            )')

        self.cursor.execute('CREATE TABLE IF NOT EXISTS test (\
                            name VARCHAR(128), \
                            discription VARCHAR(2048),\
                            primary key (name)\
                            )')

        self.connection.commit()

    def process_item(self, item, spider):
        """
        Insert (name, content) pair into the database
        :param item: a dict containing one (name, content) pair
        :param spider: bio spider
        :return: the item
        """
        # insert into table
        insert_command = 'INSERT INTO {} VALUES (?, ?) '.format(self.table_name)
        try:
            self.cursor.execute(insert_command, (item['name'],  item['content']))
        except sqlite3.Error as e:
            print('Insertion failed for {} '.format(item['name']))
            raise e

        return item

    def close_spider(self, spider):
        """
        Determine whether to commit changes to the database and close the connection
        :param spider: the bio spider
        :return: None
        """
        self.connection.commit()
        self.connection.close()
