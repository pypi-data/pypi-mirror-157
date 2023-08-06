from kabaret import flow
from kabaret.flow_entities.entities import Entity
from libreflow.baseflow.film import Film as BaseFilm

from .shot import Shots


class Film(BaseFilm):
    
    shots = flow.Child(Shots).ui(expanded=True)

    sequences = flow.Child(flow.Object).ui(hidden=True)
