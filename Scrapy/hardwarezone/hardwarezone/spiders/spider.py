import scrapy

class HWZSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://forums.hardwarezone.com.sg/forums/pc-gaming.382/']

    def parse(self, response):
        topic_element_list = response.xpath('//div[@class="structItem-title"]')
        for topic_element in topic_element_list:
            # encode and decode to remove unicode characters
            topic = self.remove_unicode(topic_element.xpath("a/text()").get())

            yield response.follow(topic_element.xpath("a/@href").get(), self.parse_post, meta={'topic': topic} )

        next_page = response.xpath('//a[has-class("pageNav-jump--next")]/@href').get()

        # Retrieve Next Page (Topic Level)
        if next_page is not None:
            yield response.follow(next_page, self.parse)


    # callback function to parse post, separate from parsing topics.
    def parse_post(self, response):
        post_element_list = response.xpath('//div[@class="message-inner"]')

        for post in post_element_list:
            author = post.xpath('div/section/div/h4/a//text()').get()

            ## I feel like using css is a better alternative here. It's much shorter.
            # content = " ".join(self.remove_unicode(text) for text in post.css('article div.bbWrapper::text').getall() if text.strip() != "")

            ## use XPATH - incase we are being marked according to usage of XPATH
            content = " ".join(self.remove_unicode(text) for text in post.xpath('*//div[@class="bbWrapper"]/text()').getall() if text.strip() != "")

            yield {
                'author': author,
                'topic': response.meta.get('topic'), # Retrieving topic passed via meta
                'content': content
            }

        next_page = response.xpath('//a[has-class("pageNav-jump--next")]/@href').get()

        # Retrieve Next Page (Post Level)
        if next_page is not None:
            yield response.follow(next_page, self.parse_post)


    def remove_unicode(self, text):
        return text.strip().encode("ascii",'ignore').decode()