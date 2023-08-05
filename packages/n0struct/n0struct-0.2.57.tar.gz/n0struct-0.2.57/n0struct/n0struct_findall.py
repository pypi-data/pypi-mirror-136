import typing
from .n0struct_utils import n0isnumeric
from .n0struct_logging import *
# ******************************************************************************
# ******************************************************************************
def findall(current_node: dict, seeked_xpath_str: str, raise_exception = True) -> dict:
    if not isinstance(seeked_xpath_str, str):
        raise TypeError(f"seeked_xpath_str: expected str, got other type: {type(seeked_xpath_str)}{str(seeked_xpath_str)}")
    if seeked_xpath_str.startswith("./"):
        seeked_xpath_str = seeked_xpath_str[2:]
    if seeked_xpath_str.startswith("//"):
        seeked_xpath_str = seeked_xpath_str[2:]
    if seeked_xpath_str.startswith("/"):
        seeked_xpath_str = seeked_xpath_str[1:]
    seeked_xpath_list = [
                        stripped_item
                        for itm in seeked_xpath_str \
                                                    .replace("[", '/[') \
                                                    .replace("//", "/") \
                                                    .split('/')
                        if (stripped_item:=itm.strip())
    ]
    return _findall(current_node, seeked_xpath_list)
# ******************************************************************************
def _findall(
            parent_node: typing.Union[dict, list],
            seeked_xpath_list: list,

            found_xpath_list: list = [],
            parent_nodes_stack: dict = {}, # {found_xpath_list[0]: parent_node^0..found_xpath_list[0..-1]: parent_node^-1}

            raise_exception = True,
            level = 0,
) -> dict:
    """
        returns:
            {
                seeked_xpath_str: node_ptr # if node_ptr is dict/list it's real node, else the final element
            }
    """
    # # n0print("="*80)
    # # n0debug("level")
    # # n0print("="*80)
    # # # n0debug("found_xpath_list")
    # # n0debug_calc("//" + "/".join(found_xpath_list).replace('/[', '['), "found_xpath_list")
    # # n0debug("parent_node")
    # # # n0debug("seeked_xpath_list")
    # # n0debug_calc("/".join(seeked_xpath_list).replace('/[', '['), "seeked_xpath_list")
    # # n0debug("parent_nodes_stack")
    # # n0print("-"*80)

    if not seeked_xpath_list:
        # # n0print("*"*30 + f" FOUND!!! Force surface...")
        # # n0debug_calc("//" + "/".join(found_xpath_list).replace('/[', '['), "found_xpath_list")
        # # n0debug("parent_node")
        return {"//" + "/".join(found_xpath_list).replace('/[', '['): parent_node}
    # **************************************************************************
    # *** Arguments validation
    ##if not isinstance(parent_node, (dict, list)):
    ##    if raise_exception:
    ##        raise TypeError(f"parent_node: expected dict/list, got other type: {type(parent_node)} '{str(parent_node)}'")
    ##    else:
    ##        return None
    if not isinstance(seeked_xpath_list, list):
        if raise_exception:
            raise TypeError(f"seeked_xpath_list: expected list, got other type: {type(seeked_xpath_list)} '{str(seeked_xpath_list)}'")
        else:
            return None
    if not isinstance(found_xpath_list, list):
        if raise_exception:
            raise TypeError(f"found_xpath_list: expected list, got other type: {type(found_xpath_list)} '{str(found_xpath_list)}'")
        else:
            return None
    # **************************************************************************
    # Get child name or index/condition
    # **************************************************************************
    child_name = None
    child_index = None
    if seeked_xpath_list[0].strip() == '..':
        # # n0print("*"*30 + f" Surface...")
        if len(parent_nodes_stack) < 2:
            if raise_exception:
                raise KeyError(f"Imposible to surface from {found_xpath_list+'/'+child_name}")
            else:
                return None
        '''
        # **********************************************************************
        # Surface
        if child_name == "..":
            # ******************************************************************
            # Surface for one level
            n0debug_calc(parent_nodes_stack,         "parent_nodes_stack")
            n0debug_calc(parent_nodes_stack[-1],     "parent_nodes_stack[-1]")

            n0debug_calc(seeked_xpath_list,             "seeked_xpath_list")
            n0debug_calc(seeked_xpath_list[1:],         "seeked_xpath_list[1:]")

            n0debug_calc(found_xpath_list,       "found_xpath_list")
            n0debug_calc(found_xpath_list[-1],   "found_xpath_list[-1]")

            n0debug_calc(parent_nodes_stack,         "parent_nodes_stack")
            n0debug_calc(parent_nodes_stack[:-1],    "parent_nodes_stack[:-1]")

            n0debug_calc(raise_exception,        "raise_exception")

            return _findall(
                            parent_nodes_stack[-1],
                            seeked_xpath_list[1:],
                            found_xpath_list[-1],
                            parent_nodes_stack[:-1],
                            raise_exception,
                            level + 1,
            )
        '''
        # n0debug("parent_nodes_stack")
        del parent_nodes_stack[list(parent_nodes_stack.keys())[-1]]
        # n0debug("parent_nodes_stack")
        # n0debug("found_xpath_list")
        # # n0debug_calc("//" + "/".join(found_xpath_list[:-1]).replace('/[', '['), "found_xpath_list[:-1]")
        # # n0debug_calc(parent_nodes_stack[list(parent_nodes_stack.keys())[-1]], "parent_nodes_stack[list(parent_nodes_stack.keys())[-1]]")
        # # n0debug_calc("/".join(seeked_xpath_list[1:]).replace('/[', '['), "seeked_xpath_list[1:]")
        return _findall(
                        parent_nodes_stack[list(parent_nodes_stack.keys())[-1]],
                        # parent_nodes_stack,
                        seeked_xpath_list[1:],
                        found_xpath_list[:-1],
                        # {**parent_nodes_stack, **{"//" + "/".join(found_xpath_list).replace('/[', '['): parent_node}},
                        parent_nodes_stack,
                        raise_exception,
                        level - 1,
        )
    elif seeked_xpath_list[0].startswith("["):
        # **********************************************************************
        # Index or condition
        if not seeked_xpath_list[0].endswith("]"):
            raise TypeError(f"Index or condition should be inside [], but '{str(seeked_xpath_list[0])}'")
        child_index = seeked_xpath_list[0][1:-1].strip() # Index or xpath condition/function
        if n0isnumeric(child_index):
            # Index
            child_index = int(child_index)
        else:
            # Conditions
            lower_child_index = child_index.lower().replace(' ','')
            # # n0debug("lower_child_index")
            if lower_child_index == '*':
                pass  # will be processed lately
            elif lower_child_index.startswith("last()"):
                after_last = lower_child_index[6:]
                child_index = eval("-1"
                                   + after_last if not any(not ch in "-+01234567890" for ch in after_last) else ""
                )
            elif lower_child_index.startswith("text()"):
                after_text = lower_child_index[6:]
                equal_condition = None
                if after_text.startswith('=='):
                    equal_condition = True
                    condition_separator = '=='
                elif after_text.startswith('='):
                    equal_condition = True
                    condition_separator = '='
                elif after_text.startswith('!='):
                    equal_condition = False
                    condition_separator = '!='
                elif after_text.startswith('<>'):
                    equal_condition = False
                    condition_separator = '<>'
                else:
                    raise TypeError(f"Unknown logic condition [{child_index}] in '{str(seeked_xpath_list[0])}'")
                before_condition,after_condition = child_index.split(condition_separator, 1)
                value_for_condition = after_condition.strip()
                if len(value_for_condition) > 1 and \
                   (
                       (value_for_condition.startswith('"') and value_for_condition.endswith('"'))
                       or
                       (value_for_condition.startswith("'") and value_for_condition.endswith("'"))
                   ):
                    value_for_condition = value_for_condition[1:-1]
                if (parent_node.lower() == value_for_condition.lower()) != equal_condition:
                    # # n0print(f"CONDITION FAILED: {child_index}: {parent_node} {'==' if equal_condition else '!='} {value_for_condition}")
                    return None
                else:
                    # # n0print("*"*30 + f" Deep after condition [{child_index}]...")
                    found_xpath_list[-1] += seeked_xpath_list[0]
                    return _findall(
                                    parent_node,
                                    seeked_xpath_list[1:],
                                    # found_xpath_list[-1] + seeked_xpath_list[0:1],
                                    found_xpath_list,
                                    {**parent_nodes_stack, **{"//" + "/".join(found_xpath_list).replace('/[', '['): parent_node}},
                                    raise_exception,
                                    level + 1,
                    )
            else:
                raise TypeError(f"Unknown condition [{child_index}] in '{str(seeked_xpath_list[0])}'")
    else:
        child_name = seeked_xpath_list[0]
        # # n0debug("child_name")
        # # n0debug("parent_node")
    # **************************************************************************
    if isinstance(parent_node, list):
        # **********************************************************************
        # If we have NOT got index for the list, so try to check all items in the list
        if child_index is None:
            # n0print("*"*30 + " NOT TESTED #0...")
            # n0debug("parent_node")
            # __seeked_xpath_list = "/".join(["[*]"] + seeked_xpath_list)
            # n0print("FOUND: " + "/".join(found_xpath_list))
            # n0print(f"========================= {level} -> {__seeked_xpath_list}")
            # result = _findall(
                            # parent_node,
                            # ["[*]"] + seeked_xpath_list,
                            # found_xpath_list,
                            # parent_nodes_stack,
                            # raise_exception,
                            # level,
            # )
            # n0print(f"-------------------------")
            # n0debug("result")
            # n0print(f"-------------------------")
            # exit()
            # return result
            return _findall(
                            parent_node,
                            ["[*]"] + seeked_xpath_list,
                            found_xpath_list,
                            parent_nodes_stack,
                            raise_exception,
                            level,
            )
        elif isinstance(child_index, int):
            if child_index >= len(parent_node) or (child_index < 0 and -child_index > len(parent_node)):
                if raise_exception:
                    raise IndexError(f"Index {child_index} is out of range {len(parent_node)} at '{'//' + '/'.join(found_xpath_list).replace('/[', '[')}'")
                else:
                    return None
            child_node = parent_node[child_index]
            if isinstance(child_node, (dict, list)):
                n0print("*"*30 + " NOT TESTED #1...")
                found_xpath_list[-1] += f"[{child_index}]"
                return _findall(
                                child_node,
                                seeked_xpath_list[1:],
                                # found_xpath_list + seeked_xpath_list[0:1],
                                # found_xpath_list + [f"[{child_index}]"],
                                found_xpath_list,
                                # parent_nodes_stack + [(found_xpath_list, parent_node)],
                                {**parent_nodes_stack, **{"//" + "/".join(found_xpath_list).replace('/[', '['): parent_node}},
                                raise_exception,
                                level + 1,
                )
            else:
                if raise_exception:
                    raise IndexError(f"Child under {'//' + '/'.join(found_xpath_list).replace('/[', '[')}[{child_index}] is {type(child_node)}'{child_node}', but expected dict/list")
                else:
                    return None
        elif isinstance(child_index, str) and child_index == '*':
            # # n0print("*"*30 + " Multiple deep to each index [*]...")
            multi_found = {}
            last_xpath = found_xpath_list[-1]
            for child_index, child_node in enumerate(parent_node):
                if isinstance(child_node, (dict, list)):
                    # # n0print("*"*25 + f" Multiple deep to index [{child_index}]...")
                    found_xpath_list[-1] = last_xpath + f"[{child_index}]"
                    found = _findall(
                                    # child_node,
                                    __parent_node := parent_node[child_index],
                                    __seeked_xpth := seeked_xpath_list[1:],
                                    # found_xpath_list + [f"[{child_index}]"],
                                    __found_xpath := found_xpath_list,
                                    # parent_nodes_stack + [(found_xpath_list, parent_node)],
                                    __parent_stck := {**parent_nodes_stack, **{"//" + "/".join(found_xpath_list).replace('/[', '['): parent_node}},
                                    raise_exception,
                                    level,
                    )
                    # n0debug("__parent_node")
                    # n0print("seeked_xpath_list:" + "/".join(__seeked_xpth))
                    # n0print("found_xpath_list:" + "/".join(__found_xpath))
                    # n0debug("__parent_stck")
                    # n0debug("found")
                    if found:
                        multi_found.update(found)
                else:
                    if raise_exception:
                        raise IndexError(f"Child under {'//' + '/'.join(found_xpath_list).replace('/[', '[')}[{child_index}] is {type(child_node)}'{child_node}', but expected dict/list")
                    else:
                        return None
            return multi_found
        else:
            raise NotImplementedError(f"Not implemented xpath language: '{seeked_xpath_list[0]}'") # xpath parser will implemented in the next version
    # **************************************************************************
    # parent_node[child_name]
    elif isinstance(parent_node, dict):
        # **********************************************************************
        # Just to be sure that for dict we have name of subnode and no index
        if child_index:
            if raise_exception:
                raise IndexError(f"Index {child_index} could not be uplied to {type(parent_node)} at '{found_xpath_list}'")
            else:
                return None
        if not child_name:
            if raise_exception:
                raise KeyError(f"Subnode {child_node} is not found at '{found_xpath_list}'")
            else:
                return None
        # **********************************************************************
        # Find any
        if child_name == '*':
            multi_found = {}
            # ******************************************************************
            # just skip * and check if the current node is satisfied to the xpath/conditions
            n0print("*"*30 + " NOT TESTED #2...")
            found = _findall(
                            parent_node,
                            seeked_xpath_list[1:],
                            found_xpath_list,
                            parent_nodes_stack,
                            raise_exception,
                            level + 1,
            )
            if found:
                multi_found.update(found)
            # ******************************************************************
            # and just after check recursively all branches below
            for child_name in parent_node: # checking * sub-nodes
                child_node = parent_node[child_name]
                if isinstance(child_node, (dict, list)):
                    n0print("*"*30 + " NOT TESTED #3...")
                    found = _findall(
                                    child_node,
                                    seeked_xpath_list,
                                    # found_xpath_list + [child_name],
                                    found_xpath_list + seeked_xpath_list[0:1],
                                    # parent_nodes_stack + [(found_xpath_list, parent_node)],
                                    {**parent_nodes_stack, **{"//" + "/".join(found_xpath_list).replace('/[', '['): parent_node}},
                                    raise_exception,
                                    level + 1,
                    )
                    if found:
                        multi_found.update(found)
            return multi_found
        # **********************************************************************
        # Find by exact xpath
        if child_name in parent_node:
            # # n0print("*"*30 + f" Deep to dict key [{child_name}]...")
            return _findall(
                            parent_node[child_name],
                            seeked_xpath_list[1:],
                            # found_xpath_list + [child_name],
                            found_xpath_list + seeked_xpath_list[0:1],
                            {**parent_nodes_stack, **{"//" + "/".join(found_xpath_list).replace('/[', '['): parent_node}},
                            raise_exception,
                            level + 1,
            )
        else:
            return None
    # **************************************************************************
    else:
        n0print("="*80)
        n0debug("level")
        n0print("="*80)
        # n0debug("found_xpath_list")
        n0debug_calc("//" + "/".join(found_xpath_list).replace('/[', '['), "found_xpath_list")
        n0debug("parent_node")
        # n0debug("seeked_xpath_list")
        n0debug_calc("/".join(seeked_xpath_list).replace('/[', '['), "seeked_xpath_list")
        # n0debug("parent_nodes_stack")
        n0print("-"*80)
        raise KeyError(f"Internal error:: looking for {seeked_xpath_list} already found: {found_xpath_list} in {type(parent_node)}'{str(parent_node)}'")
# ******************************************************************************
# ******************************************************************************
