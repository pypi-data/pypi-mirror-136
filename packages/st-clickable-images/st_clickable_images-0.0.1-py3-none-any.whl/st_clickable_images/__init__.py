import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "clickable_images",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "st_clickable_images", path=build_dir
    )


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def clickable_images(paths, titles=[], div_style={}, img_style={}, key=None):
    """Create a new instance of "my_component".

    Parameters
    ----------
    paths: list
        The list of URLS of the images
    
    titles: list
        The (optional) titles of the images
    
    div_style: dict
        A dict with the CSS property/value pairs for the div container

    img_style: dict
        A dict with the CSS property/value pairs for the images

    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    int
        The index of the last image clicked on (or -1 before any click)

    """
    component_value = _component_func(
        paths=paths,
        titles=titles,
        div_style=div_style,
        img_style=img_style,
        key=key,
        default=-1,
    )

    return component_value


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
if not _RELEASE:
    import streamlit as st

    clicked = clickable_images(
        [
            "https://images.unsplash.com/photo-1565130838609-c3a86655db61?w=700",
            "https://images.unsplash.com/photo-1565372195458-9de0b320ef04?w=700",
            "https://images.unsplash.com/photo-1582550945154-66ea8fff25e1?w=700",
            "https://images.unsplash.com/photo-1591797442444-039f23ddcc14?w=700",
            "https://images.unsplash.com/photo-1518727818782-ed5341dbd476?w=700",
        ],
        titles=[f"Image #{str(i)}" for i in range(5)],
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": "5px", "height": "200px"},
        key="foo",
    )

    st.markdown(f"Image #{clicked} clicked" if clicked > -1 else "No image clicked")
