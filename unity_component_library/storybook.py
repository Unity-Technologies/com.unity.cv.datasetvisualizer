import os
import streamlit.components.v1 as components

# Set to True when building the components
# Set to False during development
_RELEASE = False

# When releasing, get the components from the respective path
# When developing, get from the localhost server at some port
if _RELEASE:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")

    _page_selector = components.declare_component("page_selector", path=build_dir)
else:
    _page_selector = components.declare_component(
        "page_selector",
        url="http://localhost:3001",
    )


def page_selector(increment_amt: int, key=None):
    component_value = _page_selector(incrementAmt=increment_amt, key=key, default=0)
    return component_value


# Test the components during development
if not _RELEASE:
    import streamlit as st

    st.subheader("Component – Page Selector")
    start_at = page_selector(10)

    st.subheader("Component – Go To")
