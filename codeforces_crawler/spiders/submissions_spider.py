# coding=utf-8
import scrapy
from scrapy_splash import SplashRequest
from codeforces_crawler.items import CodeforcesSubmissionItem

script = """
    function main(splash, args)
        splash.private_mode_enabled = false
        assert(splash:go(args.url))
        assert(splash:wait(2))
        assert(splash:runjs("$('.click-to-view-tests').click();"))
        assert(splash:wait(2))
        --splash.scroll_position = {x=0, y=400}
        return {
            html = splash:html(),
            --png = splash:png(),
  }
end
"""


class SubmissionsSpider(scrapy.Spider):
    name = "cf_submission"
    allowed_domains = ['codeforces.com']
    start_urls = ['https://codeforces.com/problemset/status/1082/problem/F']

    # Lựa chọn ngôn ngữ chương trình muốn get về
    wanted_languages = ['Java 8', 'Python 3', 'GNU C++11', 'Java 7', 'Java 6', 'Python 2']

    # Kiểm tra verdict mong muốn
    wanted_verdicts = ['RUNTIME_ERROR', 'OK']  # TIME_LIMIT_EXCEEDED

    # html_file = open("html_file", 'w')

    def parse(self, response):
        print("Processing: ", response.url)

        submission_id_list = response.xpath('//tr/@data-submission-id').extract()

        for submission_id in submission_id_list:

            submission_lang = response.xpath('//tr[@data-submission-id=%s]/td[5]/text()' % submission_id)[
                0].extract().strip()

            # Kiểm tra xem có nằm trong các ngôn ngữ mình mong muốn
            if submission_lang not in self.wanted_languages:
                continue

            submission_verdict = response.xpath(
                '//tr[@data-submission-id=%s]/td[6]/span/@submissionverdict' % submission_id)[0].extract().strip()
            if submission_verdict not in self.wanted_verdicts:
                continue

            code_link = 'https://codeforces.com' + (response.xpath('//tr[@data-submission-id=%s]/td[1]/a/@href'
                                                                   % submission_id)[0].extract().strip())
            print("====================================")
            print(code_link)
            item = CodeforcesSubmissionItem()
            item['submission_id'] = submission_id
            item['submission_lang'] = submission_lang
            item['submission_verdict'] = submission_verdict
            yield SplashRequest(url=code_link, callback=self.parse_sourcecode, meta={'item': item}, endpoint='execute',
                                args={'lua_source': script})

    # Next page code
    # Todo

    def parse_sourcecode(self, response):
        # self.html_file.write(response.body.decode("utf-8"))
        # close(html_file)
        source_code = response.xpath('//*[@id="program-source-text"]').extract()

        input_list = response.xpath('//div[@class="roundbox"]//pre[@class="input"]/text()').extract()
        inputs = {}
        for i in range(0, len(input_list)):
            inputs["input" + str(i).zfill(2)] = input_list[i]
            # print(input_list[i])

        output_list = response.xpath('//div[@class="roundbox"]//pre[@class="output"]/text()').extract()
        outputs = {}
        for j in range(0, len(output_list)):
            outputs["output" + str(j).zfill(2)] = output_list[j]
            # print(output_list[i])

        item = response.meta['item']
        item['source_code'] = source_code
        item['inputs'] = inputs
        item['outputs'] = outputs

        yield item
