"""
filepath: app code app/src/main/AndroidManifest.xml
function:  xml activities info
"""
import xml.etree.ElementTree as ET


def get_all_activities(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    app = root.find('application')
    activities = []

    for e in app.iter('activity'):
        if e.find('intent-filter') is not None:
            activities.append(e.attrib['{http://schemas.android.com/apk/res/android}name'].split('.')[-1].replace('Activity', ''))
    return activities


if __name__ == '__main__':
    activities = get_all_activities("./AndroidManifest.xml")
    pass
