from operator import ge
import os
import json
import streamlit.components.v1 as components
from typing import ( Optional, Union, List )

_RELEASE = True

if not _RELEASE:
    _get_host = components.declare_component(
        "get_host",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "./get_host/frontend/build")
    _get_host = components.declare_component("get_host", path=build_dir)

def get_host(key='foo'):
    """Create a new instance of "get_geometry".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    host: 'web' | 'rhino' | 'revit' | 'sketchup'
    """
    
    get_host = _get_host(key=key)

    return get_host

if not _RELEASE:
    _get_geometry = components.declare_component(
        "get_geometry",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "./get_geometry/frontend/build")
    _get_geometry = components.declare_component("get_geometry", path=build_dir)

def get_geometry(key='foo'):
    """Create a new instance of "get_geometry".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    dict
        A dictionary with the following structure

        {
            'geometry': List[dict]
        }

        where
            'geometry': List of ladybug geometries as dictionary
    """
    
    get_geometry = _get_geometry(key=key)

    return get_geometry


if not _RELEASE:
    _get_hbjson = components.declare_component(
        "get_hbjson",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "./get_hbjson/frontend/build")
    _get_hbjson = components.declare_component("get_hbjson", path=build_dir)

def get_hbjson(key='foo'):
    """Create a new instance of "get_hbjson".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    dict
        A dictionary with the following structure

        {
            'hbjson': dict
        }

        where
            'hbjson': hbjson model as dictionary
    """
    
    get_hbjson = _get_hbjson(key=key)

    return get_hbjson


if not _RELEASE:
    _send_geometry = components.declare_component(
        "send_geometry",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "./send_geometry/frontend/build")
    _send_geometry = components.declare_component("send_geometry", path=build_dir)

def send_geometry(key='foo', *, geometry={}, option='preview'):
    """Create a new instance of "send_geometry".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    geometry: dictionary
    option: 'add' | 'preview' | 'clear' | 'subscribe-preview'

    Returns
    -------
    """
    
    send_geometry = _send_geometry(geometry=geometry, key=key, option=option)

    return send_geometry


if not _RELEASE:
    _send_hbjson = components.declare_component(
        "send_hbjson",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "./send_hbjson/frontend/build")
    _send_hbjson = components.declare_component("send_hbjson", path=build_dir)

def send_hbjson(key='foo', *, hbjson={}, option='preview'):
    """Create a new instance of "send_hbjson".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    hbjson: dictionary
    option: 'add' | 'preview' | 'clear' | 'subscribe-preview'

    Returns
    -------
    """
    
    send_hbjson = _send_hbjson(hbjson=hbjson, key=key, option=option)

    return send_hbjson



if not _RELEASE:
    _send_results = components.declare_component(
        "send_hbjson",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "./send_results/frontend/build")
    _send_results = components.declare_component("send_results", path=build_dir)

def send_results(key='foo', *, geometry={}):
    """Create a new instance of "send_hbjson".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    geometry: dictionary

    Returns
    -------
    """
    
    send_results = _send_results(key=key, geometry=geometry)

    return send_results

if not _RELEASE:
    import streamlit as st

    st.header("Hello Get Geometry!")

    # Create an instance of our component with a constant `name` arg, and
    # print its output value.
    geometry = get_geometry('bar')
    
    st.json(geometry)

    