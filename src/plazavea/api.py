import requests
import sys
from utils import CreateCSV, ColorPrint, Color
import concurrent.futures
from parser_data import ParserPlazaVea
from datetime import datetime as DateTime
from queue import Queue, Empty
import threading

WEB_URL = 'https://www.plazavea.com.pe'

class ScrapperOfApi:
    def __init__(self, url=WEB_URL, parser=ParserPlazaVea(), headers_csv=None, csv_name='./data.csv', tree_depth=3, threads=5):
        self.url = url
        self.tree_depth = tree_depth
        self.threads = threads
        self.timeout = 30
        self.session = requests.Session()
        self.page_size = 50
        self.csv = CreateCSV(filename=csv_name, headers=headers_csv)
        self.parser = parser
        self.logger = ColorPrint()
        self.task_queue = Queue()
        self.start_time = DateTime.now()
        self.end_time = None
        self.workers = []
        # self.init_workers()
        # self.try_get_page()

    def init_workers(self):
        for _ in range(self.threads):
            worker = threading.Thread(target=self.task_processor)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def task_processor(self):
        while True:
            try:
                task = self.task_queue.get(timeout=3)  # Adjust timeout as needed
                if task is None:
                    break  # None is a signal to stop the worker
                self.fetch_and_process_products(*task)
                self.task_queue.task_done()
            except Empty:
                continue

    def fetch_and_process_products(self, category, category_path):
        current_page = 1
        more_pages = True
        while more_pages:
            resp, page = self.fetch_products(category, current_page)
            if resp:
                self.process_product_data(resp, category_path)
                current_page += 1
            else:
                more_pages = False

    def try_get_page(self, params=None, headers=None):
        url = f'{self.url}/api/catalog_system/pub/category/tree/{self.tree_depth}'
        self.logger.print(f'Getting categories from {url}', Color.YELLOW)
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()  # This will raise an HTTPError if the response was an error
            response_json = response.json()
        except requests.exceptions.RequestException as e:
            self.logger.print(f'Failed to get categories: {e}', Color.RED)
            return

        for section in response_json:
            # For tree_depth == 1, only fetch top-level categories
            if self.tree_depth >= 1:
                if 'children' in section and len(section['children']) > 0:
                    for child in section['children']:
                        self.enqueue_category(child, [section['name']])
                else:
                    # Enqueue section if it has no children but is part of the required depth
                    self.enqueue_category(section, [])

            # If the tree_depth requires, dive deeper into the category structure
            if self.tree_depth >= 2 and 'children' in section:
                for category in section['children']:
                    if 'children' in category and len(category['children']) > 0:
                        for subcategory in category['children']:
                            self.enqueue_category(subcategory, [section['name'], category['name']])
                    else:
                        # Enqueue category if it has no children but is part of the required depth
                        self.enqueue_category(category, [section['name']])

    def enqueue_category(self, category, parent_names):
        category_id = category.get('id')
        category_path = parent_names + [category.get('name')]
        category_id_path = f'C:/{"/".join([str(id) for id in category_path])}/'
        # Enqueue the task with category ID and path for further processing
        self.task_queue.put((category_id_path, category_path))
        self.logger.print(f'Enqueued category {category_id_path}', Color.GREEN)


    # Other methods (api_get_products_by_page, save_to_excel, fetch_products, process_product_data) remain unchanged
    def save_to_excel(self, product):
        
        self.csv.write(self.parser.parse(product))

    
    def fetch_products(self, category, page):
        resp = self.api_get_products_by_page(category, page)
        if resp is None or resp.status_code not in (200, 206):
            error_msg = f'Error getting page {page} of category {category}'
            print(error_msg, file=sys.stderr)
            return None, page
        return resp.json(), page

    def process_product_data(self, product_data, category_path):
        for product in product_data:
            product['category_path'] = category_path
            self.save_to_excel(product)

    def get_products_by_category(self, category, category_path, max_workers=50):
        current_page = 1
        more_pages = True

        while more_pages:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.fetch_products, category, page) for page in range(current_page, current_page + max_workers)]
                for future in concurrent.futures.as_completed(futures):
                    product_data, page = future.result()
                    if product_data:
                        self.process_product_data(product_data, category_path)
                    else:
                        more_pages = False
                    if page >= current_page + max_workers - 1:
                        more_pages = False  # Assuming no more pages if any fetch fails or we reach the batch end without finding more data

            current_page += max_workers

    def shutdown_workers(self):
        for _ in self.workers:
            self.task_queue.put(None)  # Signal to stop the worker
        for worker in self.workers:
            worker.join()

    def execute(self):
        # This method is called to start the scraping process
        self.init_workers()
        self.try_get_page()
        # self.shutdown_workers()
        self.end_time = DateTime.now()
        self.logger.print(f'Elapsed time: {self.end_time - self.start_time}', Color.GREEN)

# Example usage:
# scrapper = ScrapperOfApi()
# scrapper.execute()



# import requests
# import sys
# from utils import CreateCSV, ColorPrint, Color
# from concurrent.futures import ThreadPoolExecutor
# from parser_data import ParserPlazaVea
# from datetime import datetime as DateTime
# import concurrent.futures
# WEB_URL = 'https://www.plazavea.com.pe'



# class ScrapperOfApi:
#     def __init__(self, url=WEB_URL, parser=ParserPlazaVea(), headers_csv=None, csv_name='./data.csv', tree_depth=3, threads=5):
#         self.threads = threads
#         self.url = url
#         self.tree_depth = tree_depth
#         self.timeout = 30
#         self.session = requests.Session()
#         self.session.headers.clear()
#         self.session.headers.update
#         self.page_size = 50
#         self.csv = CreateCSV(filename=csv_name, headers=headers_csv)
#         self.parser = parser
#         self.logger = ColorPrint()
#         self.start_time = DateTime.now()
#         self.end_time = None
#         self.try_get_page()

#     def try_get_page(self, params=None, headers=None):
#         url = f'{self.url}/api/catalog_system/pub/category/tree/3'
#         self.logger.print(f'Getting categories from {url}', ColorPrint.color.RED)
       
#         response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)

#         response_json = response.json()
#         for section in response_json:
            
#             if len(section['children']) == 0 and self.tree_depth == 2:
#                 category_id = f'C:/{section["id"]}/'
#                 category_path = [section['name']]
#                 self.logger.print(f'Getting products from category {category_id}', ColorPrint.color.RED)
#                 with ThreadPoolExecutor(max_workers=self.threads) as executor:
#                     executor.submit(self.get_products_by_category, category_id, category_path)
#                 continue

#             if not section['hasChildren']:
#                 continue

#             for category in section['children']:

#                 if self.tree_depth == 2:
#                     category_id = f'C:/{section["id"]}/{category["id"]}/'
#                     category_path = [section['name'], category['name']]

#                     # thread pool executor
#                     # print(category_id, category_path)

#                     with ThreadPoolExecutor(max_workers=self.threads) as executor:
#                         executor.submit(self.get_products_by_category, category_id, category_path)
                    
#                     continue

#                 if not category['hasChildren']:
#                     continue



#                 for subcategory in category['children']:

                    
#                     category_id = f'C:/{section["id"]}/{category["id"]}/{subcategory["id"]}/'
#                     category_path = [section['name'], category['name'], subcategory['name']]

#                     # thread pool executor
#                     # print(category_id, category_path)

#                     with ThreadPoolExecutor(max_workers=self.threads) as executor:
#                         executor.submit(self.get_products_by_category, category_id, category_path)
#         self.end_time = DateTime.now()
#         self.logger.print(f'Elapsed time: {self.end_time - self.start_time}', ColorPrint.color.GREEN)
#         return response.json()  
    
#     def api_get_products_by_page(self, category, page):
#         params = {
#             "fq": category,
#             "_from": (page - 1) * self.page_size,
#             "_to": page * self.page_size - 1,
#         }

#         self.logger.print(f'Getting products from category {category} page {page}', ColorPrint.color.VIOLET)
#         return self.session.get(f'{self.url}/api/catalog_system/pub/products/search/', params=params, timeout=self.timeout)
    
#     def save_to_excel(self, product):
        
#         self.csv.write(self.parser.parse(product))

    
#     def fetch_products(self, category, page):
#         resp = self.api_get_products_by_page(category, page)
#         if resp is None or resp.status_code not in (200, 206):
#             error_msg = f'Error getting page {page} of category {category}'
#             print(error_msg, file=sys.stderr)
#             return None, page
#         return resp.json(), page

#     def process_product_data(self, product_data, category_path):
#         for product in product_data:
#             product['category_path'] = category_path
#             self.save_to_excel(product)

#     def get_products_by_category(self, category, category_path, max_workers=50):
#         current_page = 1
#         more_pages = True

#         while more_pages:
#             with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#                 futures = [executor.submit(self.fetch_products, category, page) for page in range(current_page, current_page + max_workers)]
#                 for future in concurrent.futures.as_completed(futures):
#                     product_data, page = future.result()
#                     if product_data:
#                         self.process_product_data(product_data, category_path)
#                     else:
#                         more_pages = False
#                     if page >= current_page + max_workers - 1:
#                         more_pages = False  # Assuming no more pages if any fetch fails or we reach the batch end without finding more data

#             current_page += max_workers
