from typing import Union

from unit_parse.config import Quantity
from unit_parse.pre_processing_substitution import remove_strings, substitution
from unit_parse.pre_processing_multiple import multiple_quantities_main
from unit_parse.core import text_list_to_quantity
from unit_parse.post_processing import remove_duplicates
from unit_parse.utils import remove_empty_cells
from unit_parse.logger import logger


def parser(text_in: str, remove_string: list[str] = None) -> Union[Quantity, list[Quantity], list[list[Quantity]]]:
    """ parser

    Main function to call to do parsing.

    Parameters
    ----------
    text_in: str
        text you want to be parsed
    remove_string: list[str
        string that will just be deleted from text_in

    Returns
    -------
    output: Quantity, list[Quantity], list[list[Quantity]]

    """
    logger.info(f"INPUT: {text_in}")
    # type check
    if not isinstance(text_in, str):
        raise TypeError(f"'text_in' must be a string. Given {text_in} (type: {type(text_in)}")
    if remove_string is not None:
        if isinstance(remove_string, str):
            remove_string = [remove_string]
        if not isinstance(remove_string, list) and isinstance(remove_string[0], str):
            raise TypeError(f"'remove_string' must be a str, or list[str]. Given {remove_string} (type:"
                            f" {type(remove_string)})")

    # pre-processing
    if remove_string is not None:
        text_in = remove_strings(text_in, remove_string)
    text_in = substitution(text_in)
    text_list = multiple_quantities_main(text_in)

    # text to unit
    out = text_list_to_quantity(text_list)

    # post processing
    out = remove_duplicates(out)
    out = remove_empty_cells(out)

    # return unit instead of list if just one
    if isinstance(out, list) and len(out) == 1:
        if not isinstance(out[0], list):
            out = out[0]
        elif isinstance(out[0], list) and len(out[0]) == 1:
            out = out[0][0]

    logger.info(f"OUTPUT: {out}'")
    return out
