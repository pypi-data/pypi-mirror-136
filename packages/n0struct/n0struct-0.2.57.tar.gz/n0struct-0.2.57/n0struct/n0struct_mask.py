import re
# ******************************************************************************
# ******************************************************************************
def mask_number(not_masked_number: str):
    """
    Public function: convert numbers into similar looks letters
    """
    not_masked_number = str(not_masked_number)
    return not_masked_number \
                    .replace("0","o") \
                    .replace("1","i") \
                    .replace("2","Z") \
                    .replace("3","?") \
                    .replace("4","?") \
                    .replace("5","S") \
                    .replace("6","b") \
                    .replace("7","T") \
                    .replace("8","B") \
                    .replace("9","g")
# ******************************************************************************
def unmask_number(masked_number: str):
    """
    Public function: convert letters into similar looks numbers
    """
    return masked_number \
                    .replace("o","0") \
                    .replace("O","0") \
                    .replace("i","1") \
                    .replace("I","1") \
                    .replace("l","1") \
                    .replace("z","2") \
                    .replace("Z","2") \
                    .replace("?","3") \
                    .replace("?","4") \
                    .replace("s","5") \
                    .replace("S","5") \
                    .replace("b","6") \
                    .replace("T","7") \
                    .replace("B","8") \
                    .replace("g","9")
# ******************************************************************************
compiled_regexp_mask_pan = re.compile("(([^0-9]|^)?(000)?[456][0-9]{5})([0-9]{6})([0-9]{4})([^0-9]|$)?")
def mask_pan(buffer: str):
    """
    Public function: mask PANs in buffer
    """
    return compiled_regexp_mask_pan.sub(r"\1******\5\6", buffer)
# ******************************************************************************
# ******************************************************************************
