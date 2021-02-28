
import numpy as np
import os, base64, shutil, csv, json


def rm_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)


def rm_tree(folder_name):
    shutil.rmtree(folder_name, True)
    os.mkdir(folder_name)


def img_encode_b64(img_name):
    img_file = open(img_name, 'rb')
    img_b64_data = base64.b64encode(img_file.read()).decode('UTF-8')
    return img_b64_data


def img_decode_b64(img_date, img_name):
    img_out = open(img_name, 'wb')
    img_out.write(img_date.decode('base64'))
    img_out.close()


def write_text(filename, text):
    file1 = open(filename, 'w')
    file1.write(text)
    file1.close()


def append_text(filename, text):
    file1 = open(filename, 'a')
    file1.write(text)
    file1.close()


def read_text(filename):
    file1 = open(filename, 'r')
    text = file1.read()
    file1.close()

    return text


def get_file_list(root_dir):
    path_list = []
    file_list = []
    join_list = []
    for path, _, files in os.walk(root_dir):
        for name in files:
            path_list.append(path)
            file_list.append(name)
            join_list.append(os.path.join(path, name))

    return path_list, file_list, join_list


def load_csv(filename):
    """
        load the csv data and return it.
    """
    if not os.path.isfile(filename):
        return []

    file_csv = open(filename, 'r')
    reader = csv.reader(file_csv)
    data_csv = []
    for row_data in reader:
        data_csv.append(row_data)

    file_csv.close()
    return data_csv


def save_csv(filename, data):
    """
        save the "data" to filename as csv format.
    """
    file_out = open(filename, 'wb')
    writer = csv.writer(file_out)
    writer.writerows(data)
    file_out.close()


def append_csv(filename, data):
    file_out = open(filename, 'a')
    writer = csv.writer(file_out)
    writer.writerows(data)
    file_out.close()


def get_distance_rect(rect1, rect2):
    cx1 = int((rect1[2] + rect1[0]) / 2)
    cy1 = int((rect1[3] + rect1[1]) / 2)
    cx2 = int((rect2[2] + rect2[0]) / 2)
    cy2 = int((rect2[3] + rect2[1]) / 2)
    d = (cx2 - cx1) ** 2 + (cy2 - cy1) ** 2

    return np.sqrt(d)


def read_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)

    return data


def write_json(filename, data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def calc_overlap_area(rect1, rect2):
    dx = min(rect1[2], rect2[2]) - max(rect1[0], rect2[0])
    dy = min(rect1[3], rect2[3]) - max(rect1[1], rect2[1])
    if (dx >= 0) and (dy >= 0):
        return dx * dy
    else:
        return 0


def check_overlap_rect(rect1, rect2):
    # calculate the area of each rects and their overlap
    area1 = (rect1[2] - rect1[0]) * (rect1[3] - rect1[1])
    area2 = (rect2[2] - rect2[0]) * (rect2[3] - rect2[1])
    area_overlap = calc_overlap_area(rect1, rect2)

    # decide 2 rects are 80% overlap or not
    if area_overlap / area1 > 0.6 or area_overlap / area2 > 0.6:
        return True
    else:
        return False
