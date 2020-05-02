# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CodeforcesSubmissionItem(scrapy.Item):
    submission_id = scrapy.Field()
    submission_lang = scrapy.Field()
    submission_verdict = scrapy.Field()
    source_code = scrapy.Field()
    pass


class CodeforcesTestcaseItem(scrapy.Item):
    contest_id = scrapy.Field()
    problem = scrapy.Field()
    inputs = scrapy.Field()
    outputs = scrapy.Field()
    pass
