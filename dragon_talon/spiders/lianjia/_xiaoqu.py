from typing import Optional

import scrapy

from ... import items


class XiaoquSpider(scrapy.Spider):
    name = "xiaoqu"
    allowed_domains = ["lianjia.com"]
    _CITY_SET = {
        "bj",  # beijing
        "sh",  # shanghai
        "sz",  # shenzhen
    }
    _DISTRICT_BLACKLIST = {
        "chongming",
        "shanghaizhoubian"
    }

    def __init__(self, city: str = "sh", *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert city in self._CITY_SET, f"city should be in [self._CITY_SET]"
        self._url = f"https://{city}.lianjia.com/xiaoqu/"

    def start_requests(self):
        yield scrapy.Request(url=self._url, callback=self._parse_xiaoqu_home)

    def _parse_xiaoqu_home(self, response: scrapy.http.HtmlResponse):
        districts = response.xpath("//div[@data-role='ershoufang']/div[1]/a")
        # TODO: test
        districts = districts[:1]
        yield from response.follow_all(districts, callback=self._parse_disctrict)

    def _parse_disctrict(self, response: scrapy.http.HtmlResponse):
        areas = response.xpath("//div[@data-role='ershoufang']/div[2]/a")
        # TODO:
        areas = areas[:1]
        yield from response.follow_all(areas, callback=self._parse_area)


    def _parse_area(self, response: scrapy.http.HtmlResponse):
        xiaoqu_nodes = response.xpath("//li[@class='clear xiaoquListItem']")
        for xiaoqu_node in xiaoqu_nodes:
            xiaoqu_id: Optional[str] = xiaoqu_node.xpath("@data-id").get()
            if xiaoqu_id is None:
                continue
            try:
                info_node = xiaoqu_node.xpath("div[@class='info']")[0]
            except IndexError:
                continue
            name = info_node.xpath("div[@class='title']/a/text()").get()
            yield items.XiaoquItem(xiaoqu_id, name)
            break
        #     if info_node is None:
        #         continue
        #     name = info_node.xpath("div[@class='title']/a/text()").get()
        #     if name is None:
        #         continue
        #     print(xiaoqu_id, name)
            # yield items.XiaoquItem(name=node.xpath["div[@class='info']/div[@class='title']/"])
        # TODO: following links
