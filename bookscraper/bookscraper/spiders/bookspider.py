import scrapy
import random
from bookscraper.items import BookItem
from urllib.parse import urlencode


API_KEY = 'df079156-1232-41f4-994c-955c39aef4'

## End point proxy solution
def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)

    return proxy_url

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com", "proxy.scrapeops.io"]
    start_urls = ["https://books.toscrape.com"]

    # overwrite settings FEEDS
    custom_settings = {
        'FEEDS' : {
           'booksdata.json': {
                'format': 'json',
                'overwrite': True
            },
        }
    }

    ## very first url proxy add. Not mandatory. using it for Endpoint proxy solution: scrapeops
    # def start_requests(self):
    #     yield scrapy.Request(url=get_proxy_url(self.start_urls[0]), callback=self.parse)

    # if use scrapeops-scrapy-proxy-sdk, then

    # def start_requests(self):
    #     yield scrapy.Request(url=self.start_urls[0], callback=self.parse)

    # user_agent_list = [
    #     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    #     'Mozilla/4.0 (X11; Linux x86_64) AppleWebKit/588.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/588.36',
    #     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/599.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/599.36',
    #     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.30 (KHTML, like Milon) Chrome/115.0.0.0 Safari/599.36'
    # ]

    def parse(self, response):
        books = response.css('article.product_pod')

        for book in books:
            relative_url = book.css('h3 a ::attr(href)').get()

            if 'catalogue/' in relative_url:
                book_url = "https://books.toscrape.com/" + relative_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + relative_url

            # yield response.follow(book_url, callback=self.parse_book_page, headers={"User-Agent": self.user_agent_list[random.randint(0, len(user_agent_list)-1)]})
            # yield response.follow(book_url, callback=self.parse_book_page, meta={"proxy": "http://user-asdas3a4545:12345678@gate.smartproxy.com:7000"}) # For smart proxy
            # yield response.follow(url=get_proxy_url(book_url), callback=self.parse_book_page) # Endpoint proxy solution
            yield response.follow(book_url, callback=self.parse_book_page) # callback call back function will call the parse (it's self) when the current response get

        #     yield{
        #         'name': book.css('h3 a::text').get(),
        #         'price': book.css('.product_price .price_color::text').get(),
        #         'url': book.css('h3 a').attrib['href']
        #     }
        
        next_page = response.css('li.next a ::attr(href)').get()

        if next_page is not None:
            print("next_page: ", next_page)
            if 'catalogue/' in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page

            # yield response.follow(next_page_url, callback=self.parse, meta={"proxy": "http://user-asdas3a4545:12345678@gate.smartproxy.com:7000"}) # for smart proxy
            # yield response.follow(url=get_proxy_url(next_page_url), callback=self.parse) # Endpoint proxy solution
            yield response.follow(next_page_url, callback=self.parse) # callback call back function will call the parse (it's self) when the current response get
    
    def parse_book_page(self, response):
        table_rows = response.css("table tr")

        book_item = BookItem()

        book_item['url'] =  response.url
        book_item['title'] =  response.css('.product_main h1::text').get()
        book_item['upc'] =  table_rows[0].css('td ::text').get()
        book_item['product_type'] =  table_rows[1].css('td ::text').get()
        book_item['price_excl_tax'] =  table_rows[2].css('td ::text').get()
        book_item['price_incl_tax'] =  table_rows[3].css('td ::text').get()
        book_item['tax'] =  table_rows[4].css('td ::text').get()
        book_item['availability'] =  table_rows[5].css('td ::text').get()
        book_item['num_reviews'] =  table_rows[6].css('td ::text').get()
        book_item['stars'] =  response.css("p.star-rating").attrib['class']
        book_item['category'] =  response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item['description'] =  response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price'] = response.css('p.price_color ::text').get()

        yield book_item

        # yield {
        #     'url': response.url,
        #     'title': response.css('.product_main h1::text').get(),
        #     'product_type': table_rows[1].css('td ::text').get(),
        #     'price_excl_tax': table_rows[2].css('td ::text').get(),
        #     'price_incl_tax': table_rows[3].css('td ::text').get(),
        #     'tax': table_rows[4].css('td ::text').get(),
        #     'availability': table_rows[5].css('td ::text').get(),
        #     'num_reviews': table_rows[6].css('td ::text').get(),
        #     'stars': response.css("p.star-rating").attrib['class'],
        #     'category': response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        #     'description': response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
        #     'price': response.css('p.price_color ::text').get(),
        # }
