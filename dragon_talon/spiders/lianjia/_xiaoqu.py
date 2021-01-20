import re
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
                pos_info = info_node.xpath("div[@class='positionInfo']")[0]
            except IndexError:
                continue
            name = info_node.xpath("div[@class='title']/a/text()").get()
            district = pos_info.xpath("a[@class='district']/text()").get()
            area = pos_info.xpath("a[@class='bizcircle']/text()").get()
            pos_info_txt = pos_info.get()
            matched = re.search(r"(\d+)年建成", pos_info_txt)
            built_year = matched.group(1) if matched else None
            tags = info_node.xpath("div[@class='tagList']/span/text()").getall()
            yield items.XiaoquItem(xiaoqu_id, name, district, area, built_year, tags)
            houseinfo_nodes = info_node.xpath("div[@class='houseInfo']/a")
            for_rent = 0
            deal_in_90days= 0
            for houseinfo_node in houseinfo_nodes:
                title = houseinfo_node.xpath("@title").get()
                if title.endswith("网签"):
                    matched = re.match(r"90天成交(\d+)", houseinfo_node.xpath("text()").get())
                    deal_in_90days = matched.group(1) if matched else None
                elif title.endswith("租房"):
                    matched = re.match(r"(\d+)套正在出租", houseinfo_node.xpath("text()").get())
                    for_rent = matched.group(1) if matched else None
            yield items.XiaoQuDailyStats(xiaoqu_id, name, for_rent, deal_in_90days)
            break
        #     if info_node is None:
        #         continue
        #     name = info_node.xpath("div[@class='title']/a/text()").get()
        #     if name is None:
        #         continue
        #     print(xiaoqu_id, name)
            # yield items.XiaoquItem(name=node.xpath["div[@class='info']/div[@class='title']/"])
        # TODO: following links
