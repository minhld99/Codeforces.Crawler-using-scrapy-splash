# coding=utf-8
import scrapy
import time
from scrapy_splash import SplashRequest
from codeforces_crawler.items import CodeforcesTestcaseItem

script = """
    function main(splash, args)
        splash.private_mode_enabled = false
        assert(splash:go(args.url))
        assert(splash:wait(1))
        assert(splash:runjs("$('.click-to-view-tests').click();"))
        assert(splash:wait(2))
        --splash.scroll_position = {x=0, y=400}
        return {
            html = splash:html(),
            --png = splash:png(),
        }
    end
"""


class TestcasesSpider(scrapy.Spider):
    name = "cf_testcase"
    allowed_domains = ['codeforces.com']
    urls = []
    start_urls = []

    contest_link = open('contest-info.csv', 'r')
    for row in contest_link:
        urls.append(row.split(',')[1])
    start_urls = urls[99:]

    # Choose your source_code language
    wanted_languages = ['GNU C11']  # 'Java 8', 'Python 3', 'GNU C++11', 'Java 7', 'Java 6', 'Python 2'

    # Choose your desired verdicts
    wanted_verdicts = ['OK']

    MAX = 50
    i = 1

    def start_requests(self):
        # start from second page, because the first is always update, sometimes it doesn't have a testcase
        yield scrapy.Request(url=self.start_urls[self.i-1]+'/page/2?order=BY_JUDGED_DESC', callback=self.parse)

    wanted_problem = {'A': 0, 'B': 0}

    current_url = urls[99]

    def parse(self, response):
        print("Processing: ", response.url)

        submission_id_list = response.xpath('//tr/@data-submission-id').extract()
        for submission_id in submission_id_list:
            submission_verdict = response.xpath('//tr[@data-submission-id=%s]/td[6]/span/@submissionverdict'
                                                % submission_id)[0].extract().strip()
            if submission_verdict not in self.wanted_verdicts:
                continue

            submission_problem = response.xpath('//tr[@data-submission-id=%s]/td[4]/a/text()'
                                                % submission_id)[0].extract().strip()

            if ('A' in submission_problem[0] and self.wanted_problem['A'] == 0) or ('B' in submission_problem[0] and self.wanted_problem['B'] == 0):
                self.wanted_problem[submission_problem[0]] = 1
                item = CodeforcesTestcaseItem()
                item['problem'] = submission_problem
                # print("===" + submission_problem[0] + "===" + submission_verdict + "===" + submission_id + "===")
                # print(wanted_problem)
                code_link = 'https://codeforces.com' + (response.xpath('//tr[@data-submission-id=%s]/td[1]/a/@href'
                                                                       % submission_id)[0].extract().strip())
                item['contest_id'] = code_link.split('/')[4]
                yield SplashRequest(url=code_link, callback=self.parse_testcase, meta={'item': item}, endpoint='execute',
                                    args={'lua_source': script})

            if self.wanted_problem['A'] == 1 and self.wanted_problem['B'] == 1:
                break

        # generate next-page url
        if self.wanted_problem['A'] == 0 or self.wanted_problem['B'] == 0:
            if response.selector.xpath('//span[@class="inactive"]/text()').extract():
                # '\u2192' is the unicode of 'right arrow' symbol
                if response.selector.xpath('//span[@class="inactive"]/text()')[0].extract() != u'\u2192':
                    next_page_href = \
                    response.selector.xpath('//div[@class="pagination"]/ul/li/a[@class="arrow"]/@href')[0]
                    next_page_url = response.urljoin(next_page_href.extract())
                    yield scrapy.Request(next_page_url, callback=self.parse)
            else:
                next_page_href = \
                response.selector.xpath('//div[@class="pagination"]/ul/li/a[@class="arrow"]/@href')[1]
                next_page_url = response.urljoin(next_page_href.extract())
                yield scrapy.Request(next_page_url, callback=self.parse)

        time.sleep(0.5)
        if self.wanted_problem['A'] == 1 and self.wanted_problem['B'] == 1 and self.i < self.MAX:
            self.i += 1
            self.wanted_problem = {'A': 0, 'B': 0}
            # proceed to next link
            yield scrapy.Request(url=self.start_urls[self.i-1]+'/page/2?order=BY_JUDGED_DESC', callback=self.parse)

    def parse_testcase(self, response):
        input_list = response.xpath('//div[@class="roundbox"]//pre[@class="input"]/text()').extract()
        inputs = {}
        for i in range(0, len(input_list)):
            inputs["input" + str(i).zfill(2)] = input_list[i]
            # print(input_list[i])

        output_list = response.xpath('//div[@class="roundbox"]//pre[@class="answer"]/text()').extract()
        outputs = {}
        for j in range(0, len(output_list)):
            outputs["output" + str(j).zfill(2)] = output_list[j]
            # print(output_list[j])

        item = response.meta['item']
        item['inputs'] = inputs
        item['outputs'] = outputs
        yield item
