from pathlib import Path

import scrapy


class QuotesSpider(scrapy.Spider):
    name = "chars"

    start_urls = [
        "https://arknights.fandom.com/wiki/Category:6-star",
        "https://arknights.fandom.com/wiki/Category:5-star",
        "https://arknights.fandom.com/wiki/Category:4-star",
        "https://arknights.fandom.com/wiki/Category:3-star",
        "https://arknights.fandom.com/wiki/Category:2-star",
        "https://arknights.fandom.com/wiki/Category:1-star",
    ]

    def parse(self, response):
        yield {
            "nameEN": response.css("span.mw-page-title-main::text").get(),
            "nameCN": response.css("div.pi-item.pi-data.pi-item-spacing.pi-border-color[data-source=cnname] div::text").get(),
            "nameJP": response.css("div.pi-item.pi-data.pi-item-spacing.pi-border-color[data-source=jpname] div::text").get(),
            "source": response.url+'/Story',
            "indexed": False,
        }

        for next_page in response.css("a.category-page__member-link::attr(href)").getall():
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)    

