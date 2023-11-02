from pathlib import Path
import scrapy, pathlib, os

class QuotesSpider(scrapy.Spider):
    name = "prts"

    start_urls = [
        #"https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88",
        "https://prts.wiki/w/SW-ST1_%E6%97%A0%E5%90%8D%E6%B0%8F%E7%9A%84%E6%88%98%E4%BA%89/NBT",
        #pathlib.Path(os.path.abspath('prts.html')).as_uri(),
    ]

    def parse(self, response):
        for this in response.css("td.navbox-list.navbox-odd a"):
            if not(this.css("a::attr(href)").get() is None):
                yield{
                    #"source": response.urljoin(this.css("a::attr(href)").get()+"&action==edit"),
                    "source": "https://prts.wiki/index.php?title="+this.css("a::attr(href)").get()[3:]+"&action=edit",
                    "indexed": False,
                    "stage": this.css("a::text").get(),
                }