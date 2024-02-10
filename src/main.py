import argparse
from headers import csv_paraiso_headers, headers_plaza_vea_csv
from paraiso.main import ParaisoScrapper
from ripley.main import RipleyScrapper
from utils import ColorPrint, Color

from datetime import datetime
from api import ScrapperOfApi
from parser_data import ParserPlazaVea, ParserParaiso

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ripley', action='store_true', help='Use the Ripley scrapper')
    parser.add_argument('--paraiso', action='store_true', help='Use the Paraiso scrapper')
    parser.add_argument('--plazavea', action='store_true', help='Use the Plazavea scrapper')
    args = parser.parse_args()
    printer = ColorPrint()

    if args.plazavea:
        printer.start_loader(text="Searching for data Plazavea ", color=Color.GREEN)
        file_name = f'./output/plazavea/plaza-vea-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'

        plazavea_scrapper = ScrapperOfApi(headers_csv=headers_plaza_vea_csv, csv_name=file_name,)
    if args.ripley:
        printer.start_loader(text="Searching for data Ripley ", color=Color.GREEN)
        ripley_scrapper = RipleyScrapper(url='https://simple.ripley.com.pe/')
        data = ripley_scrapper.get_data()
    if args.paraiso:
        printer.start_loader(text="Searching for data Paraiso ", color=Color.GREEN)
        # paraiso_scrapper = ParaisoScrapper(url='https://www.paraiso-peru.com/', timer_for_scroll=10.5, threads_for_navbar=1, threads_for_product=5)
        # data = paraiso_scrapper.get_data()
        url = 'https://www.paraiso-peru.com'
        file_name = f'./output/paraiso/paraiso-peru-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        scrapper = api.ScrapperOfApi(url=url, headers_csv=csv_paraiso_headers, csv_name=file_name, tree_depth=2, parser=ParserParaiso(), threads=4,)
        scrapper.execute()

    printer.stop_loader()
