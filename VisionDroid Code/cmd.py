import json
import os
import re
import subprocess

import cv2
import uiautomator2 as u2
import xmltodict

PACKAGE = "xxxx"


def layout_to_json():
    d = u2.connect()
    page_source = d.dump_hierarchy(compressed=True, pretty=True)
    data_dict = xmltodict.parse(page_source)
    return data_dict


def _get_desc(node):
    text = node['@text']
    content = node['@content-desc']
    resource_id = node['@resource-id']
    if text != "":
        desc = text
    elif content != "":
        desc = content
    elif resource_id != "":
        desc = resource_id.split('/')[-1]
        desc = desc.replace('_', ' ')
    else:
        desc = ""
    return desc


def _node_check(node, is_farther_clickable):
    # package
    if node['@package'] != PACKAGE:
        return False, False

    # click
    is_clickable = node['@clickable'] == "true" or is_farther_clickable
    if is_clickable:
        node['@clickable'] = "true"
    else:
        node['@clickable'] = "false"

    # fill
    is_editable = ('@class' in node) and (node['@class'] == 'android.widget.EditText' or
                                          node['@class'] == 'android.widget.AutoCompleteTextView')
    if is_editable:
        node['@editable'] = "true"
    else:
        node['@editable'] = "false"

    # desc
    node["@desc"] = _get_desc(node)
    is_described = node["@desc"] != ""
    if not is_described:
        # desc
        return is_clickable, False

    return is_clickable, is_described


def get_nodes(hierarchy):
    info_nodes = []

    def dfs(node, is_farther_clickable=False):
        if 'node' not in node:
            return
        node = node['node']
        if type(node) is dict:
            is_clickable, is_described = _node_check(node, is_farther_clickable)
            if is_described:
                info_nodes.append(node)
            dfs(node, is_farther_clickable or is_clickable)
        else:
            for idx in range(len(node)):
                is_clickable, is_described = _node_check(node[idx], is_farther_clickable)
                if is_described:
                    info_nodes.append(node[idx])
                dfs(node[idx], is_farther_clickable or is_clickable)

    dfs(hierarchy['hierarchy'])
    return info_nodes


def get_key_nodes():
    hierarchy = layout_to_json()
    # with open("dump.test.json", "r") as f:
    #     hierarchy = json.load(f)
    return get_nodes(hierarchy)


def get_bounds(bounds):
    a, b, c, d = [int(i) for i in re.findall(r"(\d+)", bounds)]
    return a, b, c, d


def click_node(target):
    pos_x_start, pos_y_start, pos_x_end, pos_y_end = get_bounds(target['@bounds'])
    cmd = "adb shell input tap {} {}".format(str((pos_x_start + pos_x_end) // 2), str((pos_y_start + pos_y_end) // 2))
    os.system(cmd)


def execute_adb_cmd(cmd):
    return subprocess.getoutput("D:\\Android\\android-sdk\\platform-tools\\adb.exe shell " + cmd)


if __name__ == '__main__':
    k = get_key_nodes()
    pass
