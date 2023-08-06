from .numeric import Numeric
def num_preprocessing(text):
    """
    :param text (str): raw text you wanna preprocess
    :return: normalize text
    """
    return Numeric(text).remove_num()