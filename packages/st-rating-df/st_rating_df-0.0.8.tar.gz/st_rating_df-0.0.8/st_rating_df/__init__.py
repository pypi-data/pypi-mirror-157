import os
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True


if not _RELEASE:
    _st_rating_df = components.declare_component("st_rating_df", url="http://localhost:3001" )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _st_rating_df = components.declare_component("st_rating_df", path=build_dir)


def st_rating_df(data,  height, width=-1, evaluationColumn=-1, smilesColumn=15, key=None):
    if(evaluationColumn==-1):
        data.insert(loc=0, column='Rating', value=np.zeros(data.shape[0]))
        evaluationColumn=0
        smilesColumn+=1
    return _st_rating_df(data=data, evaluationColumn=evaluationColumn, smilesColumn=smilesColumn,width=width, height=height, key=key)
