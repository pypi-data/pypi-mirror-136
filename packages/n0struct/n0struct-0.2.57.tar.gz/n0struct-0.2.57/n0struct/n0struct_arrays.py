import typing
# ******************************************************************************
# ******************************************************************************
def split_pair(
                in_str: str,
                separator: str,
                transform1: callable = lambda x:x,
                transform2: callable = lambda x:x,
                default_element: int = 1
) -> tuple:
    """
    split_pair(in_str: str, separator: str, transform1: callable = lambda x:x, transform2: callable = lambda x:x, default_element: int = 1) -> tuple:

    split string into 2 sub strings in any cases:
        '' by '://'                                     => (None,   None)
        'www.aaa.com' by '://'                          => (None,   'www.aaa.com')
        'https://www.aaa.com' by '://'                  => ('http', 'www.aaa.com')
        'www.aaa.com',default_element = 0 by '/'        => ('www.aaa.com')
        'www.aaa.com/path',default_element = 0 by '/'   => ('www.aaa.com', 'path')
    """
    if not in_str:
        return transform1(None), transform2(None)

    str_parts = in_str.split(separator, 1)
    if len(str_parts) == 1:
        if default_element:
            # second (right) element is default
            return transform1(None), transform2(str_parts[0])
        else:
            # first (left) element is default
            return transform1(str_parts[0]), transform2(None)
    return transform1(str_parts[0]), transform2(str_parts[1])
# ******************************************************************************
def join_triplets(
                    in_list: typing.Union[None, str, tuple, list],
                    level:int = 0
) -> str:
    """
    join_triplets(in_list: typing.Union[None, str, tuple, list], level = 0) -> str:

    join elements with middle sepataror:
        [elem1, separator, elem2]   => elem1, separator, elem2
        [elem1, separator, None]    => elem1
        [None, separator, elem2]    => elem2
    """
    if isinstance(in_list, str) or in_list is None:
        return in_list or ""
    elif not isinstance(in_list, (tuple, list)):
        raise Exception(f"{type(in_list)} '{in_list}' should be None|str|tuple|list")
    elif not len(in_list):
        return ""
    elif len(in_list) > 3:
        raise Exception(f"'{in_list}' should consist not more 3 elements")
    else:
        out_list = []
        for item in in_list:
            out_list.append(join_triplets(item, level+1))

        if len(in_list) == 3:
            if isinstance(in_list[1], str):
                result = out_list[0] +  (out_list[1] if out_list[0] and out_list[2] else "") + out_list[2]
            else:
                if not isinstance(in_list[1], (tuple, list)) or not len(in_list[1]) in (1,2):
                    raise Exception(f"{type(in_list[1])} '{in_list[1]}' is not correct separator")
                if len(in_list[1]) == 2 and not in_list[1][0]:
                    result = out_list[0] +  (out_list[1] if out_list[2] else "") + out_list[2]
                else:
                    result = out_list[0] +  (out_list[1] if out_list[0] else "") + out_list[2]
        else:
            result = "".join(out_list)

        return result
# ******************************************************************************
# ******************************************************************************
