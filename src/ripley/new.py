
import time
from driver import init_driver, simulate_scroll, Selector
from selenium.webdriver.chrome.options import Options
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import CreateCSV, purify_str, Color, ColorPrint
from threading import Lock
from datetime import datetime
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List

EMPTY_FIELD = 'X'

MAX_THREADS_CATEGORY = 1
MAX_THREADS_PRODUCT = 5

class RipleyScrapper:
    def __init__(self, url):
        self.url = url
        self.driver = init_driver()
        self.lock = Lock()
        self.counter = 0
        self.categories = []
        self.MAX_THREADS_CATEGORY = MAX_THREADS_CATEGORY
        self.MAX_THREADS_PRODUCT = MAX_THREADS_PRODUCT


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()

    def get_data(self, printer: ColorPrint):
        csv_headers = [
            'Competidor',
            'Categoría',
            'Subcategoría',
            'Sección',
            'Código Web Agrupado',
            'Código Web Individual',
            'EAN',
            'Descripción',
            'Marca',
            'UM',
            'Seller',
            'RUC',
            'Precio Regular',
            'Precio Promo',
            'Precio Tarjeta',
            'Página Web',
            'Delivery disponible',
            'Recojo en tienda',
            'Retiro cercano',
            'Shipping Cost Express',
            'Shipping Lead Time Express',
            'Delivery Time Express',
            'Shipping Cost Normal',
            'Shipping Lead Time Normal',
            'Delivery Time Normal',
            'Tag Best Seller',
            'All Tags',
            'Stock',
            'Tiene Stock',
            'Modelo',
        ]
        file_name = f'./output/ripley/ripley-peru-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        csv_file = CreateCSV(filename=file_name, headers=csv_headers)
        self.scrape_data_ripley(csv_file, printer=printer)

        csv_file.close()



    def get_hamburger_menu(self):
        hamburger_menu = Selector(self.driver).get('.menu-button')
        # wait until the hamburger menu is clickable
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.menu-button'))
        )
        return hamburger_menu

    def check_sidebar_open(self):
        try:
            hamburger_menu = self.get_hamburger_menu()
            hamburger_menu.click()
            self.driver.implicitly_wait(0.5)
        except Exception:
            return None
    def get_product_breadcrumb(self, product: WebElement):
        return [breadcrumb.text for breadcrumb in product.find_elements(By.CSS_SELECTOR, '.breadcrumbs a span') ]

    def get_value_in_table(self, table: WebElement, label: str):
        try:
            # Encuentra todas las filas en el elemento del
            rows = table.find_elements(By.CSS_SELECTOR, "tr")

            # Itera sobre cada fila para buscar la etiqueta
            for row in rows:
                # Obtén las celdas de la fila
                cells = row.find_elements(By.CSS_SELECTOR,"td")

                if len(cells) == 2 and cells[0].get_attribute('innerHTML').strip() == label:
                    # Retorna el valor si la etiqueta coincide
                    return cells[1].get_attribute('innerHTML').strip()

            # Si no se encuentra la etiqueta, retorna el valor predeterminado
            return EMPTY_FIELD

        except Exception:
            return EMPTY_FIELD


    def get_product_competitor(self, product: WebElement):
        return 'Ripley'

    def flat_map_category(self, categories):
        flat_categories = []
        for category in categories:
            flat_categories.append({
                'identifier': category['identifier'],
                'name': category['name'],
                'slug': category['slug'],
            })
            if len(category['categories']) > 0:
                flat_categories += self.flat_map_category(category['categories'])
        return flat_categories
        
    def get_product_breadcrumb(self, menu, categories: List[dict], index=0):
        try:
            category_id = menu[index]

            for category in categories:
                if category['identifier'] == category_id:
                    return category['name']
                
            return EMPTY_FIELD
        except Exception:
            return EMPTY_FIELD

    def get_product_subcategory(self, menu, categories: List[dict]):
        return self.get_product_breadcrumb(menu, categories, index=1)

    def get_product_section(self, menu, categories: List[dict]):
        return self.get_product_breadcrumb(menu, categories, index=2)

    def get_product_code_grouped(self, product):
        try:
            return product['parentProductID']
        except Exception:
            return EMPTY_FIELD
    def get_product_code_individual(self, product):
        try:
            return product['selectedPartNumber']
        except Exception:
            return EMPTY_FIELD
    def get_product_ean(self, product: WebElement):
        return EMPTY_FIELD

    def get_product_description(self, product):
        try:
            return product['name']
        except Exception:
            return EMPTY_FIELD
        
    def get_attribute_by_identifier(self, product, identifier):
        try:
            for attribute in product['attributes']:
                if attribute['identifier'] == identifier:
                    return attribute['value']
            return EMPTY_FIELD
        except Exception:
            return EMPTY_FIELD
    def get_product_brand(self, product):
        try:
            brand = self.get_attribute_by_identifier(product, 'marca')
            return brand
        except Exception:
            return EMPTY_FIELD
    def get_product_um(self, product: WebElement):
        return 'UN'

    def get_product_seller(self, product):
        try:
            return self.get_attribute_by_identifier(product, 'seller_v2')
        except Exception:
            return 'Ripley'

    def get_product_ruc(self, product: WebElement):
        return EMPTY_FIELD

    def get_product_regular_price(self, product):
        try:
            return product['prices']['offerPrice'] + product['prices']['discount']
        except Exception:
            return EMPTY_FIELD
    def get_product_promo_price(self, product):
        try:
            return product['prices']['offerPrice']
        except Exception:
            return EMPTY_FIELD

    def get_product_card_price(self, product):
        try:
            return product['prices']['cardPrice']
        except Exception:
            return EMPTY_FIELD

    def get_product_page(self, product: WebElement):
        try:
            return product.get_attribute('href')
        except Exception:
            return EMPTY_FIELD

    def select_location(self, driver_product: WebElement):
        try:
            select =  driver_product.find_element(By.CSS_SELECTOR, '.Select-control')
            select.click()
            id_lima_department = '#react-select-2--option-14'
            lima_department = driver_product.find_element(By.CSS_SELECTOR, id_lima_department)
            lima_department.click()

            select_province = driver_product.find_elements(By.CSS_SELECTOR, '.Select-placeholder')[-1]
            select_province.click()
            id_lima_province = 'react-select-4--option-7'
            lima_province = driver_product.find_element(By.ID, id_lima_province)
            lima_province.click()


            select_district = driver_product.find_elements(By.CSS_SELECTOR, '.Select-placeholder')[-1]
            select_district.click()
            id_lima_district = 'react-select-6--option-14'
            lima_district = driver_product.find_element(By.ID, id_lima_district)
            lima_district.click()
            button = driver_product.find_element(By.CSS_SELECTOR, '.location-button-container .location-button')
            button.click()

            WebDriverWait(driver_product, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.pickup-and-delivery__options'))
            )
            return 'Disponible'
        except Exception as e:
            print(f'No se pudo obtener el tag de envío {e}')
            return EMPTY_FIELD
    def get_product_shipping_tag(self, product: WebElement):
        return EMPTY_FIELD
    def get_by_key_cost(self, option_details: List[WebElement], key: str):
        for option_detail in option_details:
            print(option_detail.get_attribute('outerHTML'))
            if option_detail.find_element(By.CSS_SELECTOR, '.pickup-and-delivery__options__name').get_attribute('innerHTML') == key:
                return option_detail.find_element(By.CSS_SELECTOR, '.pickup-and-delivery__options__details').get_attribute('innerHTML')
        return EMPTY_FIELD

    def get_number_from_string(self, string: str):

        number = ''
        for char in string:
            if char.isdigit() or char == '.':
                number += char
        return number



    def get_product_shipping_cost(self, product: WebElement, key: str = 'Express'):
        try:
            all_details = product.find_elements(By.CSS_SELECTOR, '.pickup-and-delivery__options')
            express_cost = self.get_by_key_cost(all_details, key=key)
            if express_cost != EMPTY_FIELD:
                string = express_cost.split(',')[0]
                return self.get_number_from_string(string)
            return EMPTY_FIELD

            #Array of  <div class="pickup-and-delivery__options"><span class="pickup-and-delivery__options__name">Express</span><span class="pickup-and-delivery__options__details">: a partir de S/ 12, para el 3 de febrero</span></div>
        except Exception as e:
            print(f'No se pudo obtener el costo de envío {e}')
            return EMPTY_FIELD

    def format_date(self, date: str):

        months = {
            'enero': '01',
            'febrero': '02',
            'marzo': '03',
            'abril': '04',
            'mayo': '05',
            'junio': '06',
            'julio': '07',
            'agosto': '08',
            'septiembre': '09',
            'octubre': '10',
            'noviembre': '11',
            'diciembre': '12'
        }

        arr_string_date = date.replace('para el ', '').strip().split(' ')

        day = arr_string_date[-3]

        if len(day) == 1:
            day = '0' + day
        month = months[arr_string_date[-1]]

        # return a valid date format ejm: 2022-02-05
        new_valid_date = datetime.now().strftime('%Y') + '-' + month + '-' + day
        return new_valid_date





    def get_product_shipping_lead_time(self, product: WebElement, key: str = 'Express'):

        try:
            all_details = product.find_elements(By.CSS_SELECTOR, '.pickup-and-delivery__options')
            express_lead_time = self.get_by_key_cost(all_details, key=key)
            if express_lead_time != EMPTY_FIELD:
                date_info =  express_lead_time.split(',')[1]
                valid_date = self.format_date(date_info)

                return valid_date

            return EMPTY_FIELD
        except Exception:
            return EMPTY_FIELD

    def get_days_until_date(self, date: str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
            today = datetime.now()

            difference = date - today
            flat_days = difference.days
            if difference.seconds > 0:
                flat_days += 1
            return flat_days

        except Exception:
            return EMPTY_FIELD

    def get_product_tags(self, product):
        try :
            
            return [tag['label'] for tag in product['tags']]
        except Exception:
            return []

    def get_product_best_seller_tag(self, product: WebElement):
        try:
            all_tags = self.get_product_tags(product)
            if 'Vendedor destacado' in all_tags:
                return 'Vendedor destacado'
        except Exception:
            return EMPTY_FIELD

    def get_product_stock(self, product):
        try:
            return 'Si' if product['stock']['available'] else 'No'
        except Exception:
            return EMPTY_FIELD

    def get_product_has_stock(self, product):

        try:
            return 'No' if product['isOutOfStock'] else 'Sí'
        except Exception:

            return 'No'

    def get_product_model(self, product: WebElement):

        try:
            table = Selector(product).get('#panel-Especificaciones .rpl-product-description-wrapper .table')
            return self.get_value_in_table(table, 'Modelo')
        except Exception:

            return EMPTY_FIELD
    def get_delivery_information(self, product, id: str):
        try:
            if product['shipping'][id]:
                return 'Disponible'
            return 'No disponible'
        except Exception as e:
            print(f'No se pudo obtener la información de envío {e}')
            return 'No disponible'



    def scrape_category_per_page(self, category_url, csv_file):
        try:

            # options.s
            driver = init_driver(
               disable_js=True
            )

            driver.get(category_url)

            # products = Selector(driver).get_all('.catalog-page__product-grid--with-sidebar .catalog-container .catalog-product-item a')

            # get window.__INITIAL_STATE__

            # initial_state = driver.execute_script('return window.__PRELOADED_STATE__')

            # get the text/javascript tag that has inside this window.__PRELOADED_STATE__ variable

            scripts = Selector(driver=driver).get_all('script[type="text/javascript"]')

            # get the script that has the window.__PRELOADED_STATE__ variable

            script = [script for script in scripts if 'window.__PRELOADED_STATE__' in script.get_attribute('innerHTML')][0]
            
            driver.execute_script(script.get_attribute('innerHTML'))

            preloaded_state_obj = driver.execute_script('return window.__PRELOADED_STATE__')

            products = preloaded_state_obj['products']

            if len(self.categories) == 0:
                self.categories = self.flat_map_category(preloaded_state_obj['categories']['normal']) 
            menu = preloaded_state_obj['menu']['branch']
            for product in preloaded_state_obj['products']:
                product_obj = {}

                product_obj['Competidor'] = "Ripley"

                product_obj['Categoría'] = self.get_product_breadcrumb(menu, self.categories)
                product_obj['Subcategoría'] = self.get_product_subcategory(menu=menu, categories=self.categories)
                product_obj['Sección'] = self.get_product_section(menu=menu, categories=self.categories)
                product_obj['Código Web Agrupado'] = self.get_product_code_grouped(product=product)
                product_obj['Código Web Individual'] = self.get_product_code_individual(product=product)
                product_obj['EAN'] = self.get_product_ean(driver)
                product_obj['Descripción'] = self.get_product_description(product=product)
                product_obj['Marca'] = self.get_product_brand(product=product)
                product_obj['UM'] = self.get_product_um(driver)
                product_obj['Seller'] = self.get_product_seller(product=product)
                product_obj['RUC'] = self.get_product_ruc(driver)
                product_obj['Precio Regular'] = self.get_product_regular_price(product=product)
                product_obj['Precio Promo'] = self.get_product_promo_price(product=product)
                product_obj['Precio Tarjeta'] = self.get_product_card_price(product=product)
                product_obj['Página Web'] = product['url']
                product_obj['Delivery disponible'] = self.get_delivery_information(product=product, id='dDomicilio')
                product_obj['Recojo en tienda'] = self.get_delivery_information(product=product, id='rTienda')
                product_obj['Retiro cercano'] = self.get_delivery_information(product=product, id='rCercano')
                product_obj['Shipping Cost Express'] =  'No implementado' #self.get_product_shipping_cost(driver, key='Express')
                product_obj['Shipping Lead Time Express'] = 'No implementado' #self.get_product_shipping_lead_time(driver, key='Express')
                product_obj['Delivery Time Express'] = 'No implementado' #self.get_days_until_date(product_obj['Shipping Lead Time Express'])
                product_obj['Shipping Cost Normal'] = 'No implementado' # self.get_product_shipping_cost(driver, key='Normal')
                product_obj['Shipping Lead Time Normal'] ='No implementado' # self.get_product_shipping_lead_time(driver, key='Normal')
                product_obj['Delivery Time Normal'] = 'No implementado' # self.get_days_until_date(product_obj['Shipping Lead Time Normal'])
                product_obj['Tag Best Seller'] = self.get_product_best_seller_tag(product=product)
                product_obj['All Tags'] = ','.join(self.get_product_tags(product=product))
                product_obj['Stock'] = ''
                product_obj['Tiene Stock'] = self.get_product_has_stock(product=product)
                product_obj['Modelo'] = self.get_attribute_by_identifier(product=product, identifier='modelo')
                self.counter += 1
                csv_file.write(product_obj)

                # remove driver from memory

                ColorPrint.print(f"Scraped {self.counter} products {product['url']}", Color.GREEN)

            print('=====================')
            print(category_url)
            # print(preloaded_state_obj['products'])
            print('=====================')

            # product_urls = [product.get_attribute('href') for product in products]
            # with ThreadPoolExecutor(max_workers=self.MAX_THREADS_PRODUCT) as executor:
            #     for product_url in product_urls:
            #         executor.submit(self.scrape_product, product_url, csv_file)

            # go to next page if exists
            try:
                next_page = Selector(driver).get_all('.pagination a').pop().get_attribute('href')
                driver.quit()
                print(next_page)
                if next_page.endswith('#'):
                    return None
                return self.scrape_category_per_page(next_page, csv_file)

            except Exception as e:
                print('No next page',e)
                

            # self.driver.get(category_url)
            # self.check_sidebar_open()
            # simulate_scroll(self.driver, timeout=3, logger=False)
            # products = Selector(self.driver).get_all('.catalog-product-item')
            # for product in products:
            #     self.scrape_product(product, csv_file)
        except Exception as e:
            print(f"An error occurred while processing category link {category_url}: {e}")

            # try again in 5 seconds
            time.sleep(5)
            self.scrape_category_per_page(category_url, csv_file)
             


    def select_category(self, categories_url):
        for i, category in enumerate(categories_url):
            # name_category = category.split('/')[-1].split('?')[0]
            print(f'{i + 1}. {category['slug']}')
        category = int(input('Seleccione una categoría: '))

        initial_page = input('Ingrese la página inicial(O preciones enter para omitir): ')
        if initial_page == '':
            initial_page = 1
        else:
            initial_page = int(initial_page)
        
        return categories_url[category - 1]['slug'] + f'?page={initial_page}'

    def scrape_data_ripley(self, csv_file, printer: ColorPrint):
        self.driver.get(self.url)

        
        scripts = Selector(driver=self.driver).get_all('script[type="text/javascript"]')

        # get the script that has the window.__PRELOADED_STATE__ variable

        script = [script for script in scripts if 'window.__PRELOADED_STATE__' in script.get_attribute('innerHTML')][0]
        
        self.driver.execute_script(script.get_attribute('innerHTML'))

        preloaded_state_obj = self.driver.execute_script('return window.__PRELOADED_STATE__')

        categories_url = preloaded_state_obj['categories']['normal']
        # print(categories_url)

        # hamburger_menu = self.get_hamburger_menu()
        # # wait until the hamburger menu is clickable

        # hamburger_menu.click()
        # navbar_items = self.driver.find_elements(By.CSS_SELECTOR, '.tree-node-items > a')

        # printer.stop_loader("==========================")
        # categories_url = []
        # for item in categories_url:
        #     categories_url.append(item.get_attribute('href'))
        # select category in terminal input
        category_url = self.select_category(categories_url)
        print(category_url)
        category = category_url.split('/')[-1].split('?')[0]
        printer.start_loader(text=f"Searching for data Ripley for category: {category}", color=Color.GREEN)


        self.scrape_category_per_page(self.url+category_url, csv_file)
        # with ThreadPoolExecutor(max_workers=self.MAX_THREADS_CATEGORY) as executor:
        #     for category_url in categories_url:
        #         executor.submit(self.scrape_category_per_page, category_url, csv_file)
