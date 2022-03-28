import numpy as np
from PIL import Image, ImageDraw
from datasetinsights.datasets.synthetic import read_bounding_box_2d, read_bounding_box_3d
from datasetinsights.io.bbox import BBox3D, BBox2D
from datasetinsights.stats.visualization.plots import plot_bboxes, plot_bboxes3d, plot_keypoints
from pyquaternion import Quaternion


def draw_legacy_image_with_boxes(
    image,
    index,
    catalog,
    label_mappings,
):
    cap = catalog.iloc[index]
    ann = cap["annotation.values"]
    capture = image
    image = capture.convert("RGB")  # Remove alpha channel
    bboxes = read_bounding_box_2d(ann, label_mappings)
    return plot_bboxes(image, bboxes, label_mappings)


def draw_solo_image_with_boxes(
        image,
        bbox_data,
        label_mappings,
):
    img = image.convert("RGB")  # Remove alpha channel
    bboxes = to_db_insights_bbox2d(bbox_data)
    return plot_bboxes(img, bboxes, label_mappings)


def draw_image_with_segmentation(
        image: Image,
        segmentation: Image,
):
    """
    Draws an image in streamlit with labels and bounding boxes.

    :param image: the PIL image
    :type PIL:
    :param height: height of the image
    :type int:
    :param width: width of the image
    :type int:
    :param segmentation: Segmentation Image
    :type PIL:
    :param header: Image header
    :type str:
    :param description: Image description
    :type str:
    """
    # image_draw = ImageDraw(segmentation)
    rgba = np.array(segmentation.copy().convert("RGBA"))
    r, g, b, a = rgba.T
    black_areas = (r == 0) & (b == 0) & (g == 0) & (a == 255)
    other_areas = (r != 0) | (b != 0) | (g != 0)
    rgba[..., 0:4][black_areas.T] = (0, 0, 0, 0)
    rgba[..., -1][other_areas.T] = int(0.6 * 255)

    foreground = Image.fromarray(rgba)
    image = image.copy()
    image.paste(foreground, (0, 0), foreground)
    return image


def find_metadata_annotation_index(dataset, name):
    for idx, annotation in enumerate(dataset.metadata.annotations):
        if annotation["name"] == name:
            return idx

def draw_legacy_image_with_keypoints(
    image, annotations, templates
):
    return plot_keypoints(image, annotations, templates)

def draw_image_with_keypoints(
    image, annotations, templates
):
    return plot_keypoints_with_color(image, annotations, templates)


def plot_keypoints_with_color(image, annotations, template, visual_width=6):
    draw = ImageDraw.Draw(image)

    for figure in annotations['values']:
        draw_keypoints_for_figure(image, figure, draw, template, visual_width)

    return image


def draw_keypoints_for_figure(image, figure, draw, template, visual_width=6):
    # load the spec
    if 'skeleton' in template:
        skeleton = template["skeleton"]

        for bone in skeleton:
            j1 = figure["keypoints"][bone["joint1"]]
            j2 = figure["keypoints"][bone["joint2"]]

            if 'state' in j1 and j1['state'] == 2 and 'state' in j2 and j2['state'] == 2:
                x1 = int(j1['location'][0])
                y1 = int(j1['location'][1])
                x2 = int(j2['location'][0])
                y2 = int(j2['location'][1])

                color = _get_color_for_bone(bone)
                draw.line((x1, y1, x2, y2), fill=color, width=visual_width)

    for k in figure["keypoints"]:
        if 'state' in k and k['state'] == 2:
            x = k['location'][0]
            y = k['location'][1]

            color = _get_color_for_keypoint(template, k)

            half_width = visual_width / 2

            draw.ellipse(
                (
                    x - half_width,
                    y - half_width,
                    x + half_width,
                    y + half_width,
                ),
                fill=color,
                outline=color,
            )

    return image

def _get_color_for_bone(bone):
    """ Gets the color for the bone from the template. A bone is a visual
        connection between two keypoints in the keypoint list of the figure.

        bone
        {
            joint1: <int> Index into the keypoint list for the first joint.
            joint2: <int> Index into the keypoint list for the second joint.
            color {
                r: <float> Value (0..1) of the red channel.
                g: <float> Value (0..1) of the green channel.
                b: <float> Value (0..1) of the blue channel.
                a: <float> Value (0..1) of the alpha channel.
            }
        }

    Args:
        bone: The active bone.

    Returns: The color of the bone.

    """
    if "color" in bone:
        return _get_color_from_color_node(bone["color"])
    else:
        return 255, 0, 255, 255

def _get_color_for_keypoint(template, keypoint):
    """ Gets the color for the keypoint from the template. A keypoint is a
        location of interest inside of a figure. Keypoints are connected
        together with bones. The configuration of keypoint locations and bone
        connections are defined in a template file.

    keypoint_template {
        template_id: <str> The UUID of the template.
        template_name: <str> Human readable name of the template.
        key_points [ <List> List of joints defined in this template
            {
                label: <str> The label of the joint.
                index: <int> The index of the joint.
                color {
                    r: <float> Value (0..1) for the red channel.
                    g: <float> Value (0..1) for the green channel.
                    b: <float> Value (0..1) for the blue channel.
                    a: <float> Value (0..1) for the alpha channel.
                }
            }, ...
        ]
        skeleton [ <List> List of skeletal connections
            {
                joint1: <int> The first joint of the connection.
                joint2: <int> The second joint of the connection.
                color {
                    r: <float> Value (0..1) for the red channel.
                    g: <float> Value (0..1) for the green channel.
                    b: <float> Value (0..1) for the blue channel.
                    a: <float> Value (0..1) for the alpha channel.
                }
            }, ...
        ]
    }

    Args:
        template: The active template.
        keypoint: The active keypoint.

    Returns: The color for the keypoint.

    """
    if not 'index' in keypoint:
        return 0, 0, 255, 255

    node = template["keypoints"][keypoint["index"]]

    if "color" in node:
        return _get_color_from_color_node(node["color"])
    else:
        return 0, 0, 255, 255

def _get_color_from_color_node(color):
    """ Gets the color from the color node in the template.

    Args:
        color (tuple): The color's channel values expressed in a range from 0..1

    Returns: The color for the node.

    """
    r = color[0]
    g = color[1]
    b = color[2]
    a = color[3]
    return r, g, b, a

def to_db_insights_bbox3d(boxes):
    bboxes = []
    for b in boxes['values']:
        trans = b['translation']
        size = b['size']
        r = b['rotation']
        rotation = Quaternion(r[3], r[0], r[1], r[2])
        box = BBox3D(
            translation=(trans[0], trans[1], trans[2]),
            size=(size[0], size[1], size[2]),
            label=b['labelId'],
            sample_token=0,
            score=1,
            rotation=rotation,
        )
        bboxes.append(box)

    return bboxes


def to_db_insights_bbox2d(boxes):
    bboxes = []
    for b in boxes['values']:
        box = BBox2D(
            label=b['labelId'],
            x=b['origin'][0],
            y=b['origin'][1],
            w=b['dimension'][0],
            h=b['dimension'][1],
            score=1,
        )
        bboxes.append(box)

    return bboxes


# TODO Implement colors
def draw_image_with_box_3d(image, sensor, values, colors):
    i = sensor.matrix
    matrix = [
        [i[0], i[1], i[2]],
        [i[3], i[4], i[5]],
        [i[6], i[7], i[8]]
    ]
    projection = np.array(matrix)

    boxes = to_db_insights_bbox3d(values)
    img_with_boxes = plot_bboxes3d(image, boxes, projection, None,
                                   orthographic=(sensor.projection == "Orthographic"))
    return img_with_boxes


def draw_legacy_image_with_box_3d(image, sensor, values, colors):
    if 'camera_intrinsic' in sensor:
        projection = np.array(sensor["camera_intrinsic"])
    else:
        projection = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    boxes = read_bounding_box_3d(values)
    img_with_boxes = plot_bboxes3d(image, boxes, projection, None,
                                   orthographic=(sensor["projection"] == "orthographic"))
    return img_with_boxes