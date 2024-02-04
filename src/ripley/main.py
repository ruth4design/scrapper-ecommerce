
from driver import init_driver, simulate_scroll, Selector
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
        self.MAX_THREADS_CATEGORY = MAX_THREADS_CATEGORY
        self.MAX_THREADS_PRODUCT = MAX_THREADS_PRODUCT


    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()
    
    def get_data(self):
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
        file_name = f'./output/ripley/paraiso-peru-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        csv_file = CreateCSV(filename=file_name, headers=csv_headers)
        self.scrape_data_ripley(csv_file)
        
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
    
    def get_product_category(self, product: WebElement):
        try:
            return self.get_product_breadcrumb(product)[0]
        except Exception:
            return EMPTY_FIELD
    
    def get_product_subcategory(self, product: WebElement):
        try:
            return self.get_product_breadcrumb(product)[1]
        except Exception:
            return EMPTY_FIELD
    
    def get_product_section(self, product: WebElement):
        try:
            return self.get_product_breadcrumb(product)[2]
        except Exception:
            return EMPTY_FIELD
    
    def get_product_code_grouped(self, product: WebDriver):
        try:
            last_path = product.current_url.split('/')[-1].split('?')[0].split('-')[-1]
            # check if pmp string is in the last path
            if 'pmp' in last_path:
                return last_path
            return EMPTY_FIELD
        except Exception:
            return EMPTY_FIELD
    def get_product_code_individual(self, product: WebDriver):
        try:
            sku = Selector(product).get('.sku-container .sku-value').get_attribute('innerHTML')
            return sku
        except Exception:
            return EMPTY_FIELD
    def get_product_ean(self, product: WebElement):
        return EMPTY_FIELD
    
    def get_product_description(self, product: WebElement):
        try:
            return Selector(product).get('.product-header h1').get_attribute('innerHTML')
        except Exception:
            return EMPTY_FIELD
    def get_product_brand(self, product: WebElement):
        try:
            table = Selector(product).get('#panel-Especificaciones .rpl-product-description-wrapper .table')
            return self.get_value_in_table(table, 'Marca')
        except Exception:
            return EMPTY_FIELD
    def get_product_um(self, product: WebElement):
        return 'UN'
    
    def get_product_seller(self, product: WebElement):
        try:
            seller = Selector(product).get('.product-information-cell a').get_attribute('innerHTML')
            return seller
        except Exception:
            return 'Ripley'
    
    def get_product_ruc(self, product: WebElement):
        return EMPTY_FIELD
    
    def get_product_regular_price(self, product: WebElement):
        try:
            return product.find_element(By.CSS_SELECTOR, '.product-normal-price .product-price').get_attribute('innerHTML')
        except Exception:
            return EMPTY_FIELD
    def get_product_promo_price(self, product: WebElement):
        try:
            return product.find_element(By.CSS_SELECTOR, '[class*=product-internet] .product-price').get_attribute('innerHTML')
        except Exception:
            return EMPTY_FIELD
        
    def get_product_card_price(self, product: WebElement):
        try:
            return product.find_element(By.CSS_SELECTOR, '.product-price-container.product-ripley-price .product-price').get_attribute('textContent').strip()
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

    def get_product_tags(self, product: WebElement):
        try :
            tags = product.find_elements(By.CSS_SELECTOR, '.product-header-emblems__desktop .product-emblems .emblem')
            return [tag.get_attribute('innerText') for tag in tags]
        except Exception:
            return []

    def get_product_best_seller_tag(self, product: WebElement):
        try:
            all_tags = self.get_product_tags(product)
            if 'Vendedor destacado' in all_tags:
                return 'Vendedor destacado'
        except Exception:
            return EMPTY_FIELD
    
    def get_product_stock(self, product: WebElement):
        return EMPTY_FIELD
    
    def get_product_has_stock(self, product: WebElement):

        try:
            stock = Selector(product).get('#buy-button').get_attribute('innerText')
            if 'Agregar al carro' in stock:
                return 'Si'
            return 'No'
        except Exception:

            return 'No'
    
    def get_product_model(self, product: WebElement):

        try:
            table = Selector(product).get('#panel-Especificaciones .rpl-product-description-wrapper .table')
            return self.get_value_in_table(table, 'Modelo')
        except Exception:

            return EMPTY_FIELD
    def get_delivery_information(self, product: WebElement, text: str):
        try:
            delivery_options = Selector(product).get_all('.pickup-and-delivery__information')
            # check if text exist in some of the delivery options
            for option in delivery_options:
                if text in option.get_attribute('innerHTML'):
                    return 'Disponible'
            return 'No disponible'
        except Exception as e:
            print(f'No se pudo obtener la información de envío {e}')
            return 'No disponible'
  
        
    def scrape_product(self, product_url, csv_file: CreateCSV):

        try:
            driver = init_driver()
            driver.get(product_url)
            self.select_location(driver)
            product_obj = {}
            
            product_obj['Competidor'] = self.get_product_competitor(driver)
            product_obj['Categoría'] = self.get_product_category(driver)
            product_obj['Subcategoría'] = self.get_product_subcategory(driver)
            product_obj['Sección'] = self.get_product_section(driver)
            product_obj['Código Web Agrupado'] = self.get_product_code_grouped(driver)
            product_obj['Código Web Individual'] = self.get_product_code_individual(driver)
            product_obj['EAN'] = self.get_product_ean(driver)
            product_obj['Descripción'] = self.get_product_description(driver)
            product_obj['Marca'] = self.get_product_brand(driver)
            product_obj['UM'] = self.get_product_um(driver)
            product_obj['Seller'] = self.get_product_seller(driver)
            product_obj['RUC'] = self.get_product_ruc(driver)
            product_obj['Precio Regular'] = self.get_product_regular_price(driver)
            product_obj['Precio Promo'] = self.get_product_promo_price(driver)
            product_obj['Precio Tarjeta'] = self.get_product_card_price(driver)
            product_obj['Página Web'] = product_url
            product_obj['Delivery disponible'] = self.get_delivery_information(driver, text='Despacho disponible.')
            product_obj['Recojo en tienda'] = self.get_delivery_information(driver, text='Retiro en tienda disponible.')
            product_obj['Retiro cercano'] = self.get_delivery_information(driver, text='Retiro cercano disponible.')
            product_obj['Shipping Cost Express'] = self.get_product_shipping_cost(driver, key='Express')
            product_obj['Shipping Lead Time Express'] = self.get_product_shipping_lead_time(driver, key='Express')
            product_obj['Delivery Time Express'] = self.get_days_until_date(product_obj['Shipping Lead Time Express'])
            product_obj['Shipping Cost Normal'] = self.get_product_shipping_cost(driver, key='Normal')
            product_obj['Shipping Lead Time Normal'] = self.get_product_shipping_lead_time(driver, key='Normal')
            product_obj['Delivery Time Normal'] = self.get_days_until_date(product_obj['Shipping Lead Time Normal'])
            product_obj['Tag Best Seller'] = self.get_product_best_seller_tag(driver)
            product_obj['All Tags'] = ','.join(self.get_product_tags(driver))
            product_obj['Stock'] = ''
            product_obj['Tiene Stock'] = self.get_product_has_stock(driver)
            product_obj['Modelo'] = self.get_product_model(driver)

            self.counter += 1
            csv_file.write(product_obj)
            
            # remove driver from memory
            driver.quit()

            ColorPrint.print(f"Scraped {self.counter} products", Color.GREEN)
        except Exception as e:
            print(f"An error occurred while processing product link {product_url}: {e}")
            return None
        
    def scrape_category(self, category_url, csv_file):
        try:
            driver = init_driver()
            
            driver.get(category_url)
           
            products = Selector(driver).get_all('.catalog-page__product-grid--with-sidebar .catalog-container .catalog-product-item a')

            product_urls = [product.get_attribute('href') for product in products]
            with ThreadPoolExecutor(max_workers=self.MAX_THREADS_PRODUCT) as executor:
                for product_url in product_urls:
                    executor.submit(self.scrape_product, product_url, csv_file)

            # go to next page if exists
            try:
                next_page = Selector(driver).get_all('.pagination a').pop().get_attribute('href')

                if next_page.endswith('#'):
                    return None
                return self.scrape_category(next_page, csv_file)
                
            except Exception:
                pass

            # self.driver.get(category_url)
            # self.check_sidebar_open()
            # simulate_scroll(self.driver, timeout=3, logger=False)
            # products = Selector(self.driver).get_all('.catalog-product-item')
            # for product in products:
            #     self.scrape_product(product, csv_file)
        except Exception :
            pass

    def scrape_data_ripley(self, csv_file):
        self.driver.get(self.url)
        hamburger_menu = self.get_hamburger_menu()
        # wait until the hamburger menu is clickable
       
        hamburger_menu.click()
        navbar_items = self.driver.find_elements(By.CSS_SELECTOR, '.tree-node-items > a')
        
        categories_url = []
        for item in navbar_items:
            categories_url.append(item.get_attribute('href'))

        with ThreadPoolExecutor(max_workers=self.MAX_THREADS_CATEGORY) as executor:
            for category_url in categories_url:
                executor.submit(self.scrape_category, category_url, csv_file)

        
        
    
    




    