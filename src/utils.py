import csv
import time
import threading
from enum import Enum

import os

class CreateCSV:
    def __init__(self, filename, headers):

        # create directory if not exists
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:
                error = f"Error creating directory: {exc}"
                print(error)

        self.file = open(filename, "w", newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=headers)
        self.writer.writeheader()

    def write(self, row):
        self.writer.writerow(row)
        self.file.flush()  # Manually flush the buffer after each write

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()



#  example to use CreateCSV
# csv_headers = ['name', 'imagePreview', 'details', 'price']
# csv_file = CreateCSV('data.csv', csv_headers)
# for item in data:
#     csv_file.write(item)
# csv_file.close()
        


def purify_str(text, replace_char=','):
    return text.replace('\n', replace_char).replace('\r', replace_char).replace('\t', replace_char).strip(
        replace_char)


class Color(Enum):
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    RESET = "reset"
    VIOLET = "violet"

class ColorPrint:
    COLORS = {
        Color.BLACK: "\033[30m",
        Color.RED: "\033[31m",
        Color.GREEN: "\033[32m",
        Color.RESET: "\033[0m",
        Color.VIOLET: "\033[35m"
    }

    @staticmethod
    def print(text: str, color: Color=Color.GREEN) -> None:
        if color not in ColorPrint.COLORS:
            print(text)
        else:
            print(f"{ColorPrint.COLORS[color]}{text}{ColorPrint.COLORS[Color.RESET]}")

    def __animate_loader(self, text: str, color: Color) -> None:
        loader_chars = "|/-\\"
        idx = 0
        print_end = "\r"

        color_code = ColorPrint.COLORS.get(color, "")
        reset_code = ColorPrint.COLORS[Color.RESET]

        while self.loading:
            print(f"{color_code}{text} {loader_chars[idx % len(loader_chars)]}{reset_code}", end=print_end)
            time.sleep(0.1)
            idx += 1
        print(f"{color_code}{text} done{reset_code}", end="\n")

    def __init__(self):
        self.loading = False
        self.thread = None

    def start_loader(self, text: str, color: Color) -> None:
        self.loading = True
        self.thread = threading.Thread(target=self.__animate_loader, args=(text, color))
        self.thread.start()

    def stop_loader(self) -> None:
        if self.loading:
            self.loading = False
            self.thread.join()



