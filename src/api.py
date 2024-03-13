import requests
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime as DateTime
from parser_data import ParserPlazaVea
from utils import CreateCSV, ColorPrint, Color
import time
import pandas as pd
import os
WEB_URL = 'https://www.plazavea.com.pe'


class ScrapperOfApi:
    def __init__(self, url=WEB_URL, parser=ParserPlazaVea(), headers_csv=None, csv_name='./data.csv', tree_depth=3, threads=5):
        self.threads = threads
        self.url = url
        self.tree_depth = tree_depth
        self.timeout = 60
        self.csv_name = csv_name
        self.session = requests.Session()
        self.page_size = 50
        self.csv = CreateCSV(filename=csv_name, headers=headers_csv)
        self.parser = parser
        self.logger = ColorPrint()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.start_time = DateTime.now()
        self.try_get_page()

    def try_get_page(self):
        url = f'{self.url}/api/catalog_system/pub/category/tree/3'
        response = self.session.get(url, timeout=self.timeout)
        response_json = response.json()
        # return self.remove_duplicates()÷
        futures = []
        for section in response_json:
            if self.tree_depth == 2:
                category_id = f'C:/{section["id"]}/'
                category_path = [section['name']]
                futures.append(self.executor.submit(self.get_products_by_category, category_id, category_path))
            elif len(section['children']) > 0 and self.tree_depth >= 3:
                for category in section['children']:
                    if len(category['children'])>0:
                        for subcategory in category['children']:
                            category_id = f'C:/{section["id"]}/{category["id"]}/{subcategory["id"]}/'
                            category_path = [section['name'], category['name'], subcategory['name']]
                            
                            futures.append(self.executor.submit(self.get_products_by_category, category_id, category_path))
                    elif self.tree_depth >= 2:
                        category_id = f'C:/{section["id"]}/{category["id"]}/'
                        category_path = [section['name'], category['name']]
                        futures.append(self.executor.submit(self.get_products_by_category, category_id, category_path))

        for future in as_completed(futures):


            # try:
            #     result = future.result()
            #     print(result)
            # except Exception as e:
            #     print(f'Error: {e}', file=sys.stderr)
            pass
        self.executor.shutdown(wait=True)
        # get the csv file and remove all duplicated data
        self.remove_duplicates()
        self.end_time = DateTime.now()
        self.logger.print(f'Elapsed time: {self.end_time - self.start_time}', ColorPrint.color.GREEN)

    def remove_duplicates(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
    # Construye el path absoluto combinando el directorio del script con el path relativo
        absolute_path = os.path.join(script_directory, self.csv_name)
        # Devuelve el path absoluto
        directory_csv = os.path.abspath(absolute_path)
        print(directory_csv,absolute_path)
        cvs = pd.read_csv(directory_csv, delimiter=',', error_bad_lines=False, encoding='utf-8')
        cvs.drop_duplicates(subset=['Descripción'], keep='first', inplace=True)

        cvs.to_csv(directory_csv, index=False)
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

    def api_get_products_by_page(self, category, page, retries=0):
        params = {
            "fq": category,
            "_from": (page - 1) * self.page_size,
            "_to": page * self.page_size - 1,
        }

        url = f'{self.url}/api/catalog_system/pub/products/search/'
        complete_url = f'Page {page}: {url}?fq={category}&_from={(page - 1) * self.page_size}&_to={page * self.page_size - 1}'

        if retries:
            complete_url += f' - {retries} retries'
            self.logger.print(f'Retrying {complete_url}', ColorPrint.color.RED)
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            return response
        except Exception as e:
            # Error: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer'))

            self.logger.print(f'Error getting products from category {category} page coneection aborted{page} =>{complete_url}', ColorPrint.color.RED)
            self.logger.print(f'Error: {e} RETRYING in 5 seconds', ColorPrint.color.RED)
            
            retries += 1
            time.sleep(3)

            return self.api_get_products_by_page(category, page, retries=retries)

    def fetch_products(self, category, page):
        self.logger.print(f'Fetching products from category {category} page {page}', ColorPrint.color.GREEN)
        resp = self.api_get_products_by_page(category, page)
        json = resp.json()
        if resp is None or resp.status_code not in (200, 206):
            return None, page
        if json is None or len(json) == 0:
            return None, page
        return json, page

    def process_product_data(self, product_data, category_path):
        for product in product_data:
            product['category_path'] = category_path
            self.save_to_excel(product)

    def save_to_excel(self, product):
        product_parsed = self.parser.parse(product)
        self.csv.write(product_parsed)

# Assuming utils.CreateCSV, utils.ColorPrint, utils.Color, and parser_data
