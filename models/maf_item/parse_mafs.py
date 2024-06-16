from bs4 import BeautifulSoup
from .maf_card import MafCard, map_field


def find_ter_types_list(bs_ter_type_tag):
    nested_tags = bs_ter_type_tag.contents

    output = []

    for nested_tag in nested_tags:
        output.append(nested_tag.text)

    return output


import re

two_dim_str_pattern0 = "(\d+)х(\d+)"
two_dim_str_pattern1 = "(\d+)x(\d+)"
three_dim_str_pattern0 = "(\d+)х(\d+)х(\d+)"
three_dim_str_pattern0_0 = "(\d+) х (\d+) х (\d+)"
three_dim_str_pattern0_1 = "(\d+) × (\d+) × (\d+)"
three_dim_str_pattern1 = "(\d+)x(\d+)x(\d+)"
three_dim_str_pattern1_0 = "(\d+) x (\d+) x (\d+)"
circular_size_str_pattern = "(D=)"
circular_with_height_pattern0 = "(D(\d+))x(h(\d+))"
circular_with_height_pattern1 = "(D(\d+))x(H-(\d+))"
circular_with_height_pattern2 = "(D(\d+))x(Н(\d+))"
circular_with_height_pattern2_0 = "(D(\d+))x(H(\d+))"
circular_with_height_pattern3 = "(D(\d+))x(Н-(\d+))"
circular_with_height_pattern3_0 = "(D-(\d+)),(Н-(\d+))"
circular_with_height_pattern3_1 = "(D-(\d+)),(Н-(\d+))"
circular_with_height_pattern4 = "(H(\d+))x(D(\d+))"
circular_with_height_pattern5 = "(Н(\d+))x(D(\d+))"
circular_various_len_pattern0 = "LxHx(\d+)"
width_height_various_len_pattern0 = "Lx(\d+)x(\d+)"


def parse_2dim_x0(input_txt: str):
    return input_txt.split("х")


def parse_2dim_x1(input_txt: str):
    return input_txt.split("x")


def parse_3dim_x0(input_txt: str):
    return input_txt.split("х")


def parse_3dim_x0_0(input_txt: str):
    return input_txt.split(" х ")


def parse_3dim_x0_1(input_txt: str):
    return input_txt.split(" × ")


def parse_3dim_x1(input_txt: str):
    return input_txt.split("x")


def parse_3dim_x1_0(input_txt: str):
    return input_txt.split(" x ")


def parse_circular(input_txt: str):
    diameter = input_txt.split("D=")[1]
    return [diameter, diameter, "0"]


def parce_circular_with_height0(input_txt: str):
    parts = input_txt.split("x")
    diameter = parts[0].split("D")[1]
    height = parts[1].split("h")[1]
    return [diameter, diameter, height]


def parce_circular_with_height1(input_txt: str):
    parts = input_txt.split("x")
    diameter = parts[0].split("D")[1]
    height = parts[1].split("H-")[1]
    return [diameter, diameter, height]


def parce_circular_with_height2(input_txt: str):
    parts = input_txt.split("x")
    diameter = parts[0].split("D")[1]
    height = parts[1].split("Н")[1]
    return [diameter, diameter, height]


def parce_circular_with_height2_0(input_txt: str):
    parts = input_txt.split("x")
    diameter = parts[0].split("D")[1]
    height = parts[1].split("H")[1]
    return [diameter, diameter, height]


def parce_circular_with_height3(input_txt: str):
    parts = input_txt.split("x")
    diameter = parts[0].split("D")[1]
    height = parts[1].split("Н-")[1]
    return [diameter, diameter, height]


def parce_circular_with_height3_0(input_txt: str):
    parts = input_txt.split(",")
    diameter = parts[0].split("D-")[1]
    height = parts[1].split("Н-")[1]
    return [diameter, diameter, height]


def parce_circular_with_height3_1(input_txt: str):
    parts = input_txt.split(",")
    diameter = parts[0].split("D-")[1]
    height = parts[1].split("Н-")[1]
    return [diameter, diameter, height]


def parce_circular_with_height4(input_txt: str):
    parts = input_txt.split("x")
    diameter = parts[1].split("D")[1]
    height = parts[0].split("H")[1]
    return [diameter, diameter, height]


def parce_circular_with_height5(input_txt: str):
    parts = input_txt.split("x")
    diameter = parts[1].split("D")[1]
    height = parts[0].split("Н")[1]
    return [diameter, diameter, height]


def parse_circular_various_len0(input_txt: str):
    parts = input_txt.split("LxHx")
    height = parts[1]
    return ["1", "1", height]


def parse_width_height_var_len(input_txt: str):
    l_w_h = input_txt.split("Lx")
    w_h = l_w_h[1].split("x")
    return ["1", f"{w_h[0]}", f"{w_h[1]}"]


dimensions_parsers = {
    two_dim_str_pattern0: parse_2dim_x0,
    two_dim_str_pattern1: parse_2dim_x1,
    three_dim_str_pattern0: parse_3dim_x0,
    three_dim_str_pattern0_0: parse_3dim_x0_0,
    three_dim_str_pattern0_1: parse_3dim_x0_1,
    three_dim_str_pattern1: parse_3dim_x1,
    circular_size_str_pattern: parse_circular,
    circular_with_height_pattern0: parce_circular_with_height0,
    circular_with_height_pattern1: parce_circular_with_height1,
    circular_with_height_pattern2: parce_circular_with_height2,
    circular_with_height_pattern2_0: parce_circular_with_height2_0,
    circular_with_height_pattern3: parce_circular_with_height3,
    circular_with_height_pattern3_0: parce_circular_with_height3_0,
    circular_with_height_pattern3_1: parce_circular_with_height3_1,
    circular_with_height_pattern4: parce_circular_with_height4,
    circular_with_height_pattern5: parce_circular_with_height5,
    circular_various_len_pattern0: parse_circular_various_len0,
    width_height_various_len_pattern0: parse_width_height_var_len,
}


def parse_dimensions(dim_tag: str):
    input_txt = dim_tag.text.strip()
    input_txt = input_txt.replace('±', "")
    output = ""

    patterns = dimensions_parsers.keys()
    pattern_found = False
    if input_txt == "":
        pattern_found = True
        output = ["0", "0", "0"]
    else:
        for pattern in patterns:
            if re.match(pattern,input_txt):
                pattern_found = True
                output = dimensions_parsers[pattern](input_txt)

    if not pattern_found:
        print(f"unknown dimensions pattern: {input_txt}")

    return input_txt, output


value_transformers = {
    "territorytype": find_ter_types_list,
    "dimensions": parse_dimensions
}


def parse_catalog_from_str(cat_content: str):
    bs_card = BeautifulSoup(cat_content, 'lxml')
    bs_cat_items = bs_card.findAll("catalog")

    parsed_cat_items = {}

    parsed_mafs = []

    for cat_item in bs_cat_items:
        siblings = cat_item.contents
        for tag in siblings:
            if tag.name not in value_transformers.keys():
                map_field(parsed_cat_items, tag.name, tag.text, None)
            if tag.name in value_transformers.keys():
                map_field(parsed_cat_items, tag.name, tag, value_transformers[tag.name])

        if "territoryTypes" not in parsed_cat_items.keys():
            parsed_cat_items["territoryTypes"] = []

        new_maf = MafCard(**parsed_cat_items)

        parsed_mafs.append(new_maf)
        print(f"MAF parsed: {new_maf.name} -- {new_maf.vendor} -- {new_maf.vendorCode} ")

    return parsed_mafs
