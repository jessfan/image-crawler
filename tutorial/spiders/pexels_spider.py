import re

import scrapy
from scrapy.linkextractor import LinkExtractor
from scrapy.selector import Selector

from ..DBUtil import DBUtil

class PexelsScraper(scrapy.Spider):
    name = "pexels"
    start_urls = ["https://www.pexels.com/"]
    base_url = "https://www.pexels.com/"

    # Only follow links that have this prefix
    url_matcher = re.compile('https://www.pexels.com/photo/')

    db_util = DBUtil()

    # Regex matchers for all fields for an image
    src_extractor = re.compile('src="([^"]*)"')
    tags_extractor = re.compile('alt="([^"]*)"')

    def start_requests(self):
        url = "https://www.pexels.com/"
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        if response.status == 200:
            body = Selector(text=response.body)
            images = body.css('img.image-section__image').extract()
            for image in images:
                img_url = PexelsScraper.src_extractor.findall(image)[0]
                tags = [tag.replace(',', '') for tag in PexelsScraper.tags_extractor.findall(image)[0].split(' ')]
                PexelsScraper.db_util.create_index(self.get_image_id(response.url),
                                                   1,
                                                   img_url,
                                                   response.url,
                                                   tags)
                print tags

            link_extractor = LinkExtractor(allow=PexelsScraper.url_matcher)
            next_links = filter(self.check_if_extracted,
                                map(lambda x: x.url, link_extractor.extract_links(response)))
            for link in next_links:
                yield scrapy.Request(link, self.parse)

    """
    Checks the database for the given url, if the image has already been extracted.
    Works based off of id for this particular website. 
    """
    def check_if_extracted(self, img_url):
        # Image urls are of type: https://www.pexels.com/photo/asphalt-blur-clouds-dawn-392010/
        # img_id = img_url.split('/')[-2].split('-')[-1]
        return True

    def get_image_id(self, url):
        return url.split('/')[-2].split('-')[-1]

