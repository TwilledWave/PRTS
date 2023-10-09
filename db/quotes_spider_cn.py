from pathlib import Path

import scrapy

class QuotesSpider(scrapy.Spider):
    name = "prts"

    start_urls = [
        "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88",
    ]

    def parse(self, response):
        for this in response.css("td.navbox-list.navbox-odd"):
            yield{
                "source": response.urljoin(this.css("a::attr(href)").get()+"&action==edit"),
                "indexed": False,
                "stage": this.css("a::text").get(),
            }