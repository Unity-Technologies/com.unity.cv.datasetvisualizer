from datasetvisualizer.SoloDataset import Dataset as SoloDataset
from datasetvisualizer.LegacyDataset import Dataset as LegacyDataset
from datasetvisualizer.SoloPreview import preview_dataset as solo_preview_dataset
from datasetvisualizer.LegacyPreview import preview_dataset as legacy_preview_dataset
import streamlit as st
from google.protobuf.json_format import Parse, ParseError
import argparse
import os
from typing import List, Tuple, Optional, Dict
import subprocess
import argparse
import json
import os
import sys
import subprocess
from typing import List, Tuple, Optional, Dict
import re
import streamlit as st

import streamlit.components.v1 as components
import itertools

def create_session_state_data(attribute_values: Dict[str, any]):
    """ Takes a dictionary of attributes to values to create the streamlit session_state object.
    The values are the default values

    :param attribute_values: dictionary of session_state parameter to default values
    :type attribute_values: Dict[str, any]
    """
    for key in attribute_values:
        if key not in st.session_state:
            st.session_state[key] = attribute_values[key]

def create_select_dataset_page(base_dataset_dir: str):
    # Create state with default values
    create_session_state_data({
        'zoom_image': '-1',
        'start_at': '0',
        'num_cols': '3',
        'curr_dir': base_dataset_dir,

        'just_opened_zoom': True,
        'just_opened_grid': True,

        'bbox2d_existed_last_time': False,
        'bbox3d_existed_last_time': False,
        'keypoints_existed_last_time': False,
        'semantic_existed_last_time': False,

        'previous_labelers': {},
        'labelers_changed': False,
    })
    # Gets the latest selected directory
    base_dataset_dir = st.session_state.curr_dir

    # Display select dataset menu
    st.sidebar.markdown("# Select Dataset")
    if st.sidebar.button("Open Dataset"):
        folder_select()

    if base_dataset_dir is None:
        st.markdown("# Please open a dataset folder:")
        if st.button("Open Dataset", key="second open dataset"):
            folder_select()
        return

    # Display name of dataset (Name of folder)
    dataset_name = os.path.abspath(base_dataset_dir).replace("\\", "/")

    if dataset_name[-1] == '/':
        folder_name = dataset_name.split('/')[-2]
    else:
        folder_name = dataset_name.split('/')[-1]

    if dataset_name is not None and dataset_name.strip() != "":
        data_root = os.path.abspath(dataset_name)
        # Attempt to read as a solo perception dataset
        if SoloDataset.check_folder_valid(data_root):
            # filename = os.path.join(dirname, "SoloPreview.py")
            solo_preview_dataset(data_root, folder_name)
        elif LegacyDataset.check_folder_valid(data_root):
            # filename = os.path.join(dirname, "LegacyPreview.py")
            legacy_preview_dataset(data_root, folder_name)

    else:
        st.markdown("# Please select a valid dataset folder:")
        if st.button("Select dataset folder"):
            folder_select()

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

def preview_app(args):
    """
    Starts the dataset preview app.

    :param args: Arguments for the app, such as dataset
    :type args: Namespace
    """
    create_select_dataset_page(args["data"])


if __name__ == "__main__":

    # This needs to be the first streamlit command
    st.set_page_config(layout="wide")
    # removes the default zoom button on images
    st.markdown('<style>button.css-enefr8{display: none;}'
                '       button.css-1u96g9d{display: none;}</style>', unsafe_allow_html=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=str)
    args = parser.parse_args()
    if os.path.isdir(args.data):
        preview_app({"data": args.data})
    else:
        preview_app({"data": None})