from pathlib import Path

import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    start_urls = [
        "https://arknights.fandom.com/wiki/Category:Stories",
        "https://arknights.fandom.com/wiki/Category:Stories?from=GA-2%2FStory",
    ]

    def parse(self, response):
        yield {
            "stage": response.css("span.subpages a::attr(title)").get(),
            "episode": response.css("div.page-header__categories a::text").getall()[-1],
            "characters": response.css("div.floatnone a::attr(title)").getall(),
            "source": response.url,
            "indexed": False,
        }

        for next_page in response.css("a.category-page__member-link::attr(href)").getall():
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)    