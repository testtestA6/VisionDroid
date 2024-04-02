from dataclasses import field, dataclass
from typing import Dict, Set

import cmd
import re

import extract_activities

XML_PATH = "./AndroidManifest.xml"
THRESHOLD = 0.8


@dataclass
class Global:
    app_name: str = field(
        default=None, metadata={"desc": "app name"}
    )
    activities: Set[str] = field(
        default_factory=set, metadata={"desc": "activities"}
    )
    priority: Dict = field(
        default_factory=dict, metadata={"desc": "priority"}
    )


def get_global_info(opensource=False):
    global_info = Global()
    global_info.app_name = cmd.PACKAGE
    # Activity
    ret = cmd.execute_adb_cmd("dumpsys activity activities | grep mControlTarget=Window")
    results = [i for i in re.findall(r"/(.+?)}", ret)]
    for act in results:
      global_info.activities.add(act)
    # clear duplicated elements
    global_info.activities = list(set(global_info.activities))
    if opensource:
        # Activity
        global_info.activities = extract_activities.get_all_activities(XML_PATH)
        # priority
        for act in global_info.activities:
            global_info.priority[act] = "1"
    return global_info


@dataclass
class Page:
    activity_name: str = field(
        default=None,
        metadata={"desc": "activity"}
    )
    layouts: dict = field(
        default_factory=dict,
        metadata={"desc": "widget"}
    )
    visit_times: int = field(
        default=1,
        metadata={"desc": "visit"}
    )
    is_first_page: bool = field(
        default=False,
        metadata={"desc": "first page"}
    )

    def visit(self):
        self.visit_times += 1

    @staticmethod
    def sim_ratio(page1, page2):
        if page1.activity_name != page2.activity_name:
            return 0.0
        else:
            sim = 0.0
            times = 0
            for key in page1.layouts:
                times += 1
                widget1 = page1.layouts[key]
                if key not in page2.layouts:
                    continue
                widget2 = page2.layouts[key]
                sim += Widget.sim_ratio(widget1, widget2)
            for key in page2.layouts:
                times += 1
                widget2 = page2.layouts[key]
                if key not in page1.layouts:
                    continue
                widget1 = page1.layouts[key]
                sim += Widget.sim_ratio(widget1, widget2)
            if times == 0:
                return 0
            return sim / times


all_pages = []


def page_db_fetch(page_info):
    for page in all_pages:
        if Page.sim_ratio(page_info, page) > THRESHOLD:
            page.visit()
            page.layouts = page_info.layouts
            return page
    all_pages.append(page_info)
    return page_info


def get_page_info(global_info, prev_page_info):
    if global_info is None:
        return None
    page_info = Page()
    ret = cmd.execute_adb_cmd("dumpsys activity activities | grep mControlTarget=Window")
    results = [i for i in re.findall(r"/(.+?)}", ret)]
    if len(results) == 0:
        page_info.activity_name = prev_page_info.activity_name
    else:
        page_info.activity_name = results[0]
    if prev_page_info is None:
        page_info.is_first_page = True
    info_nodes = cmd.get_key_nodes()
    all_desc = set()
    for i in info_nodes:
        if i["@desc"] in all_desc:
            continue
        all_desc.add(i["@desc"])

        widget_info = Widget()
        widget_info.widget_id = i["@desc"]
        widget_info.widget_type = i["@class"].split()[-1]
        if i["@clickable"] == "true":
            widget_info.widget_act = "click"
        elif i["@editable"] == "true":
            widget_info.widget_act = "edit"
        widget_info.node = i
        page_info.layouts[widget_info.widget_id] = widget_info
    return page_info


@dataclass
class Widget:
    widget_type: str = field(
        default=None,
        metadata={"desc": "parent"}
    )
    widget_id: str = field(
        default=None,
        metadata={"desc": "ID"}
    )
    widget_act: str = field(
        default=None,
        metadata={"desc": "action"}
    )
    node: Dict = field(
        default=None,
        metadata={"desc": "root"}
    )

    @staticmethod
    def sim_ratio(widget1, widget2):
        if widget1.widget_id != widget2.widget_id or widget1.widget_type != widget2.widget_type or widget1.widget_act != widget2.widget_act:
            return 0.0
        else:
            return 1.0


if __name__ == '__main__':
    test = get_global_info()
    print(test)