import argparse
import os
from headers import csv_paraiso_headers, headers_plaza_vea_csv
from paraiso.main import ParaisoScrapper
from ripley.main import RipleyScrapper
from utils import ColorPrint, Color
from grouper_custom_iteration import main as main_custom
from grouper_vectorized import main as main

from datetime import datetime
from api import ScrapperOfApi
from parser_data import ParserPlazaVea, ParserParaiso

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ripley', action='store_true', help='Use the Ripley scrapper')
    parser.add_argument('--paraiso', action='store_true', help='Use the Paraiso scrapper')
    parser.add_argument('--plazavea', action='store_true', help='Use the Plazavea scrapper')
    parser.add_argument('--group', action='store_true', help='Use the group function')
    args = parser.parse_args()
    printer = ColorPrint()

    if args.group:
        type_of_group = input("""What type of group do you want to use?

custom          [c]
vector          [v]
                :""")
        printer.start_loader(text="Grouping data ", color=Color.GREEN)
        if type_of_group == "custom" or type_of_group == "c":
            main_custom()
        elif type_of_group == "vector" or type_of_group == "v":
            main()
        printer.stop_loader()

    if args.plazavea:
        printer.start_loader(text="Searching for data Plazavea ", color=Color.GREEN)
        
        filename = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),f'../output/plazavea/plaza-vea-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'))
       

        plazavea_scrapper = ScrapperOfApi(headers_csv=headers_plaza_vea_csv, csv_name=filename, threads=2)
    if args.ripley:
        printer.start_loader(text="Getting categories for data Ripley ", color=Color.GREEN)
        ripley_scrapper = RipleyScrapper(url='https://simple.ripley.com.pe/')
        data = ripley_scrapper.get_data(printer=printer)
    if args.paraiso:
        printer.start_loader(text="Searching for data Paraiso ", color=Color.GREEN)
        url = 'https://www.paraiso-peru.com'
        file_name = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),f'../output//paraiso/paraiso-peru-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'))
        scrapper = ScrapperOfApi(url=url, headers_csv=csv_paraiso_headers, csv_name=file_name, tree_depth=2, parser=ParserParaiso(), threads=5)

    printer.stop_loader()
