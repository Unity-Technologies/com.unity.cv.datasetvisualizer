import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Union

import streamlit as st
from PIL import Image


class Components:
    @staticmethod
    def img(
        path: Union[str, Path],
        caption: Optional[str] = None,
        use_column_width: bool = True,
    ):
        """
        Streamlit doesn't seem to handle Windows paths at all!
        """
        final_path = str(path.resolve()) if type(path) is Path else str(path)
        pil_image = Image.open(final_path)
        st.image(pil_image, caption=caption, use_column_width=use_column_width)

    @staticmethod
    def badge(text: str):
        st.write(f'<div class="uui-badge"><p>{text}</p></div>', unsafe_allow_html=True)

    @staticmethod
    def scrollable_text(text: str, label: str):
        st.write(
            f'<div class="uui-labeled">'
            f"  <label>{label}</label>"
            f'  <div class="uui-scrollable-text">'
            f"      <span>{text}</span>"
            f"  </div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    @staticmethod
    def draw_homepage():
        st.markdown("# Unity CV Dataset Visualizer")
        Components.img(
            AppState.get_docs_path("showcase-5-labelers.gif"),
            caption="Visualization of various labelers",
            use_column_width=False,
        )
        st.markdown(
            '<p style="max-width: 600px;">'
            "Unity Computer Vision team's Dataset Visualizer provides an easy way to quickly visualize annotations "
            "from synthetic data generated using the Perception Package. Even for large datasets, selectively sample "
            "frames and visualize 2D Bounding Boxes, 3D Bounding Boxes, Keypoints, Semantic Segmentation, and Instance "
            "Segmentation data for each frame. Additionally, dive into the capture and metric JSON data to see "
            "in-depth information on each frame!"
            "</p>",
            unsafe_allow_html=True,
        )
        st.markdown("### How to Use")
        st.markdown(
            "1. Click on the **Select Dataset** in the sidebar.\n"
            "2. Choose the root folder of your dataset created using the Perception Package.\n"
            "3. Dataset Visualizer will read and display the dataset in a grid view."
        )


class AppState:
    @staticmethod
    def get_base_dataset_directory():
        return st.session_state.curr_dir

    @staticmethod
    def set_base_dataset_directory(value: str):
        st.session_state.curr_dir = value

    @staticmethod
    def get_selected_dataset_directory():
        return st.session_state.selected_dir

    @staticmethod
    def set_selected_dataset_directory(value: str):
        st.session_state.selected_dir = value

    @staticmethod
    def get_starting_frame():
        return st.session_state.start_at

    @staticmethod
    def set_starting_frame(value: int):
        st.session_state.start_at = value

    @staticmethod
    def get_zoom_image():
        return st.session_state.zoom_image

    @staticmethod
    def set_zoom_image(value: int):
        st.session_state.zoom_image = value

    @staticmethod
    def set_in_zoom_mode(value: bool):
        st.session_state.just_opened_zoom = value

    @staticmethod
    def get_in_zoom_mode():
        return st.session_state.just_opened_zoom

    @staticmethod
    def set_in_grid_mode(value: bool):
        st.session_state.just_opened_grid = value

    @staticmethod
    def get_in_grid_mode():
        return st.session_state.just_opened_grid

    @staticmethod
    def set_labelers_changed(value: bool):
        st.session_state.labelers_changed = value

    @staticmethod
    def get_labelers_changed():
        return st.session_state.labelers_changed

    @staticmethod
    def get_dataset_view_range() -> [int, int]:
        if "dataset_size" not in st.session_state:
            st.session_state.dataset_size = [0, 0]
        return st.session_state.dataset_size

    @staticmethod
    def set_dataset_view_range(value: [int, int]):
        st.session_state.dataset_size = value

    @staticmethod
    def get_num_cols():
        return st.session_state.num_cols

    @staticmethod
    def set_num_cols(value: int):
        st.session_state.num_cols = value

    @staticmethod
    def set_dataset_directory(value: str):
        st.session_state.curr_dir = value

    @staticmethod
    def get_dataset_directory():
        return st.session_state.curr_dir

    @staticmethod
    def set_instances_count(instance_count: int):
        st.session_state.instance_counts = instance_count

    @staticmethod
    def get_instances_count():
        return st.session_state.instances_count

    @staticmethod
    def set_selected_instance(selected_instance: int):
        st.session_state.selected_instance = selected_instance

    @staticmethod
    def get_selected_instance():
        return st.session_state.selected_instance

    @staticmethod
    def get_docs_path(doc: str, as_str=False):
        docs_path = Path(os.path.dirname(__file__)).resolve()
        file_path = (docs_path / ".." / "docs" / doc).resolve()
        return file_path if not as_str else str(file_path)

    @staticmethod
    def create_default_state(dataset_dir=""):
        AppState.create_session_state_data(
            {
                "zoom_image": "-1",
                "start_at": "0",
                "num_cols": "3",
                "curr_dir": dataset_dir,
                "instances_count": 0,
                "selected_instance": 0,
                "just_opened_zoom": True,
                "just_opened_grid": True,
                "bbox2d_existed_last_time": False,
                "bbox3d_existed_last_time": False,
                "keypoints_existed_last_time": False,
                "semantic_existed_last_time": False,
                "previous_labelers": {},
                "labelers_changed": False,
            }
        )

    @staticmethod
    def create_session_state_data(attribute_values: Dict[str, any]):
        """Takes a dictionary of attributes to values to create the streamlit session_state object.
        The values are the default values

        :param attribute_values: dictionary of session_state parameter to default values
        :type attribute_values: Dict[str, any]
        """
        for key in attribute_values:
            if key not in st.session_state:
                st.session_state[key] = attribute_values[key]

    @staticmethod
    def display_horizontal_rule():
        st.markdown(f"<hr />", unsafe_allow_html=True)

    @staticmethod
    def display_number_frames(num_frames: int):
        st.markdown(f"**Total Frames**: {num_frames}")

    @staticmethod
    def display_sidebar_item(label: str, value: str):
        st.markdown(f"**{label}**: {value}")

    @staticmethod
    def show_select_folder_dialog() -> Optional[str]:
        """
        Runs a subprocess that opens a file dialog to select a directory. Returns path to the directory or None if user
        cancelled the operation.
        """
        current_dir = Path(os.path.join(os.path.dirname(os.path.realpath(__file__))))
        folder_ops_module_path = (current_dir / "folder_ops.py").resolve()

        output = subprocess.run(
            [sys.executable, str(folder_ops_module_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        if (
            str(output.stdout).split("'")[1] == ""
            or output.stdout is None
            or str(output.stdout) == 'b"'
        ):
            return None

        stdout = str(os.path.abspath(str(output.stdout).split("'")[1]))

        if stdout[-4:] == "\\r\\n":
            stdout = stdout[:-4]
        elif stdout[-2:] == "\\n":
            stdout = stdout[:-2]

        proj_root = stdout.replace("\\", "/") + "/"
        return proj_root
