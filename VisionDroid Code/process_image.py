from xml.etree import ElementTree as ET
import numpy as np
from matplotlib import pyplot as plt
import cv2
import re

# Function to recursively extract bounds of enabled elements
def extract_enabled_bounds(node, f_click=False):
    bounds = []
    # Check if the node is enabled
    if node.attrib.get('clickable') == 'true':
        # Extract the 'bounds' attribute
        if len(node) == 1:
            bound = node[0].attrib.get('bounds')
            if bound:
                bounds.append(bound)
        else:
            bound = node.attrib.get('bounds')
            if bound:
                bounds.append(bound)
        
    
    # Recursively check for any child nodes
    for child in node:
        bounds.extend(extract_enabled_bounds(child, f_click))
    
    return bounds

def sortBounds(bounds):
    sorted_data = sorted(bounds, key=lambda x: (x[1], x[0])) 

    return sorted_data

# Function to draw rectangles on the image based on the bounds
def draw_bounds(image, bounds_list):
    num = 0
    last_y = -1
    for coords in bounds_list:
        num += 1
        # Extracting the coordinates from the bounds string
        # coords = list(map(int, re.findall(r'\d+', bound_str)))
        # Since coords are in the form [x1,y1,x2,y2], we unpack them
        x1, y1, x2, y2 = coords
        # Draw a rectangle on the image
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Blue color
        
        if y1 != last_y:
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            font_color = (255, 0, 0)  # Green color
            cv2.putText(image, str(num), (x1, y1 + 30), font, font_scale, font_color, 2)
        last_y = y1

    return image

def calculate_area(box):
    # bound
    return (box[2] - box[0]) * (box[3] - box[1])

def is_fully_overlapped(box1, box2):
    #  box1 and box2 
    return ((box1[0] <= box2[0] and box1[1] <= box2[1] and box1[2] >= box2[2] and box1[3] >= box2[3]) or
            (box2[0] <= box1[0] and box2[1] <= box1[1] and box2[2] >= box1[2] and box2[3] >= box1[3]))

def calculate_overlap_area(box1, box2):
    # overlap
    overlap_width = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
    overlap_height = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
    return overlap_width * overlap_height

def is_large_overlap(box1, box2, threshold=0.3):
    # overlap
    overlap_area = calculate_overlap_area(box1, box2)
    area1 = calculate_area(box1)
    area2 = calculate_area(box2)

    # area
    return overlap_area > threshold * area1 or overlap_area > threshold * area2

def remove_larger_overlap(boxes):
    i = 0
    while i < len(boxes):
        removed = False
        for j in range(i + 1, len(boxes)):
            if is_fully_overlapped(boxes[i], boxes[j]):
            # if is_overlap(boxes[i], boxes[j]):
                # overlap
                if calculate_area(boxes[i]) > calculate_area(boxes[j]):
                    del boxes[i]
                else:
                    del boxes[j]
                removed = True
                break  # delete
        if not removed:
            i += 1  # move
    return boxes
    
def shift_box(box, dx, dy):
    # bound
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]

def resolve_overlap(boxes):
    for i in range(len(boxes)):
        for j in range(len(boxes)):
            if i != j and is_large_overlap(boxes[i], boxes[j]) and is_fully_overlapped(boxes[i], boxes[j]) == False:
                # print('OOOKKKK')
                # print('box i', boxes[i])
                # print('box j', boxes[j])
                # bound
                # right
                if boxes[i][0] < boxes[j][0] or boxes[i][1] < boxes[j][1]:
                    # boxes[j] 
                    shift_x = max(0, boxes[i][2] - boxes[j][0])
                    shift_y = max(0, boxes[i][3] - boxes[j][1])
                    # boxes[j] = shift_box(boxes[j], shift_x, shift_y)
                    boxes[j] = shift_box(boxes[j], 0, shift_y)
                else:
                    # boxes[i] 
                    shift_x = max(0, boxes[j][2] - boxes[i][0])
                    shift_y = max(0, boxes[j][3] - boxes[i][1])
                    # boxes[i] = shift_box(boxes[i], shift_x, shift_y)
                    boxes[i] = shift_box(boxes[i], 0, shift_y)
                # print('box i', boxes[i])
                # print('box j', boxes[j])
    return boxes

for i in range(6):
    # Parse the XML content
    print('Num: ', i + 1)
    tree = ET.parse(f"Scene_1/hierarchy_files/{i+1}.xml")
    root = tree.getroot()

    # Extracting bounds from the root node
    enabled_bounds = extract_enabled_bounds(root)
    bounds = []
    for bound_str in enabled_bounds:
        coords = list(map(int, re.findall(r'\d+', bound_str)))
            # Since coords are in the form [x1,y1,x2,y2], we unpack them
        # x1, y1, x2, y2 = coords
        bounds.append(coords)
    print(len(bounds))
    # print(bounds) # Displaying the first 10 for brevity

    # enabled_bounds = remove_larger_overlap(bounds)
    enabled_bounds = bounds
    enabled_bounds = sortBounds(enabled_bounds)
    print(enabled_bounds)
    
    t = len(enabled_bounds)
    for m in range(t):
        # print('m: ', m)
        if enabled_bounds[0][0] == 0 and enabled_bounds[0][1] == 0:
            enabled_bounds = enabled_bounds[1:]
        else:
            break
    print(enabled_bounds)

    enabled_bounds = resolve_overlap(enabled_bounds)

    # print(enabled_bounds)

    # Load the image
    image_path = f'Scene_1/screenshots/{i+1}.jpg'
    image = cv2.imread(image_path)

    # Drawing the bounds on the image
    image_with_bounds = draw_bounds(image, enabled_bounds)

    # Save the image with drawn bounds
    output_path = f'Scene_1/annotated_image/{i+1}.jpg'
    cv2.imwrite(output_path, image_with_bounds)

    print('ok!')
