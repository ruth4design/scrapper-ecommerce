from utils import ColorPrint, Color


class ParserPlazaVea:

    def get_promotion_teaser_discount(self, product):
        for teaser in product['items'][0]['sellers'][0]['commertialOffer']['PromotionTeasers']:
            if teaser['Name'] == 'TARJETA OH - PVEA':
                parameters = teaser['Effects']['Parameters']
                for parameter in parameters:
                    if parameter['Name'] == 'PromotionalPriceTableItemsDiscount':
                        return parameter['Value']
            
        return None

    def parse(self, product) -> dict:
        
        try:
            delivery_available = False
            recojo_en_tienda = False
            despacho_a_domicilio = False
            for delivery_type in product.get('Tipo de envío', []):
                if delivery_type == "Despacho a domicilio":
                    despacho_a_domicilio = True
                if delivery_type == "Delivery Express":
                    delivery_available = True
                if delivery_type == "Recojo en tienda":
                    recojo_en_tienda = True
            price = product['items'][0]['sellers'][0]['commertialOffer']['PriceWithoutDiscount']
            promotion_teaser_discount = self.get_promotion_teaser_discount(product)
            price_card = None
            if promotion_teaser_discount:
                price_card = float(price) - float(promotion_teaser_discount)
            price_promo = product['items'][0]['sellers'][0]['commertialOffer']['Price']

                        # Initialize all variables as None
            competitor = None
            section = None
            category = None
            subcategory = None
            code_grouped = None
            code_individual = None
            ean = None
            description = None
            brand = None
            um = None
            seller = None
            stock = None
            has_stock = None

            # Try to assign values to each variable
            try:
                competitor = 'PlazaVea'
            except Exception as e:
                print(f"Error setting competitor: {e}")

            try:
                product_type = product.get('Tipo de Producto', [])

                section = product_type[0] if product_type else product['category_path'][0]
            except Exception as e:
                print(f"Error getting section: {e} {product['category_path']}")

            try:
                category = product['categories'][1].split('/')[1]
            except Exception as e:
                print(f"Error getting category: {e}")

            try:
                subcategory = product['categories'][1].split('/')[2]
            except Exception as e:
                print(f"Error getting subcategory: {e}")

            try:
                code_grouped = ''
            except Exception as e:
                print(f"Error setting code_grouped: {e}")

            try:
                code_individual = product['productReference']
            except Exception as e:
                print(f"Error getting code_individual: {e}")

            try:
                ean = product['items'][0]['ean']
            except Exception as e:
                print(f"Error getting ean: {e}")

            try:
                description = product['productName']
            except Exception as e:
                print(f"Error getting description: {e}")

            try:
                brand = product['brand']
            except Exception as e:
                print(f"Error getting brand: {e}")

            try:
                um = product['items'][0]['measurementUnit']
            except Exception as e:
                print(f"Error getting um: {e}")

            try:
                seller = product['items'][0]['sellers'][0]['sellerName']
            except Exception as e:
                print(f"Error getting seller: {e}")

            try:
                stock = product['items'][0]['sellers'][0]['commertialOffer']['AvailableQuantity']
            except Exception as e:
                print(f"Error getting stock: {e}")

            try:
                has_stock = stock > 0 and 'Si' or 'No'
            except Exception as e:
                print(f"Error determining has_stock: {e}")


            parsed_product = {
                'Competidor': competitor,
                'Categoría': category,
                'Subcategoría': subcategory,
                'Sección': section,
                'Código Web Agrupado': code_grouped,
                'Código Web Individual': code_individual,
                'EAN': ean,
                'Descripción': description,
                'Marca': brand,
                'UM': um,
                'Seller': seller,
                'RUC':'',
                'Precio Regular': price,
                'Precio Promo': price_promo,
                'Precio Tarjeta': price_card,
                'Página Web': product['link'],
                'Delivery disponible': delivery_available and 'Si' or 'No',
                'Recojo en tienda': recojo_en_tienda and 'Si' or 'No',
                'Despacho a domicilio':despacho_a_domicilio and 'Si' or 'No',
                'Shipping Cost':'',
                'Shipping Lead Time':'',
                'Delivery Time':'',
                'Tag Best Seller':'',
                'Stock': stock,
                'Tiene Stock': has_stock
            }
            return parsed_product
        except Exception as e:
            ColorPrint.print(f'Error parsing product {product["productId"]}: {e}', Color.RED)
            return {}


class ParserParaiso: 

    def parse(self, product) -> dict:
        try:

            competitor = 'Paraiso'
            section = None

            category = None

            try:
                category = "Home"
            except Exception as e:
                category = None

            subcategory = None

            try:
                subcategory = product['categories'][0].split('/')[1]
            except Exception as e:
                print(e)
                subcategory = None

            code_grouped = None
            code_individual = None
            try:
                code_individual = product['productReference']
            except Exception as e:
                code_individual = None
            ean = None
            try:
                ean = product['items'][0]['ean']
            except Exception as e:
                ean = None
            description = None

            try:
                description = product['productName']
            except Exception as e:
                description = None
            brand = None
            try:
                brand = product['brand']
            except Exception as e:
                brand = None
            model = None
            try:
                model = product['MODELOS'][0]
            except Exception as e:
                model = None
            line = None
            try:
                line = product['Línea'][0]
            except Exception as e:
                line = None
            um = None
            try:
                um = product['items'][0]['measurementUnit']
            except Exception as e:
                um = None
            seller = None
            try:
                seller = product['items'][0]['sellers'][0]['sellerName']
            except Exception as e:
                seller = None
            regular_price = None
            try:
                regular_price = product['items'][0]['sellers'][0]['commertialOffer']['Price']
            except Exception as e:
                regular_price = None
            promo_price = None

            try:
                promo_price = product['items'][0]['sellers'][0]['commertialOffer']['ListPrice']
            except Exception as e:
                promo_price = None

            card_price = None
            page_web = None
            try:
                page_web = product['link']
            except Exception as e:
                page_web = None
            shipping_cost = None
            shipping_lead_time = None
            breadcrumb = None
            colors = None
            try:
                colors = ",".join(product['items'][0]['Color'])
            except Exception as e:
                colors = None
            size = None
            try:
                size = ",".join(product['items'][0]['Medida'])
            except Exception as e:
                print(e)
                size = None
            stock = None
            try:
                stock = product['items'][0]['sellers'][0]['commertialOffer']['AvailableQuantity']
            except Exception as e:
                stock = None
            has_stock = None

            try:
                has_stock = "Si" if stock > 0 else "No"
            except Exception as e:
                has_stock = None


            parsed_product = {
                'competidor': competitor,
                'sección': section,
                'categoría': category,
                'subcategoría': subcategory,
                'cod_web_agrupado': code_grouped,
                'cod_web_individual': code_individual,
                'EAN': ean,
                'descripción': description,
                'marca': brand,
                'model': model,
                'line': line,
                'um': um,
                'seller': seller,
                'precio_regular': regular_price,
                'precio_promo': promo_price,
                'precio_tarjeta': card_price,
                'pagina_web': page_web,
                'stock': stock,
                'lead_time': shipping_lead_time,
                'shipping_price': shipping_cost,
                'breadcrumb': breadcrumb,
                'colors': colors,
                'existe_stock': has_stock,
                'size': size
            }
            return parsed_product
        except Exception as e:
            ColorPrint.print(f'Error parsing product {product["productId"]}: {e}', Color.RED)
            return {}
