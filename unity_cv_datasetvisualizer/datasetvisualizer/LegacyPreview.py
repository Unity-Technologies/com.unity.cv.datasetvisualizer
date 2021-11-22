import argparse
import json
import os
import sys
import subprocess
from typing import List, Tuple, Optional, Dict
import re

import streamlit as st

import streamlit.components.v1 as components

from datasetinsights.datasets.unity_perception import AnnotationDefinitions, MetricDefinitions
from datasetinsights.datasets.unity_perception.captures import Captures

import helpers.custom_components_setup as cc
from datasetvisualizer.LegacyDataset import Dataset

import helpers.datamaker_dataset_helper as datamaker


def datamaker_dataset(path: str) -> Optional[Dict[int, Dataset]]:
    """ Reads the given path as a datamaker dataset

        Assumes that the given path contains a folder structure as follows:
        - path
            - urn_app_params folders
                - instance_#
                    - attempt_#
                        - Normal Perception dataset folder structure

        :param path: path to dataset
        :type path: str

        :return: Dictionary containing an entry for every instance, the key is the instance number, 
                each entry is a tuple as follows: (AnnotationDefinition, MetricDefiniton, Captures, number of captures, 
                absolute path to instance)
        :rtype: Dict[int, (AnnotationDefinitions, MetricDefinitions, Captures, int, str)]
    """
    instances = {}
    try:
        for app_param in [f.path for f in os.scandir(path) if f.is_dir()]:
            read_datamaker_instance_output(app_param, instances)
    except Exception:
        # The user may be selecting an actual app-param folder instead of a folder containing app-params. This can happen if the user is on the mac and there is only one app-param folder in the downloaded dataset.
        try:
            read_datamaker_instance_output(path, instances)
        except Exception:
            return None

    if len(instances) > 0:
        return instances
    else:
        return None


def read_datamaker_instance_output(path, instances):
    for instance in [g.path for g in os.scandir(path) if g.is_dir()]:
        if re.match(".*instance_[0-9]*", instance):
            instance_num = int(instance[instance.rfind("instance_") + len("instance_"):])
            for attempt in [h.path for h in os.scandir(instance) if h.is_dir()]:
                if re.match(".*attempt_[0-9]*", attempt):
                    ds = Dataset(attempt)
                    if ds.dataset_valid:
                        instances[instance_num] = ds


def create_session_state_data(attribute_values: Dict[str, any]):
    """ Takes a dictionary of attributes to values to create the streamlit session_state object. 
    The values are the default values

    :param attribute_values: dictionary of session_state parameter to default values
    :type attribute_values: Dict[str, any]
    """
    for key in attribute_values:
        if key not in st.session_state:
            st.session_state[key] = attribute_values[key]


def create_sidebar_labeler_menu(available_labelers: List[str]) -> Dict[str, bool]:
    """
    Creates a streamlit sidebar menu that displays checkboxes and radio buttons to select which labelers to display

    :param available_labelers: List of strings representing labelers
    :type available_labelers: List[str]

    :return: Dictionary where keys are the available_labelers and values are bool representing if they have been chosen
    :rtype: Dict[str, bool]
    """

    # Note that here there is use of st.session_state._____existed_last_time this is used to workaround a streamlit bug
    # if this is removed then when user selects dataset with labeler X and turns it on then changes to dataset without
    # it then changes to a dataset with labeler X, labeler X appears as unselected but returns True as a value so acts
    # as if it was selected

    st.sidebar.markdown("# Visualize Labels")
    labelers = {}
    if 'bounding box' in available_labelers:
        labelers['bounding box'] = st.sidebar.checkbox(
            "2D Bounding Boxes") and st.session_state.bbox2d_existed_last_time
        st.session_state.bbox2d_existed_last_time = True
    else:
        st.session_state.bbox2d_existed_last_time = False

    if 'bounding box 3D' in available_labelers:
        labelers['bounding box 3D'] = st.sidebar.checkbox(
            "3D Bounding Boxes") and st.session_state.bbox3d_existed_last_time
        st.session_state.bbox3d_existed_last_time = True
    else:
        st.session_state.bbox3d_existed_last_time = False

    if 'keypoints' in available_labelers:
        labelers['keypoints'] = st.sidebar.checkbox("Key Points") and st.session_state.keypoints_existed_last_time
        st.session_state.keypoints_existed_last_time = True
    else:
        st.session_state.keypoints_existed_last_time = False

    if 'instance segmentation' in available_labelers and 'semantic segmentation' in available_labelers:
        if st.sidebar.checkbox('Segmentation', False) and st.session_state.semantic_existed_last_time:
            selected_segmentation = st.sidebar.radio("Select the segmentation type:",
                                                     ['Semantic Segmentation', 'Instance Segmentation'],
                                                     index=0)
            if selected_segmentation == 'Semantic Segmentation':
                labelers['semantic segmentation'] = True
            elif selected_segmentation == 'Instance Segmentation':
                labelers['instance segmentation'] = True
        st.session_state.semantic_existed_last_time = True
    elif 'semantic segmentation' in available_labelers:
        labelers['semantic segmentation'] = st.sidebar.checkbox("Semantic Segmentation")
        st.session_state.semantic_existed_last_time = False
    elif 'instance segmentation' in available_labelers:
        labelers['instance segmentation'] = st.sidebar.checkbox("Instance Segmentation")
        st.session_state.semantic_existed_last_time = False
    else:
        st.session_state.semantic_existed_last_time = False
    if st.session_state.previous_labelers != labelers:
        st.session_state.labelers_changed = True
    else:
        st.session_state.labelers_changed = False
    st.session_state.previous_labelers = labelers
    return labelers


def display_number_frames(num_frames: int):
    """
    Creates a sidebar display for the number of frames in the selected dataset

    :param num_frames: Number of frames in the selected dataset
    :type num_frames: int
    """
    st.sidebar.markdown("### Number of frames: " + str(num_frames))


def preview_dataset(data_root, folder_name):
    instances = datamaker_dataset(data_root)

    # if it is not a datamaker dataset
    if instances is None:
        # Attempt to read as a normal perception dataset
        ds = Dataset(data_root)
        if not ds.dataset_valid:
            st.warning("The provided Dataset folder \"" + data_root + "\" is not considered valid")

            st.markdown("# Please open a dataset folder:")
            if st.button("Open Dataset", key="second open dataset"):
                folder_select()
            return

        if len(folder_name) >= 1:
            st.sidebar.markdown("# Current dataset:")
            st.sidebar.write(folder_name)

        display_number_frames(ds.length())

        available_labelers = ds.get_available_labelers()
        labelers = create_sidebar_labeler_menu(available_labelers)

        # zoom_image is negative if the application isn't in zoom mode
        index = int(st.session_state.zoom_image)
        if index >= 0:
            zoom(index, 0, ds, labelers)
        else:
            num_rows = 5
            grid_view(num_rows, ds, labelers)

    # if it is a datamaker dataset
    else:
        if len(folder_name) >= 1:
            st.sidebar.markdown("# Current dataset:")
            st.sidebar.write(folder_name)

        display_number_frames(datamaker.get_dataset_length_with_instances(instances))

        # zoom_image is negative if the application isn't in zoom mode
        index = int(st.session_state.zoom_image)
        if index >= 0:
            instance_key = datamaker.get_instance_by_capture_idx(instances, index)

            if (instance_key is None):
                index = 0
                instance_key = datamaker.get_instance_by_capture_idx(instances, index)

            offset = datamaker.get_dataset_length_with_instances(instances, instance_key)
            ds = instances[instance_key]
            ann_def = ds.ann_def
            available_labelers = [a["name"] for a in ann_def.table.to_dict('records')]
            labelers = create_sidebar_labeler_menu(available_labelers)
            zoom(index, offset, ds, labelers)
        else:
            index = st.session_state.start_at
            num_rows = 5
            instance_key = datamaker.get_instance_by_capture_idx(instances, index)

            if (instance_key is None):
                st.session_state.start_at = 0
                index = 0
                instance_key = datamaker.get_instance_by_capture_idx(instances, index)

            ds = instances[instance_key]
            ann_def = ds.ann_def
            available_labelers = [a["name"] for a in ann_def.table.to_dict('records')]
            labelers = create_sidebar_labeler_menu(available_labelers)
            grid_view_instances(num_rows, instances, labelers)


def folder_select():
    """ Runs a subprocess that opens a file dialog to select a new directory, this will update st.session_state.curr_dir
    """
    output = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(os.path.realpath(__file__)), "helpers/folder_explorer.py")],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if str(output.stdout).split("\'")[1] == "" or output.stdout is None:
        return

    stdout = str(os.path.abspath(str(output.stdout).split("\'")[1]))

    if stdout[-4:] == "\\r\\n":
        stdout = stdout[:-4]
    elif stdout[-2:] == '\\n':
        stdout = stdout[:-2]
    proj_root = stdout.replace("\\", "/") + "/"

    st.session_state.curr_dir = proj_root
    st.experimental_rerun()


def create_grid_view_controls(num_rows: int, dataset_size: int) -> Tuple[int, int]:
    """ Creates the controls for grid view

    :param num_rows: number of rows to display
    :type num_rows: int
    :param dataset_size: The size of the dataset
    :type dataset_size: int
    :return: Returns the number of columns and the index at which the grid must start
    :rtype: Tuple[int, int]
    """
    header = st.beta_columns([2 / 3, 1 / 3])

    num_cols = header[1].slider(label="Frames per row: ", min_value=1, max_value=5, step=1,
                                value=int(st.session_state.num_cols))
    if not num_cols == st.session_state.num_cols:
        st.session_state.num_cols = num_cols
        st.experimental_rerun()

    with header[0]:
        new_start_at = int(cc.item_selector(int(st.session_state.start_at), num_cols * num_rows,
                                            dataset_size))
        if not new_start_at == st.session_state.start_at and not st.session_state.just_opened_grid:
            st.session_state.start_at = new_start_at

        st.session_state.just_opened_grid = False
        start_at = int(st.session_state.start_at)

    components.html("""<hr style="height:2px;border:none;color:#AAA;background-color:#AAA;" /> """, height=10)
    return num_cols, start_at


def create_grid_containers(num_rows: int, num_cols: int, start_at: int, dataset_size: int) -> List[any]:
    """ Creates the streamlit containers that will hold the images in a grid, this must happen before placing the images
    so that when clicking on "Expand frame" it doesn't need to reload every image before opening in zoom view

    :param num_rows: Number of rows
    :type num_rows: int
    :param num_cols: Number of columns
    :type num_cols: int
    :param start_at: Index at which the grid starts
    :type start_at: int
    :param dataset_size: Size of the dataset
    :type dataset_size: int
    :return: list of the containers in order from left to right, up to down
    :rtype: List[any]
    """
    cols = st.beta_columns(num_cols)
    containers = [None] * (num_cols * num_rows)
    for i in range(start_at, min(start_at + (num_cols * num_rows), dataset_size)):
        containers[i - start_at] = cols[(i - (start_at % num_cols)) % num_cols].beta_container()
        # container.write("Frame #" + str(i))
        with containers[i - start_at]:
            components.html(
                """<p style="margin-top:35px;margin-bottom:0px;font-family:IBM Plex Sans, sans-serif"></p>""",
                height=35)
        expand_image = containers[i - start_at].button(label="Expand Frame", key="exp" + str(i))
        if expand_image:
            st.session_state.zoom_image = i
            st.session_state.just_opened_zoom = True
            st.experimental_rerun()
    return containers


def grid_view(num_rows: int, ds: Dataset, labelers: Dict[str, bool]):
    """ Creates the grid view streamlit components

    :param num_rows: Number of rows
    :type num_rows: int
    :param ds: Current Dataset
    :type ds: Dataset
    :param labelers: Dictionary containing keys for the name of every labeler available in the given dataset
                     and the corresponding value is a boolean representing whether or not to display it
    :type labelers: Dict[str, bool]
    """
    dataset_size = ds.length()

    num_cols, start_at = create_grid_view_controls(num_rows, dataset_size)

    containers = create_grid_containers(num_rows, num_cols, start_at, dataset_size)

    for i in range(start_at, min(start_at + (num_cols * num_rows), dataset_size)):
        image = ds.get_image_with_labelers(i, labelers, max_size=get_resolution_from_num_cols(num_cols))
        containers[i - start_at].image(image, caption=str(i), use_column_width=True)


def get_resolution_from_num_cols(num_cols):
    if num_cols == 5:
        return 300
    else:
        return (6 - num_cols) * 200


def grid_view_instances(
        num_rows: int,
        instances: Dict[int, Tuple[AnnotationDefinitions, MetricDefinitions, Captures, int, str]],
        labelers: Dict[str, bool]):
    """ Creates the grid view streamlit components when using a Datamaker dataset

    :param num_rows: Number of rows
    :type num_rows: int
    :param instances: Dictionary of instances
    :type instances: Dict[int, Tuple[AnnotationDefinitions, MetricDefinitions, Captures, int, str]]
    :param labelers: Dictionary containing keys for the name of every labeler available in the given dataset
                     and the corresponding value is a boolean representing whether or not to display it
    :type labelers: Dict[str, bool]
    """
    dataset_size = datamaker.get_dataset_length_with_instances(instances)
    num_cols, start_at = create_grid_view_controls(num_rows, dataset_size)

    containers = create_grid_containers(num_rows, num_cols, start_at, dataset_size)

    for i in range(start_at, min(start_at + (num_cols * num_rows), dataset_size)):
        instance_key = datamaker.get_instance_by_capture_idx(instances, i)
        ds = instances[instance_key]
        ann_def = ds.ann_def
        cap = ds.cap
        data_root = ds.data_root
        image = ds.get_image_with_labelers(i - datamaker.get_dataset_length_with_instances(instances, instance_key),
                                           labelers, max_size=(6 - num_cols) * 150)
        containers[i - start_at].image(image, caption=str(i), use_column_width=True)


def zoom(index: int,
         offset: int,
         ds: Dataset,
         labelers: Dict[str, bool]):
    """ Creates streamlit components for Zoom in view

    :param index: Index of the image
    :type index: int
    :param offset: Is how much the index needs to be offset, this is only needed to 
                   handle multiple instances (Datamaker datasets)
    :type offset: int
    :param ds: Current Dataset
    :type ds: Dataset
    :param labelers: Dictionary containing keys for the name of every labeler available in the given dataset
                     and the corresponding value is a boolean representing whether or not to display it
    :type labelers: Dict[str, bool]
    """
    dataset_size = ds.length()

    st.session_state.start_at = index
    st.session_state.zoom_image = index

    if st.button('< Back to Grid view'):
        st.session_state.zoom_image = -1
        st.session_state.just_opened_grid = True
        st.experimental_rerun()

    header = st.beta_columns([2 / 3, 1 / 3])
    with header[0]:
        new_index = cc.item_selector_zoom(index, dataset_size + offset)
        if not new_index == index and not st.session_state.just_opened_zoom and not st.session_state.labelers_changed:
            st.session_state.zoom_image = new_index
            st.session_state.start_at = index
            st.experimental_rerun()

    st.session_state.start_at = index
    st.session_state.zoom_image = index
    st.session_state.just_opened_zoom = False

    components.html("""<hr style="height:2px;border:none;color:#AAA;background-color:#AAA;" /> """, height=30)

    index = index - offset
    image = ds.get_image_with_labelers(index, labelers, max_size=2000)

    st.image(image, use_column_width=True)
    layout = st.beta_columns(2)
    layout[0].title("Captures Metadata")

    captures_dir = None
    for directory in os.walk(ds.data_root):
        name = str(directory[0]).replace('\\', '/').split('/')[-1]
        if name.startswith("Dataset") and \
                "." not in name[1:] and \
                os.path.abspath(ds.data_root) != os.path.abspath(directory[0]):
            captures_dir = os.path.abspath(directory[0])
            break

    path_to_captures = os.path.join(os.path.abspath(captures_dir), "captures_000.json")
    json_file = json.load(open(path_to_captures, "r", encoding="utf8"))
    num_captures_per_file = len(json_file["captures"])

    file_num = index // num_captures_per_file
    postfix = ('000' + str(file_num))
    postfix = postfix[len(postfix) - 3:]
    path_to_captures = os.path.join(os.path.abspath(captures_dir), "captures_" + postfix + ".json")
    with layout[0]:
        json_file = json.load(open(path_to_captures, "r", encoding="utf8"))
        capture = json_file['captures'][index % num_captures_per_file]
        st.write(capture)

    layout[1].title("Metrics Metadata")
    metrics = []
    for i in os.listdir(captures_dir):
        path_to_metrics = os.path.join(captures_dir, i)
        if os.path.isfile(path_to_metrics) and 'metrics_' in i and 'definitions' not in i:
            json_file = json.load(open(path_to_metrics, encoding="utf8"))
            metrics.extend(json_file['metrics'])
    with layout[1]:
        for metric in metrics:
            if metric['sequence_id'] == capture['sequence_id'] and metric['step'] == capture['step']:
                for metric_def in ds.get_metrics_records():
                    if metric_def['id'] == metric['metric_definition']:
                        st.markdown("## " + metric_def['name'])
                st.write(metric)