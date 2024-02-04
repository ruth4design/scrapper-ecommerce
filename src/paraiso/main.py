
from driver import init_driver, simulate_scroll, Selector
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import CreateCSV, purify_str, Color, ColorPrint
from threading import Lock
from datetime import datetime

EMPTY_FIELD = 'X'

THREADS_FOR_NAVBAR = 1
THREADS_FOR_PRODUCT = 5


class ParaisoScrapper:
    def __init__(self, url, timer_for_scroll=2.5, threads_for_navbar=THREADS_FOR_NAVBAR, threads_for_product=THREADS_FOR_PRODUCT):
        self.url = url
        self.driver = init_driver()
        self.lock = Lock()
        self.counter = 0
        self.THREADS_FOR_NAVBAR = threads_for_navbar
        self.THREADS_FOR_PRODUCT = threads_for_product
        self.TIMER_FOR_SCROLL = timer_for_scroll

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()
    
    def get_data(self):
        csv_headers = [
            'competidor',
            'sección',
            'categoría',
            'subcategoría',
            'cod_web_agrupado',
            'cod_web_individual',
            'EAN',
            'descripción',
            'marca',
            'model',
            'line',
            'um',
            'seller',
            'precio_regular',
            'precio_promo',
            'precio_tarjeta',
            'pagina_web',
            'stock',
            'lead_time',
            'shipping_price',
            'breadcrumb',
            'colors',
            'existe_stock',
            'size'

        ]
        file_name = f'./output/paraiso/paraiso-peru-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        csv_file = CreateCSV(filename=file_name, headers=csv_headers)
        self.scrape_data_paraiso(csv_file)
        
        csv_file.close()
    
    def scrape_data_paraiso(self, csv_file):
        self.driver.get(self.url)
        navbar_items = self.driver.find_elements(By.CSS_SELECTOR, '#navbar #menu2 ul .container_menu .filas2 li')
        LINES = [
            'Royal', 'Pocket', 'Premium', 'Standard', 'Zebra'
        ]

        MODELS = [
            'Gold', 'Blocks', 'Novo', 'Capitoneada', 'Loft', 'Europea', 'Con cajones', 'Diván'
        ]
        search_all_items = []
        for item in navbar_items:

            # convert item html to driver
            try:
                item.find_element(By.CSS_SELECTOR, 'a u')
                search_all_items.append(item)
            except NoSuchElementException as e:
                # print(f"This is not `Todos` link: {item.get_attribute('innerHTML')}")
                continue

        requested_pages = []
        data = []
        with ThreadPoolExecutor(max_workers=self.THREADS_FOR_NAVBAR) as executor:
            future_to_item = {
                executor.submit(self.process_navbar_item, item, requested_pages, data, LINES, MODELS, EMPTY_FIELD, csv_file): item for item in search_all_items
                }
            
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    future.result()  # We don't need the result here, just ensuring all tasks are completed
                except Exception as exc:
                    print(f"{item} generated an exception: {exc}")

        return data
    
    def process_navbar_item(self, navbar_item, requested_pages, data, lines, models, empty_field, csv_file):
        try:
            link = navbar_item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            if link in requested_pages:
                return
            requested_pages.append(link)

            with init_driver() as navbar_driver:  # Each navbar item gets its own driver instance
                navbar_driver.get(link)
                simulate_scroll(navbar_driver, timeout=self.TIMER_FOR_SCROLL, logger=False)
                elements = navbar_driver.find_elements(By.CSS_SELECTOR, '.itemProduct.n1colunas ul>li[class*="paraiso-peru"]')
                ColorPrint.print(f"Total elements to process: {len(elements)} {link}", Color.RED)
                with ThreadPoolExecutor(max_workers=self.THREADS_FOR_PRODUCT) as executor:
                    future_to_element = {executor.submit(self.process_product_link, element.find_element(By.CSS_SELECTOR, '.row.img>a').get_attribute('href'), lines, models, empty_field, csv_file): element for element in elements}
                    
                    for future in as_completed(future_to_element):
                        element = future_to_element[future]
                        try:
                            result = future.result()
                            if result:
                                data.append(result)
                        except Exception as exc:
                            print(f"Element {element} generated an exception: {exc}")

        except NoSuchElementException as e:
            print(f"An element was not found: {e}")

    def process_product_link(self, product_link, lines, models, empty_field, csv_file):
        # Initialize driver for each product to avoid conflicts in parallel execution
        
        product_data = {}

        with init_driver() as product_driver:
            try:
                product_driver.get(product_link)
                WebDriverWait(product_driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.agregar_descuento')))
                
                selector = Selector(product_driver)
                product_data['competidor'] = "paraiso-peru"
                product_data['sección'] = empty_field
                title = selector.get('.product-name .productName').get_attribute('innerHTML')
                category = None

                breadcrumb_selector = '.bread-crumb [itemProp=itemListElement] [itemProp=name]'
                try:
                    category = selector.get_all(breadcrumb_selector)[0].text
                except IndexError:
                    category = ''
                subcategory = None
                try:
                    subcategory = selector.get_all(breadcrumb_selector)[1].text
                except IndexError:
                    subcategory = ''

                product_data['categoría'] = category
                product_data['subcategoría'] = subcategory
                product_data['cod_web_agrupado'] = empty_field
                product_data['cod_web_individual'] = selector.get('.skuReference').get_attribute('innerHTML')
                product_data['EAN'] = empty_field
                description = ''
                try:
                    description = title
                except AttributeError:
                    description = ''

                product_data['descripción'] = description
                product_data['size'] = title.split('|')[-1]
                product_data['marca'] = 'Paraiso'
                product_data['um'] = 'UN'
                product_data['seller'] = 'Paraiso'
                product_data['precio_regular'] = selector.get('.product-info .skuListPrice').text
                product_data['precio_promo'] = selector.get('.product-info .skuBestPrice').text
                product_data['precio_tarjeta'] = empty_field
                product_data['pagina_web'] = product_link
                stock = selector.get('.product-info .stock p').text.replace('Stock:', '').strip()
                product_data['stock'] = stock
                product_data['existe_stock'] = "Si" if int(stock) > 0 else "No"
                product_data['lead_time'] = empty_field
                product_data['shipping_price'] = empty_field
                breadcrumb_html = selector.get_all('.bread-crumb [itemProp=item] [itemProp=name]')
                breadcrumb = ''
                for item in breadcrumb_html:
                    breadcrumb += item.text + '> '
                product_data['breadcrumb'] = purify_str(breadcrumb, '> ')

                model = ''
                line = ''
                for line_item in lines:
                    if line_item in title:
                        line = line_item
                        break
                for model_item in models:
                    if model_item in title:
                        model = model_item
                        break
                product_data['model'] = model
                product_data['line'] = line

                colors_html = selector.get_all('.skuList.item-dimension-Color label')
                colors = ''
                for color in colors_html:
                    colors += color.get_attribute('innerHTML') + ', '

                product_data['colors']= purify_str(colors, ', ')

                # remove driver from memory
                product_driver.quit()
                # csv_file.write(product_data)

            except (NoSuchElementException, TimeoutException) as e:
                print(f"An error occurred while processing product link {product_link}: {e}")

        with self.lock:
            self.counter += 1
            csv_file.write(product_data)
            ColorPrint.print(f"{self.counter}: Writing product link {product_link}", Color.GREEN)

        return product_data
    
    




    