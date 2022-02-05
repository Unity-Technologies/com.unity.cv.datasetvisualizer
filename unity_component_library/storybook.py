import os
import streamlit.components.v1 as components

# Set to True when building the components
# Set to False during development
_RELEASE = False

_item_selector = components.declare_component(
    "item_selector",
    url="http://localhost:3001",
)

_item_selector_zoom = components.declare_component(
    "item_selector_zoom",
    url="http://localhost:3002",
)

_page_selector = components.declare_component(
    "page_selector",
    url="http://localhost:3003",
)

# Test the components during development
if not _RELEASE:
    import streamlit as st

    st.header("All Custom Components")

    st.subheader("1. Item Selector")
    _item_selector(startAt=10, datasetSize=200, incrementAmt=1, key='item-selector')

    st.subheader("2. Item Selector Zoom")
    _item_selector_zoom(startAt=10, datasetSize=200, incrementAmt=1, key='item-selector-zoom')

    st.subheader("3. Page Selector")
    _page_selector(incrementAmt=1, key='page-selector', default=0)
