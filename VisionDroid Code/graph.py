import os
import cv2
from cmd import execute_adb_cmd, get_bounds
import uiautomator2 as u2

screenshot_dir = 'screenshot'
page_hierarchy_dir = 'page'
os.makedirs(screenshot_dir, exist_ok=True)


def clear_directories():
    directories = ['screenshot', 'page']
    files = ['path.txt']

    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)

    for file in files:
        if os.path.exists(file):
            os.remove(file)

    os.makedirs(screenshot_dir, exist_ok=True)
    os.makedirs(page_hierarchy_dir, exist_ok=True)


def save_path(page_info, action_cnt, selected_widget=None):
    path_file = None
    try:
        path_file = open("path.txt", "a+", errors='ignore')
        path_file.write(f" {page_info.activity_name}({action_cnt}) ")
        if selected_widget is None:
            path_file.write(f" -> BACK\n")
        else:
            path_file.write(f" -> {selected_widget.widget_id}\n")
    finally:
        if path_file is not None:
            path_file.close()


def save_screenshot(action_cnt, widget):
    path = screenshot_dir + "/" + action_cnt + ".jpg"
    execute_adb_cmd("/system/bin/screencap -p /sdcard/screenshot.png")
    cmd = f"adb pull /sdcard/screenshot.png {path}"
    os.system(cmd)

    # widget
    if widget is not None:
        image = cv2.imread(f"{path}")
        pos_x_start, pos_y_start, pos_x_end, pos_y_end = get_bounds(widget.node['@bounds'])
        cv2.rectangle(image, (pos_x_start, pos_y_start), (pos_x_end, pos_y_end), (0, 0, 255), 4)
        cv2.imwrite(f"{path}", image)


def save_page_hierarchy(action_cnt):
    path = page_hierarchy_dir + "/" + action_cnt + ".xml"
    d = u2.connect()
    with open(path, 'w', encoding='utf-8') as hierarchy_file:
        page_source = d.dump_hierarchy(compressed=True, pretty=True)
        hierarchy_file.write(page_source)
