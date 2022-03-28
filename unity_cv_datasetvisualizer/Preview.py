import argparse
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict
import streamlit as st
import streamlit.components.v1 as components
from LegacyDataset import Dataset as LegacyDataset
from LegacyPreview import preview_dataset as legacy_preview_dataset
from SoloDataset import Dataset as SoloDataset
from SoloPreview import preview_dataset as solo_preview_dataset
import pathlib



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

    # Add logo
    st.sidebar.write(
        '<div style="display: flex; justify-content: center; padding-bottom: 16px;">'
        '<svg version="1.1" id="Logo" xmlns="http://www.w3.org/2000/svg" x="0" y="0" viewBox="0 0 130.5 48" xml:space="preserve" width="132" height="48"><style>.st0{fill:#4c4c4c}</style><path d="M53.7 26.1V12.5h5.7v13.8c0 2.3 1.2 3.8 4 3.8 2.6 0 3.9-1.6 3.9-3.9V12.5H73v13.6c0 5.3-3.2 8.5-9.6 8.5-6.5.1-9.7-3.1-9.7-8.5zM75.6 17.7h5.1V20h.1c1.2-1.8 2.8-2.7 5.1-2.7 3.6 0 5.7 2.6 5.7 6.3v10.7h-5.3v-9.7c0-1.7-.9-2.9-2.6-2.9-1.7 0-2.9 1.5-2.9 3.5v9.1h-5.3V17.7zM94.3 11.2h5.3v4.3h-5.3v-4.3zm0 6.5h5.3v16.5h-5.3V17.7zM103.7 29.9V22h-2.2v-4.3h2.2v-5.2h5.1v5.2h3V22h-3v6.8c0 1.3.7 1.6 1.8 1.6h1.2v3.8c-.5.1-1.5.3-2.9.3-3 0-5.2-1-5.2-4.6zM115.1 35.6h1.8c1.5 0 2.2-.6 2.2-1.7 0-.7-.3-1.7-1-3.4l-4.9-12.7h5.5l2.2 7c.5 1.6 1 3.8 1 3.8h.1s.5-2.2 1-3.8l2.2-7h5.3l-5.7 16.7c-1.3 3.9-2.9 5.2-6.2 5.2h-3.4l-.1-4.1z"></path><path class="st0" d="M42.5 33.6V11.2L23.1 0v8.6l7.6 4.4c.3.2.3.6 0 .7l-9 5.2c-.3.2-.6.1-.8 0l-9-5.2c-.3-.1-.3-.6 0-.7l7.6-4.4V0L0 11.2v22.4-.1.1l7.4-4.3v-8.8c0-.3.4-.5.6-.4l9 5.2c.3.2.4.4.4.7v10.4c0 .3-.4.5-.6.4l-7.6-4.4-7.4 4.3L21.2 48l19.4-11.2-7.4-4.3-7.6 4.4c-.3.2-.6 0-.6-.4V26.1c0-.3.2-.6.4-.7l9-5.2c.3-.2.6 0 .6.4v8.8l7.5 4.2z"></path><path d="M21.2 48l19.4-11.2-7.4-4.3-7.6 4.4c-.3.2-.6 0-.6-.4V26.1c0-.3.2-.6.4-.7l9-5.2c.3-.2.6 0 .6.4v8.8l7.4 4.3V11.2L21.2 23.5V48z"></path><path d="M23.1 0v8.6l7.6 4.4c.3.2.3.6 0 .7l-9 5.2c-.3.2-.6.1-.8 0l-9-5.2c-.3-.1-.3-.6 0-.7l7.6-4.4V0L0 11.2l21.2 12.3 21.2-12.3L23.1 0z" fill="gray"></path><path class="st0" d="M16.9 36.9l-7.6-4.4-7.4 4.3L21.3 48V23.5L0 11.2v22.4-.1.1l7.4-4.3v-8.8c0-.3.4-.5.6-.4l9 5.2c.3.2.4.4.4.7v10.4c.1.4-.2.7-.5.5z"></path></svg>'
        '</div>',
        unsafe_allow_html=True
    )

    # Display select dataset menu
    st.sidebar.markdown("## Select Dataset")
    if st.sidebar.button("Open Dataset"):
        folder_select()

    if base_dataset_dir is None:
        st.markdown("# Unity CV Dataset Visualizer")
        st.image("https://github.com/Unity-Technologies/com.unity.perception/blob/main/com.unity.perception/Documentation~/images/banner2.PNG")
        #if st.button("Open Dataset", key="second open dataset"):
        #    folder_select()
        return

    # Display name of dataset (Name of folder)
    dataset_name = os.path.abspath(base_dataset_dir).replace("\\", "/")

    if dataset_name[-1] == '/':
        folder_name = dataset_name.split('/')[-2]
    else:
        folder_name = dataset_name.split('/')[-1]

    if dataset_name is not None and dataset_name.strip() != "":
        data_root = os.path.abspath(dataset_name)
        # Attempt to read as a solo format perception dataset
        if SoloDataset.check_folder_valid(data_root):
            solo_preview_dataset(data_root, folder_name)
        # Attempt to read as a legacy format perception dataset
        else:
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

    st.set_page_config(
        page_title="Unity Dataset Visualizer",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # removes the default zoom button on images
    # TODO: Use global CSS
    st.markdown('<style>button.css-enefr8{display: none;}'
                '       button.css-1u96g9d{display: none;}</style>', unsafe_allow_html=True)

    # TODO: Add back the ability to take in --data command from CLI
    #parser = argparse.ArgumentParser()
    #parser.add_argument("--data", type=str)
    #args = parser.parse_args()
    #
    #if "data" in args and os.path.isdir(args.data):
    #    preview_app({"data": args.data})
    #else:
    preview_app({"data": None})
