from info import Widget
import cmd


def click(widget: Widget):
    cmd.click_node(widget.node)


def back():
    cmd.execute_adb_cmd("input keyevent 4")


