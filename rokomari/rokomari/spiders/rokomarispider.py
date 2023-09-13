import scrapy
from urllib.parse import urlencode

class RokomariSpider(scrapy.Spider):
	name = "rokomarispider"
    # allowed_domains = ["www.rokomari.com"]
	start_urls = ["https://www.rokomari.com/book/category/3402/boimela-2023-novel?page=1"]

	def parse(self, response):
		books = response.css('div.book-list-wrapper')
		print(len(books))
		for book in books:
			yield {
			"name": book.css('h4.book-title::text').get(),
			"author": book.css('p.book-author::text').get(),
			"price": book.css('strike::text').get() if book.css('strike::text').get() else '',
			"discount_price": book.css('p.book-price').get().split("TK")[2].split(" ")[1] if (len(book.css('p.book-price').get().split("TK")) == 3) else '',
			"review": book.css('span.text-secondary::text').get().split('(')[1].split(')')[0] if book.css('span.text-secondary::text').get() else '',
			"url": "https://www.rokomari.com" + book.css('div.book-list-wrapper a::attr(href)').get()
		}
		if response.css('div.pagination a:last-child').get():
			next_page_url = "https://www.rokomari.com" + response.css('div.pagination a:last-child').get().split('"')[1]
			yield response.follow(next_page_url, callback=self.parse)

# rokomary splider run command: scrapy crawl rokomarispider -O book.json