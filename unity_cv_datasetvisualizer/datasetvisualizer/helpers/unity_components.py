import os
import streamlit.components.v1 as components

built_components_dir = "../built_components"
built_component_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "built_components")

# Paths to the pre-built location of the components
build_dir_slider = os.path.join(built_component_directory, "slider", "build")
build_dir_page_selector = os.path.join(built_component_directory, "pageselector", "build")
build_dir_go_to = os.path.join(built_component_directory, "goto", "build")
build_dir_item_selector = os.path.join(built_component_directory, "itemselector", "build")
build_dir_image_selector = os.path.join(built_component_directory, "imageselector", "build")
build_dir_json_viewer = os.path.join(built_component_directory, "jsonviewer", "build")
build_dir_item_selector_zoom = os.path.join(built_component_directory, "itemselectorzoom", "build")

"""
        -- COMPONENT DECLARATIONS --
    We define a Streamlit component via reference to a pre-built directory containing the web code for it. 
"""

# Discrete Slider
_discrete_slider = components.declare_component(
    "discrete_slider",
    path=build_dir_slider
)
# Page Selector
_page_selector = components.declare_component(
    "page_selector",
    path=build_dir_page_selector
)
# Go To
_go_to = components.declare_component(
    "go_to",
    path=build_dir_go_to
)
# Item Selector
_item_selector = components.declare_component(
    "item_selector",
    path=build_dir_item_selector
)
# Image Selector
_image_selector = components.declare_component(
    "image_selector",
    path=build_dir_image_selector
)
# Json Viewer
_json_viewer = components.declare_component(
    "json_viewer",
    path=build_dir_json_viewer
)
# Item Selector
_item_selector_zoom = components.declare_component(
    "item_selector_zoom",
    path=build_dir_item_selector_zoom
)

"""
        -- WRAPPER FUNCTIONS --
    Wrapper functions for each of the components. This allows us to process the input arguments to the components
    (for example to clamp values) or change the properties of the component.
"""


def discrete_slider(greeting, name, key, default=0):
    return _discrete_slider(greeting=greeting, name=name, default=default, key=key)


def page_selector(start_at, increment_amount, key='6'):
    return _page_selector(startAt=start_at, incrementAmt=increment_amount, key=key, default=0)


def go_to(key='5'):
    return _go_to(key=key, default=0)


def item_selector(start_at, increment_amount, dataset_size, key='4'):
    return _item_selector(
        startAt=start_at, incrementAmt=increment_amount, datasetSize=dataset_size,
        key=key, default=start_at
    )


def image_selector(index, key='3'):
    return _image_selector(index=index, key=key, default=index)


def json_viewer(metadata, key='2'):
    return _json_viewer(jsonMetadata=metadata, key=key, default=0)


def item_selector_zoom(index, dataset_size, key='1'):
    return _item_selector_zoom(index=index, datasetSize=dataset_size, key=key, default=index)
