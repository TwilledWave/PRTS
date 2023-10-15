from pathlib import Path
import scrapy, pathlib, os

class QuotesSpider(scrapy.Spider):
    name = "prts"

    start_urls = [
        "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88",
        #pathlib.Path(os.path.abspath('prts.html')).as_uri(),
    ]

    def parse(self, response):
        for this in response.css("td.navbox-list.navbox-odd a"):
            yield{
                #"source": response.urljoin(this.css("a::attr(href)").get()+"&action==edit"),
                "source": "https://prts.wiki/index.php?title="+this.css("a::attr(href)").get()[3:]+"&action=edit",
                "indexed": False,
                "stage": this.css("a::text").get(),
            }