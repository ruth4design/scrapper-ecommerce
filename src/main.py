import argparse
from paraiso.main import ParaisoScrapper
from ripley.main import RipleyScrapper
from utils import ColorPrint, Color

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ripley', action='store_true', help='Use the Ripley scrapper')
    parser.add_argument('--paraiso', action='store_true', help='Use the Paraiso scrapper')
    args = parser.parse_args()

    printer = ColorPrint()

    if args.ripley:
        printer.start_loader(text="Searching for data Ripley ", color=Color.GREEN)
        ripley_scrapper = RipleyScrapper(url='https://simple.ripley.com.pe/')
        data = ripley_scrapper.get_data()
    if args.paraiso:
        printer.start_loader(text="Searching for data Paraiso ", color=Color.GREEN)
        paraiso_scrapper = ParaisoScrapper(url='https://www.paraiso-peru.com/', timer_for_scroll=10.5, threads_for_navbar=1, threads_for_product=5)
        data = paraiso_scrapper.get_data()

    printer.stop_loader()
