import scrapy

class HWZSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://forums.hardwarezone.com.sg/forums/pc-gaming.382/']

    def parse(self, response):
        topic_element_list = response.xpath('//div[@class="structItem-title"]')
        for topic_element in topic_element_list:
            yield response.follow(topic_element.xpath("a/@href").get(), self.parse)


        post_element_list = response.xpath('//div[@class="message-inner"]')
        topic = response.xpath('//h1[@class="p-title-value"]/text()').get().strip()
        for post in post_element_list:
            author = post.xpath('div/section/div/h4/a//text()').get()
            postNumber = post.xpath('*//ul[has-class("message-attribution-opposite")]/li[2]/a/text()').get().strip()
            postDate = post.xpath('*//li[@class="u-concealed"]/a/time/@datetime').get()

            content = " ".join(text.strip() for text in post.xpath('*//div[@class="bbWrapper"]/text()').getall() if text.strip() != "")
            if content == "":
                # The post has no text, try finding image posts instead
                content = " ".join(post.xpath('*//div[@class="bbWrapper"]/div/img/@src').getall())

            yield {
                'topic': topic, # Retrieving topic passed via meta
                'author': author,
                'postNumber': postNumber,
                'date': postDate,
                'content': content,
                'url': response.url
            }

        next_page = response.xpath('//a[has-class("pageNav-jump--next")]/@href').get()

        # Retrieve Next Page (Topic Level)
        if next_page is not None:
            yield response.follow(next_page, self.parse)