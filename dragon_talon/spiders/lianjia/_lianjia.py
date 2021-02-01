import json
import re
import urllib
from datetime import datetime, timezone
from typing import Optional

import scrapy

from ... import items


class LianjiaSpider(scrapy.Spider):
    name = "lianjia"
    allowed_domains = ["lianjia.com"]
    _SEARCH_CONDITION = "su1y4bp5ep10000"  # built in 20 years; price>50k
    _CITY_SET = {
        "bj",  # beijing
        "sh",  # shanghai
        "sz",  # shenzhen
    }
    _DISTRICT_BLACKLIST = {
        "chongming",
        "shanghaizhoubian",
        "jinshan",
        "fengxian",
        "qingpu",
    }

    def __init__(self, city: str = "sh", *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert city in self._CITY_SET, f"city should be in [self._CITY_SET]"
        self._base_url = f"https://{city}.lianjia.com"
        self._start_url = f"https://{city}.lianjia.com/xiaoqu/{self._SEARCH_CONDITION}"

    def start_requests(self):
        yield scrapy.Request(url=self._start_url, callback=self._parse_home)

    def _parse_home(self, response: scrapy.http.HtmlResponse):
        districts = response.xpath("//div[@data-role='ershoufang']/div[1]/a")
        # TODO:
        districts = districts[:1]
        pattern = re.compile(r"\/xiaoqu\/(\w+)\/su1.+")
        districts2fo = []
        for dist in districts:
            follow_path = dist.xpath("@href").get()
            m = pattern.match(follow_path)
            if m:
                district_str = m.group(1)
                if district_str not in self._DISTRICT_BLACKLIST:
                    districts2fo.append(dist)
            else:
                continue

        yield from response.follow_all(districts2fo, callback=self._parse_disctrict_first_page)

    def _parse_disctrict_first_page(self, response: scrapy.http.HtmlResponse):
        yield from self._parse_district_page(response)
        page_box_node = response.xpath("//div[@class='page-box house-lst-page-box']")
        page_path_fmt_str = page_box_node.xpath("@page-url").get()
        page_data = page_box_node.xpath("@page-data").get()
        page_data = json.loads(page_data)
        total_page = page_data["totalPage"]
        for page in range(2, total_page + 1):
            page_path = page_path_fmt_str.format(page=page)
            page_url = urllib.parse.urljoin(self._base_url, page_path)
            yield scrapy.Request(url=page_url, callback=self._parse_district_page)

    def _parse_district_page(self, response: scrapy.http.HtmlResponse):
        xiaoqu_nodes = response.xpath("//li[@class='clear xiaoquListItem']")
        # TODO:
        xiaoqu_nodes = xiaoqu_nodes[:1]
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
            built_matched = re.search(r"(\d+)年建成", pos_info_txt)
            built_year = built_matched.group(1) if built_matched else None
            tags = info_node.xpath("div[@class='tagList']/span/text()").getall()
            cb_kwargs = {
                "xiaoqu_id": xiaoqu_id,
                "name": name,
                "district": district,
                "area": area,
                "built_year": int(built_year),
                "tags": tags,
            }
            xiaoqu_daily_stats = self.__parse_xiaoqu_daily_stats(info_node, xiaoqu_id, name)
            if xiaoqu_daily_stats:
                yield xiaoqu_daily_stats
            yield response.follow(
                xiaoqu_node.xpath("a/@href").get(), callback=self._parse_xiaoqu, cb_kwargs=cb_kwargs
            )

    def __parse_xiaoqu_daily_stats(
        self, xiaoqu_node, xiaoqu_id: str, xiaoqu_name: str
    ) -> Optional[items.XiaoquDailyStats]:
        houseinfo_nodes = xiaoqu_node.xpath("div[@class='houseInfo']/a")
        for_rent = 0
        deal_in_90days = 0
        for houseinfo_node in houseinfo_nodes:
            title = houseinfo_node.xpath("@title").get()
            if title.endswith("网签"):
                matched = re.match(r"90天成交(\d+)", houseinfo_node.xpath("text()").get())
                deal_in_90days = matched.group(1) if matched else None
            elif title.endswith("租房"):
                matched = re.match(r"(\d+)套正在出租", houseinfo_node.xpath("text()").get())
                for_rent = matched.group(1) if matched else None
        ask_avg_price = xiaoqu_node.xpath(
            "//div[@class='xiaoquListItemPrice']/div[@class='totalPrice']/span/text()"
        ).get()
        on_sale_count = xiaoqu_node.xpath("//a[@class='totalSellCount']/span/text()").get()
        try:
            return items.XiaoquDailyStats(
                datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
                ),
                xiaoqu_id,
                xiaoqu_name,
                int(for_rent),
                int(on_sale_count),
                int(deal_in_90days),
                int(ask_avg_price),
            )
        except (TypeError, ValueError):
            return None

    __XIAOQU_LABEL_TO_FIELD_NAME = {
        "建筑类型": "building_type",
        "物业费用": "management_fee",
        "物业公司": "prop_manager",
        "开发商": "prop_developer",
        "楼栋总数": "num_of_buildings",
        "房屋总数": "num_of_units",
    }

    def __fill_label_content(self, xiaoqu_label: str, xiaoqu_content: str, item_kwargs: dict):
        field_name = self.__XIAOQU_LABEL_TO_FIELD_NAME.get(xiaoqu_label)
        if field_name is None:
            return
        if field_name == "num_of_buildings" or field_name == "num_of_units":
            num_matched = re.match(r"(\d+).*", xiaoqu_content)
            item_kwargs[field_name] = int(num_matched.group(1))
        else:
            item_kwargs[field_name] = xiaoqu_content

    def _parse_xiaoqu(self, response: scrapy.http.HtmlResponse, **kwargs):
        xiaoqu_info_items = response.xpath("//div[@class='xiaoquInfoItem']")
        for info_item in xiaoqu_info_items:
            info_label = info_item.xpath("span[@class='xiaoquInfoLabel']/text()").get()
            if info_label == "附近门店":
                xiaoqu_latitude = info_item.xpath(
                    "span[@class='xiaoquInfoContent']/span/@xiaoqu"
                ).get()
                north_latitude, east_latitude = json.loads(xiaoqu_latitude)
                kwargs["north_latitude"] = north_latitude
                kwargs["east_latitude"] = east_latitude
            else:
                info_content = info_item.xpath("span[@class='xiaoquInfoContent']/text()").get()
                self.__fill_label_content(info_label, info_content, kwargs)
        yield items.XiaoquInfo(**kwargs)
        xiaoqu_info = {"xiaoqu_id": kwargs["xiaoqu_id"], "xiaoqu_name": kwargs["name"]}
        chengjiao_url = response.xpath("//div[@id='frameDeal']/a/@href").get()
        if chengjiao_url:
            yield response.follow(
                chengjiao_url,
                self._parse_chengjiao,
                cb_kwargs=xiaoqu_info,
            )
        # TODO:

    def _parse_chengjiao(self, response: scrapy.http.HtmlResponse, **kwargs):
        all_trans_nodes = response.xpath("//ul[@class='listContent']/li/div[@class='info']")
        for trans_node in all_trans_nodes:
            title = trans_node.xpath("div[@class='title']/a/text()").get()
            splitted_title = title.split()
            if len(splitted_title) < 3:
                continue
            # houseinfo =
            print(splitted_title)

    def _parse_ershoufang(self, response: scrapy.http.HtmlResponse, **kwargs):
        pass
