import requests
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime as DateTime
from parser_data import ParserPlazaVea
from utils import CreateCSV, ColorPrint, Color

WEB_URL = 'https://www.plazavea.com.pe'


class ScrapperOfApi:
    def __init__(self, url=WEB_URL, parser=ParserPlazaVea(), headers_csv=None, csv_name='./data.csv', tree_depth=3, threads=5):
        self.threads = threads
        self.url = url
        self.tree_depth = tree_depth
        self.timeout = 30
        self.session = requests.Session()
        self.page_size = 50
        self.csv = CreateCSV(filename=csv_name, headers=headers_csv)
        self.parser = parser
        self.logger = ColorPrint()
        self.executor = ThreadPoolExecutor(max_workers=self.threads)
        self.start_time = DateTime.now()
        self.try_get_page()

    def try_get_page(self):
        url = f'{self.url}/api/catalog_system/pub/category/tree/3'
        self.logger.print(f'Getting categories from {url}', ColorPrint.color.RED)
        response = self.session.get(url, timeout=self.timeout)
        response_json = response.json()

        futures = []
        for section in response_json:
            if len(section['children']) == 0 and self.tree_depth == 2:
                category_id = f'C:/{section["id"]}/'
                category_path = [section['name']]
                futures.append(self.executor.submit(self.get_products_by_category, category_id, category_path))
            elif section['hasChildren']:
                for category in section['children']:
                    if self.tree_depth >= 2:
                        category_id = f'C:/{section["id"]}/{category["id"]}/'
                        category_path = [section['name'], category['name']]
                        futures.append(self.executor.submit(self.get_products_by_category, category_id, category_path))
                    if category['hasChildren']:
                        for subcategory in category['children']:
                            category_id = f'C:/{section["id"]}/{category["id"]}/{subcategory["id"]}/'
                            category_path = [section['name'], category['name'], subcategory['name']]
                            futures.append(self.executor.submit(self.get_products_by_category, category_id, category_path))

        for future in as_completed(futures):

            # try:
            #     result = future.result()
            #     print(result)
            # except Exception as e:
            #     print(f'Error: {e}', file=sys.stderr)
            pass

        self.end_time = DateTime.now()
        self.logger.print(f'Elapsed time: {self.end_time - self.start_time}', ColorPrint.color.GREEN)

    def get_products_by_category(self, category, category_path):
        current_page = 1
        more_pages = True
        while more_pages:
            futures = []
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                for page in range(current_page, current_page + self.threads):
                    futures.append(executor.submit(self.fetch_products, category, page))
                for future in as_completed(futures):
                    product_data, page = future.result()
                    if product_data:
                        self.process_product_data(product_data, category_path)
                    else:
                        more_pages = False
                current_page += self.threads

    def api_get_products_by_page(self, category, page):
        params = {
            "fq": category,
            "_from": (page - 1) * self.page_size,
            "_to": page * self.page_size - 1,
        }
        # self.logger.print(f'Getting products from category {category} page {page}', ColorPrint.color.VIOLET)
        return self.session.get(f'{self.url}/api/catalog_system/pub/products/search/', params=params, timeout=self.timeout)

    def fetch_products(self, category, page):
        resp = self.api_get_products_by_page(category, page)
        if resp is None or resp.status_code not in (200, 206):
            # self.logger.print(f'Error getting page {page} of category {category}', ColorPrint.color.RED)
            return None, page
        return resp.json(), page

    def process_product_data(self, product_data, category_path):
        for product in product_data:
            product['category_path'] = category_path
            self.save_to_excel(product)

    def save_to_excel(self, product):
        self.csv.write(self.parser.parse(product))

# Assuming utils.CreateCSV, utils.ColorPrint, utils.Color, and parser_data
