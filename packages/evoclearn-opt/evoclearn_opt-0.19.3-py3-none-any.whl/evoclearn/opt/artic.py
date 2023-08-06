# -*- coding: utf-8 -*-
"""DEMIT TODO: Of course all the defaults here and in EVL-core are
actually based on the "JD2" speaker. Once we store all of this kind of
stuff in the speaker file and update EVL-core to do better "speaker
management", then we can revamp this file, constraints and the tools
built around it.

"""

from functools import partial
from itertools import groupby

import numpy as np
import pandas as pd

from evoclearn.core.definitions import VOCALTRACT_PARAMS
from evoclearn.core.constraints.generic import (DEFAULT_VOLUME_VELOCITY_THRESHOLD,
                                                DEFAULT_SINGLE_PLACE_CLOSURE_MAX_LENGTH)
from evoclearn.core import vocaltractlab as vtl
from evoclearn.core.vocaltractlab import TUBE_AREA_THRESHOLD as TUBE_AREA_EPSILON
from evoclearn.core import utils


VOCALTRACT_PARAMS = list(VOCALTRACT_PARAMS)
DEFAULT_OPEN_TRACT_AREA_THRESHOLD = 0.3
DEFAULT_ALMOST_OPEN_TRACT_AREA_THRESHOLD = 0.1
DEFAULT_TONGUE_TIP_LENGTH = 1.5

DEFAULT_CV_ARTICVECSPEC = [["C", "tract_open", "le", 3.34e-04],
                           ["V", "voiced", "ge", 1.0],
                           ["V", "tract_open", "ge", 1.0]]


def _contiguous_closure_lengths(tubes, open_tract_area_threshold):
    closed = []
    for i in range(len(tubes)):
        if tubes["tube_area"].iloc[i] < open_tract_area_threshold:
            closed.append(True)
        else:
            closed.append(False)
    closed_lengths = []
    i = 0
    for is_closed, run in groupby(closed):
        run = list(run)
        if is_closed:
           closed_lengths.append(tubes["tube_length"][i:i+len(run)].sum())
        i += len(run)
    return closed_lengths


def voiced(seq,
           volume_velocity_threshold=DEFAULT_VOLUME_VELOCITY_THRESHOLD,
           num_spectrum_samples = 2048) -> float:
    """-> [0.0, 1.0]"""
    assert len(seq) == 1 and not seq.empty
    (magnitude_spectrum,
     phase_spectrum) = vtl.transfer_function(seq.iloc[0],
                                             num_spectrum_samples)
    mag = magnitude_spectrum[:num_spectrum_samples // 2]
    clipped_normmaxvol = min(mag.max() / (10 ** volume_velocity_threshold), 1.0)
    return clipped_normmaxvol


def tract_open(seq,
               open_tract_area_threshold=DEFAULT_OPEN_TRACT_AREA_THRESHOLD):
    assert len(seq) == 1 and not seq.empty
    areas = vtl.tube(seq.iloc[0][VOCALTRACT_PARAMS]).tubes["tube_area"]
    clipped_normminarea = min(areas.min() / open_tract_area_threshold, 1.0)
    return clipped_normminarea


def tongue_tip_open(seq,
                    tongue_tip_length=DEFAULT_TONGUE_TIP_LENGTH,
                    invert_articulators=False,
                    open_tract_area_threshold=DEFAULT_OPEN_TRACT_AREA_THRESHOLD):
    assert len(seq) == 1 and not seq.empty
    tongue_idx = pd.IndexSlice[:, "tongue"]
    tubes = vtl.tube(seq.iloc[0][VOCALTRACT_PARAMS]).tubes
    tongue_from_tip_to_body = tubes.loc[tongue_idx, :].iloc[::-1]
    tongue_positions_relative_to_tip = np.cumsum(tongue_from_tip_to_body["tube_length"])
    tongue_tip_areas = tongue_from_tip_to_body.loc[tongue_positions_relative_to_tip < tongue_tip_length]["tube_area"]
    areas = (tongue_tip_areas
             if not invert_articulators
             else tubes.loc[tubes.index.difference(tongue_tip_areas.index)]["tube_area"])
    clipped_normminarea = min(areas.min() / open_tract_area_threshold, 1.0)
    return clipped_normminarea



def tongue_body_open(seq,
                     tongue_tip_length=DEFAULT_TONGUE_TIP_LENGTH,
                     invert_articulators=False,
                     open_tract_area_threshold=DEFAULT_OPEN_TRACT_AREA_THRESHOLD):
    assert len(seq) == 1 and not seq.empty
    tongue_idx = pd.IndexSlice[:, "tongue"]
    tubes = vtl.tube(seq.iloc[0][VOCALTRACT_PARAMS]).tubes
    tongue_from_tip_to_body = tubes.loc[tongue_idx, :].iloc[::-1]
    tongue_positions_relative_to_tip = np.cumsum(tongue_from_tip_to_body["tube_length"])
    tongue_body_areas = tongue_from_tip_to_body.loc[tongue_positions_relative_to_tip >= tongue_tip_length]["tube_area"]
    areas = (tongue_body_areas
             if not invert_articulators
             else tubes.loc[tubes.index.difference(tongue_body_areas.index)]["tube_area"])
    clipped_normminarea = min(areas.min() / open_tract_area_threshold, 1.0)
    return clipped_normminarea


def articulators_open(seq,
                      articulators,
                      invert_articulators=False,
                      open_tract_area_threshold=DEFAULT_OPEN_TRACT_AREA_THRESHOLD):
    assert len(seq) == 1 and not seq.empty
    articulators_idx = pd.IndexSlice[:, articulators]
    tubes = vtl.tube(seq.iloc[0][VOCALTRACT_PARAMS]).tubes
    try:
        _areas = tubes.loc[articulators_idx, :]["tube_area"]
    except KeyError:
        if not invert_articulators:
            areas = None
        else:
            areas = tubes["tube_area"]
    else:
        if not invert_articulators:
            areas = _areas
        else:
            areas = tubes.loc[tubes.index.difference(_areas.index)]["tube_area"]
    if areas is None:
        clipped_normminarea = 1.0
    else:
        clipped_normminarea = min(areas.min() / open_tract_area_threshold, 1.0)
    return clipped_normminarea


mouth_open = partial(articulators_open,
                     articulators=["lower_incisors", "lower_lip"])

lip_open = partial(articulators_open,
                   articulators="lower_lip")
teeth_open = partial(articulators_open,
                   articulators="lower_incisors")

other_than_tongue_tip_open = partial(tongue_tip_open,
                                     invert_articulators=True)
other_than_tongue_body_open = partial(tongue_body_open,
                                      invert_articulators=True)
other_than_mouth_open = partial(articulators_open,
                                articulators=["lower_incisors", "lower_lip"],
                                invert_articulators=True)
other_than_lip_open = partial(articulators_open,
                              articulators="lower_lip",
                              invert_articulators=True)


def precise_closures(seq,
                     maximum_closure_length=DEFAULT_SINGLE_PLACE_CLOSURE_MAX_LENGTH,
                     open_tract_area_threshold=DEFAULT_ALMOST_OPEN_TRACT_AREA_THRESHOLD):
    assert len(seq) == 1 and not seq.empty
    tubes = vtl.tube(seq.iloc[0][VOCALTRACT_PARAMS]).tubes
    closure_lengths = np.array(_contiguous_closure_lengths(tubes,
                                                           open_tract_area_threshold))
    if len(closure_lengths) == 0:
        retval = 0.0
    else:
        if (closure_lengths > maximum_closure_length).any():
            retval = 0.0
        else:
            retval = 1.0
    return retval


def single_closure(seq,
                   open_tract_area_threshold=DEFAULT_OPEN_TRACT_AREA_THRESHOLD):
    assert len(seq) == 1 and not seq.empty
    tubes = vtl.tube(seq.iloc[0][VOCALTRACT_PARAMS]).tubes
    closure_lengths = np.array(_contiguous_closure_lengths(tubes,
                                                           open_tract_area_threshold))
    if len(closure_lengths) == 1:
        return 1.0
    return 0.0


def zero(*args):
    return 0.0


def one(*args):
    return 1.0


def coart(seq, speakerbounds, articcomps):
    """return value in [0.0, 1.0]"""
    assert not seq.empty
    normseq = utils.normalise_minmax(seq, pd.DataFrame(speakerbounds), lb=0.0, ub=1.0)
    dist = 0.0
    for segdim_a, segdim_b in articcomps:
        lab_a, param_a = segdim_a.split("-")
        lab_b, param_b = segdim_b.split("-")
        val_a = float(normseq.loc[pd.IndexSlice[:, lab_a], param_a])
        val_b = float(normseq.loc[pd.IndexSlice[:, lab_b], param_b])
        dist += abs(val_a - val_b)
    return dist / len(articcomps)


def articvec(seq, spec):
    v = np.zeros(len(spec))
    for i, (seglab, func, *_) in enumerate(spec):
        segs = seq if seglab is None else seq.loc[pd.IndexSlice[:, seglab], :]
        f = func if callable(func) else globals()[func]
        v[i] = f(segs)
    return v
