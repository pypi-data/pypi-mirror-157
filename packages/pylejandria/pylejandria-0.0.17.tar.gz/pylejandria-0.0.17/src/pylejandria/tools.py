"""
the module tools is a collection of functions for variety of things, it
contains functions for printing or simplify repetitive things.
"""

from math import floor, ceil
import os
from typing import Any, Optional
import img2pdf
from tkinter import Tk
from tkinter.filedialog import askopenfilenames, asksaveasfilename

Number = float | int
FILETYPES = {
    'PDF': '*.pdf',
    'JPEG': '*jpg;*.jpeg;*.jpe;*.jfif',
    'PNG': '*png',
    'TIFF': '*.tiff;*.tif'
}


def center(text: str, space: int) -> str:
    """
    secondary function for prettify, it centers the given text and splits the
    space evenly.
    Params:
        text: string to be centered.
        space: quantity of white space to split.
    """
    padding = (space-len(text))/2
    return f'{" "*floor(padding)}{text}{" "*ceil(padding)}'


def filetypes(
    *types: list[str],
    all_files: Optional[bool]=True
) -> list[tuple[str, str]]:
    """
    returns a list with the corresponding file types, is useful for tkinter
    filedialog.
    Params:
        types: all the types to be returned.
        all_files: appends the all files extension *.*.
    """
    result = [(type_, FILETYPES.get(type_)) for type_ in types]
    if all_files is True:
        result.append(('All Files', '*.*'))
    return result


class PrettifyError(Exception):
    """
    Custom Exception for Prettify function.
    """
    pass


class PrettyDictError(Exception):
    """
    Custom Exception for Pretty_dict function.
    """
    pass


class PdfError(Exception):
    """
    Custom Exception for image_to_pdf function.
    """
    pass


def prettify(
        values: list[list[Any]],
        separator: Optional[str]='|',
        padding: Optional[int]=0,
        headers: Optional[bool]=False,
        orientation: Optional[str]='center',
        _print: Optional[bool]=True
) -> str:
    """
    prettify receives as main argument a 2D matrix and returns a string
    to make easier the visualization of data in console, mostly is for
    school projects, if is something more complicated it would be easier
    to use tkinter.

    Params:
        separator: string that separated columns.
        padding: integer of white space to fill each item.
        headers: boolean to indicate if horizontal bar of headings is needed.
        centered: boolean to indiceate if text must be centered.
    """
    separator = " "*padding + separator + " "*padding
    total_rows = len(values)
    total_cols = max([len(row) for row in values])
    string_values = [[str(col) for col in row] for row in values]
    all_values = [row + [""]*(total_cols - len(row)) for row in string_values]
    col_values = [[row[i] for row in all_values] for i in range(total_cols)]
    lengths = [(col, max([len(i) for i in col])) for col in col_values]
    if orientation == 'left':
        padded_values = [
            [row + " "*(length - len(row)) for row in col]
            for col, length in lengths
        ]
    elif orientation == 'right':
        padded_values = [
            [" "*(length - len(row)) + row for row in col]
            for col, length in lengths
        ]
    elif orientation == 'center':
        padded_values = [
            [center(row, length) for row in col]
            for col, length in lengths
        ]
    else:
        raise PrettifyError(
            "invalid orientation. Expected right, left or center."
        )
    row_values = [[col[i] for col in padded_values] for i in range(total_rows)]
    joined_rows = [separator.join(row) for row in row_values]
    if headers:
        joined_rows.insert(1, '-'*len(joined_rows[0]))

    if _print:
        print('\n'.join(joined_rows))
    return '\n'.join(joined_rows)


def pretty_dict(
        dictionary: dict,
        indent: Optional[int]=0,
        tab: Optional[str]=' '*4,
        _print: Optional[bool]=True
) -> str:
    """
    pretty_dict is a function to print dictionaries with indentation, it may be
    helpful for print debugging or console programs.

    Params:
        dictionary: a dict with the info we want to display.
        indent: is a parameter used for the function to print nested dicts.
        tab: is a string to separate levels of indentation, it can be any
             string.
    """
    if not isinstance(dictionary, dict):
        raise PrettyDictError("Argument must be dict type.")
    if not dictionary.items():
        return '{}\n'
    result = tab*indent + '{\n'
    for key, value in dictionary.items():
        result += tab*indent + f'{tab}{key}: '
        if not isinstance(value, dict):
            result += f'{value}\n'
        else:
            result += pretty_dict(value, indent=indent+1)
    if _print:
        print(result + tab*indent + '}\n')
    return result + tab*indent + '}\n'


def image_to_pdf(
    images: list[str], path: str,
    get_path: Optional[bool]=False,
    get_images: Optional[bool]=False,
    remove: Optional[bool]=False
) -> str:
    """
    saves a pdf file with the given images at the given location and returns
    the path, specificated or not. 
    Params:
        images: list of paths of the images.
        path: path where pdf will be saved.
        get_path: bool to open a window to ask path.
        get_images: bool to open a window to select images.
        remove: remove or not the given files.
    """
    if get_path is True:
        Tk().withdraw()
        path = asksaveasfilename(
            filetypes=filetypes('PDF'),
            defaultextension='*.pdf'
        )
        if not path:
            return
    if get_images is True:
        Tk().withdraw()
        images = askopenfilenames(
            filetypes=filetypes('PNG', 'JPEG')
        )
        if not images:
            return
    with open(path, 'wb') as f:
        f.write(img2pdf.convert(images))
    if remove is True:
        for image in images:
            os.remove(image)
    return path


def parse_seconds(seconds: Number, decimals: Optional[int]=0) -> str:
    """
    Simple function to parse seconds to standard form hh:mm:ss.
    Params:
        seconds: number of seconds to represent.
        decimals: number of decimals of seconds.
    """
    h = int(seconds // 3600)
    m = int(seconds // 60)
    s = round(seconds % 60, decimals)
    if decimals < 1:
        s = int(s)
    return f'{0 if h < 10 else ""}{h}:{0 if m < 10 else ""}{m}:{s}'


if __name__ == '__main__':
    image_to_pdf(None, None, True, True)
