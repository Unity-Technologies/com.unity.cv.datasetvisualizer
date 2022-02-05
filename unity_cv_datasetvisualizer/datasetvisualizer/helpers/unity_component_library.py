import os
import streamlit.components.v1 as components

COMPONENT_DEBUG_MODE = True

"""
        -- COMPONENT DECLARATIONS --
    We define a Streamlit component via reference to a pre-built directory containing the web code for it. 
"""

components_configuration = {
    "item_selector": {
        "path": "itemselector",
        "port": 3001
    },
    "item_selector_zoom": {
        "path": "itemselectorzoom",
        "port": 3002
    },
    "page_selector": {
        "path": "pageselector",
        "port": 3003
    },
}


def get_component(name):
    if name not in components_configuration:
        raise Exception(f"Component {name} not declared.")

    component_info = components_configuration[name]
    if COMPONENT_DEBUG_MODE:
        return components.declare_component(
            name,
            url=f"http://localhost:{component_info['port']}"
        )
    else:
        return components.declare_component(
            name,
            path=os.path.join(os.path.abspath(__file__), "..", "built_components", component_info['path'], "build")
        )


# Load in the streamlit components
_item_selector = get_component("item_selector")
_item_selector_zoom = get_component("item_selector_zoom")
_page_selector = get_component("page_selector")

"""
        -- WRAPPER FUNCTIONS --
    Wrapper functions for each of the components. This allows us to process the input arguments to the components
    (for example to clamp values) or change the properties of the component.
"""


def item_selector(start_at, increment_amount, dataset_size, key='item-selector'):
    return _item_selector(
        startAt=start_at, incrementAmt=increment_amount, datasetSize=dataset_size,
        key=key, default=start_at
    )


def item_selector_zoom(index, dataset_size, key='item-selector-zoom'):
    return _item_selector_zoom(index=index, datasetSize=dataset_size, key=key, default=index)


def page_selector(start_at, increment_amount, key='page-selector'):
    return _page_selector(startAt=start_at, incrementAmt=increment_amount, key=key, default=0)
