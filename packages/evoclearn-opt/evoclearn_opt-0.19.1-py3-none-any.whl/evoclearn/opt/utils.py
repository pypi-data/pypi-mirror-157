# -*- coding: utf-8 -*-

import os, sys
from typing import Optional, Callable, List, Tuple
from functools import partial, reduce
import json
import time
from collections import namedtuple

import numpy as np
import pandas as pd
from scipy.spatial import distance
import nlopt
import hyperopt as hpopt
hpopt.progress.default_callback = hpopt.progress.no_progress_callback

from praatio import textgrid as tgio
import librosa

from evoclearn.core import Sequence, Waveform
from evoclearn.core import samplers
from evoclearn.core.samplers import tied_targets as tt
from evoclearn.core import mappings
from evoclearn.core import utils
from evoclearn.core import log
from evoclearn.core import io
from evoclearn.core import constraints as constr
from evoclearn.core.constraints import generic as constr_float
from evoclearn.core import vocaltractlab as vtl
from evoclearn.rec import Ac2Vec
from . artic import coart as artcoef


LOGGER = log.getLogger("evl.opt")

Constraints = namedtuple("Constraints", ["funcs", "kwargs"])

ALGOS = {"nlopt.isres",
         "nlopt.direct",
         "nlopt.directl",
         "nlopt.crs",
         "nlopt.esch",
         "nlopt.cobyla",
         "nlopt.bobyqa",
         "hpopt.tpe"}


INF_INT = int(10e10)
AC_LARGE_VAL = 1e8
VEC_LARGE_VAL = 1e2
VEC_LARGE_COORD = 10.0 #coords usually in the range [0.0, 1.0]
FLOAT_TOL = 1e-8
VTLN_MIN = 0.1
VTLN_MAX = 1.8
PROPRIOCEPTIVE_TOLERANCE = 0.01
ARTTARGETTOLS_NUM_SAMPLES = 5

STD_VARPARAMS = {"JD2": {"HX", "HY",
                         "JX", "JA",
                         "LP", "LD",
                         "VS",
                         "TCX", "TCY",
                         "TTX", "TTY",
                         "TBX", "TBY",
                         #"TRX", "TRY",
                         "TS1", "TS2", "TS3",
                         "vt_tau_s"},
                 "boy3": {"HX", "HY",
                          "JX", "JA",
                          "LP", "LD",
                          "VS",
                          "TCX", "TCY",
                          "TTX", "TTY",
                          "TBX", "TBY",
                          "TRX", "TRY",
                          "TS1", "TS2", "TS3",
                          "vt_tau_s"}}

C_VARPARAMS = {
    "b": {"JX", "JA", "LD", "vt_tau_s"},
    "d": {"JX", "JA", "TTX", "TTY", "TBX", "TBY", "TS3", "vt_tau_s"},
    "g": {"JX", "JA", "TCY", "TS2", "vt_tau_s"}
}

C_CONSTRAINTS = {
    "b": ["consonant_lip_closure"],
    "d": ["consonant_tongue_tip_closure"],
    "g": ["consonant_tongue_body_closure"],
    "any": ["consonant_any_closure"],
    "any_open_mouth": ["consonant_any_closure", "consonant_mouth_open"]
}

C_OPEN_CONSTRAINTS = {
    "b": "consonant_other_than_lip_open",
    "d": "consonant_other_than_tongue_tip_open",
    "g": "consonant_other_than_tongue_body_open"
}


#This threshold is used in the consonant closure constraints in
#evl-core and is defined with a default value there to ensure that we
#__only__ form a closure at the location enforced by the constraint
#function, this is useful when using these constraints to sample CVs
#without optimisation. HERE IN EVL-OPT, however, we want to use the
#constraint functions only to ensure that a closure is indeed formed
#at the location, but rely on the optimisation process to dictate any
#further detail.
UNCLOSED_TRACT_AREA_THRESHOLD = None

#This is the threshold we use in the `vowel_voiced` constraint to
#ensure we have a voiced sound:
VOLUME_VELOCITY_THRESHOLD = constr_float.DEFAULT_VOLUME_VELOCITY_THRESHOLD

OPEN_TRACT_AREA_THRESHOLD = constr_float.DEFAULT_OPEN_TRACT_AREA_THRESHOLD


def and_funcs(x, funcs):
    for f in funcs:
        val = f(x)
        if val > 0.0:
            return val
    return val


def read_roi_intervals_from_textgrid(path: str, rois: set, tier: str="rois") -> List[Tuple[float]]:
    tg = tgio.openTextgrid(path, includeEmptyIntervals=False)
    intervals = [(e.start, e.end) for e in tg.tierDict[tier].entryList if e.label.strip() in rois]
    return intervals


def params_to_seq(paramvals, paramkeys,
                  baseseq, label_construction_order,
                  copy=None, preserve_params=None):
    params = dict(zip(paramkeys, paramvals))
    seq = tt.params_to_sequence(params,
                                baseseq=baseseq,
                                copy=copy,
                                label_construction_order=label_construction_order)
    if preserve_params is not None:
        for paramkey in preserve_params:
            lab, param = paramkey.split("-")
            idx = pd.IndexSlice[:, lab]
            seq.loc[idx, param] = baseseq.loc[idx, param]
    return seq


def wave_to_vec(waveform: Waveform, ac2vec: Ac2Vec) -> np.ndarray:
    return list(ac2vec([waveform], from_wav=True))[0]


def vec_loss(vec, ref_vec, metric, partdims=None, partwts=None, aggf=np.mean):
    if partdims is None:
        X = np.zeros((2, len(ref_vec)), dtype=float)
        X[0] = ref_vec
        X[1] = vec
        return float(distance.pdist(X, metric=metric)[0])
    partdists = np.zeros(len(partdims))
    i0 = 0
    for i, n in enumerate(partdims):
        X = np.zeros((2, n))
        X[0] = ref_vec[i0:i0+n]
        X[1] = vec[i0:i0+n]
        partdists[i] = distance.pdist(X, metric=metric)
        i0 += n
    if partwts is not None:
        partdists *= partwts
    return float(aggf(partdists))


def err_synth(seq, durs, get_features, get_error,
              perturbdurs=None,
              get_artcoef=None,
              get_articvec=None, articvec_is_okay=None,
              penaltyfuncs=None,
              vtln_warpfactor=None,
              trajectcomps=None, arttargettols=None,
              parammagnitudes=None,
              proprioceptive_tolerance=None, large_val=None,
              syncounter=None, rng=None,
              debugdir=None):
    """in terms of a seq"""
    call_instant = int(time.time() * 1000000)
    ### New layer of threshold checks based on the articvec to see if
    ### we need to bother synthesising, if not, then we will leave the
    ### auditvec as all-zeros. This will probably supersede the
    ### original constraints system eventually
    do_synthesis = True
    if get_articvec is not None:
        articvec = get_articvec(seq)
        if not articvec_is_okay(articvec):
            do_synthesis = False
            synth_sound = None
            featvec = get_features(synth_sound, articvec=articvec)
            error = get_error(featvec)
            LOGGER.debug("Articvec only: loss=%s", error)
    else:
        articvec = None

    if do_synthesis:
        if perturbdurs is not None:
            newdurs = rng.uniform(low=durs - perturbdurs, high=durs + perturbdurs)
        else:
            newdurs = durs
        LOGGER.debug("Synthesising with durs %s...", newdurs)
        trajects_passed = True
        if trajectcomps is not None:
            full_targets = mappings.add_slope_and_duration(seq, durations=newdurs)
            vtl_curves = mappings.target_approximation(full_targets)
            for params, seglabs in trajectcomps.items():
                LOGGER.debug("Proprioceptive test: %s, %s", params, seglabs)
                if not constr.achieved_targets(vtl_curves,
                                               seq,
                                               parammagnitudes * proprioceptive_tolerance,
                                               seglabs=seglabs,
                                               params=params):
                    trajects_passed = False
                    break
        if not trajects_passed:
            LOGGER.debug("TARGETS NOT REACHED in trajectories...")
            artcoef = None
            synth_sound = None
            error = large_val
        else:
            if syncounter is not None: syncounter[0] += 1
            if arttargettols is None:
                full_targets = mappings.add_slope_and_duration(seq, durations=newdurs)
                vtl_curves = mappings.target_approximation(full_targets)
                synth_sound = mappings.synthesise_vtl_curves(vtl_curves)
                synth_feats = get_features(synth_sound,
                                           articvec=articvec,
                                           warp_alpha=vtln_warpfactor)  # warp if needed
                error = get_error(synth_feats)
            else:
                errors_samples = []
                for i in range(ARTTARGETTOLS_NUM_SAMPLES):
                    s = seq.copy()
                    for lab_param, ptol in arttargettols.items():
                        lab, param = lab_param.split("-")
                        p = s.loc[pd.IndexSlice[:, lab], param]
                        rp = rng.uniform(p - ptol, p + ptol)
                        s.loc[pd.IndexSlice[:, lab], param] = rp
                        LOGGER.debug("%s: %s-%s +- %s was %.3f now %.3f", i, lab, param, ptol, float(p), float(rp))
                    full_targets = mappings.add_slope_and_duration(s, durations=newdurs)
                    vtl_curves = mappings.target_approximation(full_targets)
                    synth_sound = mappings.synthesise_vtl_curves(vtl_curves)
                    synth_feats = get_features(synth_sound,
                                               articvec=articvec,
                                               warp_alpha=vtln_warpfactor)  # warp if needed
                    errors_samples.append(get_error(synth_feats))
                error = max(errors_samples)
            ####TODO: Gain control of the weighting:
            if get_artcoef is not None:
                artcoef = get_artcoef(seq)
                error += 0.1 * artcoef
            if penaltyfuncs:
                for pf in penaltyfuncs:
                    violation = pf(seq)
                    if violation > 0.0:
                        LOGGER.debug("Penalty applied: (func=%s) (viol=%s)", pf, violation)
                        error += 0.1 * violation
                    else:
                        LOGGER.debug("Fine: %s", pf)
        ####
        if vtln_warpfactor is None:
            LOGGER.debug("Synthesised: loss=%s", error)
        else:
            LOGGER.debug("Synthesised: vtln_warpfactor=%s loss=%s", vtln_warpfactor, error)

    if debugdir is not None:
        basename = "debug_" + str(call_instant)
        if synth_sound is not None:
            wavoutpath = os.path.join(debugdir, f"{basename}.wav")
            io.wav_write(synth_sound, wavoutpath, samplerate_hz=vtl.AUDIO_SAMPLERATE)
        erroutpath = os.path.join(debugdir, f"{basename}.error.txt")
        with open(erroutpath, "w") as outfh:
            outfh.write(str(error) + "\n")
        tgtoutpath = os.path.join(debugdir, f"{basename}.targets.json.bz2")
        seq.to_file(tgtoutpath)
        if get_artcoef is not None and artcoef is not None:
            artcoefoutpath = os.path.join(debugdir, f"{basename}.artcoef.txt")
            with open(artcoefoutpath, "w") as outfh:
                outfh.write(f"{artcoef}\n")
        if articvec is not None:
            articvecoutpath = os.path.join(debugdir, f"{basename}.articvec.txt")
            np.savetxt(articvecoutpath, articvec)

    return error, synth_sound


def err_wrap_constr(seq, *args, constraints, err_func, large_val, syncounter=None, **kwargs):
    err = None
    violations = []
    for constrfuncname in constraints.funcs:
        #LOGGER.debug("Applying %s...", constrfuncname)
        violation = getattr(constr_float, constrfuncname)(seq, **constraints.kwargs)
        if violation > 0.0:
            LOGGER.debug("Constraint not satisfied! (func=%s) (viol=%s)",
                         constrfuncname,
                         violation)
            violations.append(violation)
    if len(violations) > 0:
        LOGGER.debug("Aborted: loss=%s", large_val + sum(violations))
        err = large_val + sum(violations)

    if err is None:
        err = err_func(seq, syncounter=syncounter, *args, **kwargs)
    return err


def err_wrap_save_data(seq, *args, err_func, debug_data, **kwargs):
    call_instant = int(time.time() * 1000000)
    err = err_func(seq, *args, **kwargs)
    # store in-mem by mutating debug_data
    debug_data[call_instant] = (seq, err)
    return err


def terminate_rnd(result, maxiter, large_val):
    errs = list(map(float, result.func_vals))
    n_valid_evals = len([err for err in errs if err != large_val])
    LOGGER.debug("Number of valid calls: %s / %s", n_valid_evals, len(errs))
    if n_valid_evals >= maxiter:
        return True


def optimise_nlopt(algo_type,
                   parambounds,
                   initial_x,
                   err_func,
                   p2s,
                   maxiter: int,
                   random_init: Optional[float],
                   postsampling_constraints: Constraints,
                   large_val: float,
                   seed: Optional[int]=None,
                   debug=True):
    if random_init is not None:
        raise NotImplementedError("random_init not supported in optimise_nlopt()")
    nlopt_algo = {
        "isres": nlopt.GN_ISRES,
        "direct": nlopt.GN_ORIG_DIRECT,
        "directl": nlopt.GN_ORIG_DIRECT_L,
        "crs": nlopt.GN_CRS2_LM,
        "esch": nlopt.GN_ESCH,
        "cobyla": nlopt.LN_COBYLA,
        "bobyqa": nlopt.LN_BOBYQA
    }[algo_type]
    # Set up optimizer with constraint functions:
    nlopt.srand(seed)
    optimiser = nlopt.opt(nlopt_algo, len(parambounds))
    try:
        # FIRST try to construct constraint functions to be used directly
        # by the algorithm:
        constraintfuncs = [partial(lambda x, grad, f: float(f(p2s(x), **postsampling_constraints.kwargs)),
                                   f=getattr(constr_float, constrfuncname))
                           for constrfuncname in postsampling_constraints.funcs]
        for f in constraintfuncs:
            optimiser.add_inequality_constraint(f)
        LOGGER.debug("Added inequality constraints to the optimiser...")
    except ValueError:
        # OTHERWISE if our optimiser doesn't support ineq constraints,
        # incorp into objfunc:
        err_func = partial(err_wrap_constr,
                           constraints=postsampling_constraints,
                           err_func=err_func,
                           large_val=large_val)
        LOGGER.debug("Wrapping constraints in the objective function...")
    if debug:
        # Since NLOpt doesn't keep each iter's data like SKOpt, we do that
        # ourselves here if needed:
        debug_data = {}
        err_func = partial(err_wrap_save_data,
                           err_func=err_func,
                           debug_data=debug_data)
    # Define objective function: in addition to composing with p2s
    # we also need to change the obj func interface for NLOpt:
    objf = lambda x, grad: err_func(p2s(x))
    # Configure optimiser settings before running:
    optimiser.set_lower_bounds([bound[0] for bound in parambounds])
    optimiser.set_upper_bounds([bound[1] for bound in parambounds])
    initial_x = np.array(initial_x)
    optimiser.set_min_objective(objf)
    optimiser.set_xtol_rel(-1) #-1: disable
    optimiser.set_maxeval(maxiter)
    # Run:
    try:
        best_params = optimiser.optimize(initial_x)
        best_err = float(optimiser.last_optimum_value())
    except nlopt.RoundoffLimited:
        LOGGER.warn("Optimisation terminated due to nlopt.RoundoffLimited")
        best_seq = None
        best_err = None
    else:
        best_seq = p2s(best_params)
        # Package process data:
    if debug:
        seqs = []
        errs = []
        for k in sorted(debug_data):
            seq, err = debug_data[k]
            seqs.append(seq)
            errs.append(err)
        debug_data = {
            "seqs": seqs,
            "errs": errs
        }
        # Recover from exception if we have debug_data
        if best_seq is None:
            best_i = np.argmin(errs)
            best_err = errs[best_i]
            best_seq = seqs[best_i]
    else:
        debug_data = None
    return best_seq, best_err, debug_data


def optimise_hpopt(algo_type,
                   paramkeys,
                   parambounds,
                   initial_x,
                   err_func,
                   p2s,
                   maxiter: Optional[int],
                   synthn: Optional[int],
                   random_init: Optional[float],
                   postsampling_constraints: Constraints,
                   large_val: float,
                   seed: Optional[int]=None,
                   debug=True):
    hpopt_algo = {
        "tpe": (partial(hpopt.tpe.suggest,
                       n_startup_jobs=int((maxiter or synthn) * random_init))
                if random_init is not None
                else hpopt.tpe.suggest)
    }[algo_type]
    space = [hpopt.hp.uniform(k, b[0], b[1])
             for k, b
             in zip(paramkeys, parambounds)]
    # Incorporate any "post-sampling" constraints via the objective
    # function and log:
    if synthn is not None:
        syncounter = [0]
        early_stop_fn = partial(lambda *args, sc, sn: (sc[0] >= sn, {}),
                                sc=syncounter,
                                sn=synthn)
    else:
        syncounter = None
        early_stop_fn = None

    err_func = partial(err_wrap_constr,
                       constraints=postsampling_constraints,
                       err_func=err_func,
                       large_val=large_val,
                       syncounter=syncounter)
    if debug:
        # We manually keep each iter's data as done for NLOpt:
        debug_data = {}
        err_func = partial(err_wrap_save_data,
                           err_func=err_func,
                           debug_data=debug_data)
    objf = utils.compose_funcs(err_func, p2s)
    # Configure optimiser and run:
    best_d = hpopt.fmin(fn=objf,
                        space=space,
                        algo=hpopt_algo,
                        max_evals=maxiter or sys.maxsize,
                        rstate=(np.random.RandomState(seed)
                                if seed is not None
                                else None),
                        points_to_evaluate=[dict(zip(paramkeys, initial_x))],
                        early_stop_fn=early_stop_fn)
    best_seq = p2s([best_d[k] for k in paramkeys])
    best_err = None
    if debug:
        seqs = []
        errs = []
        for k in sorted(debug_data):
            seq, err = debug_data[k]
            seqs.append(seq)
            errs.append(err)
        debug_data = {
            "seqs": seqs,
            "errs": errs,
            "synth_count": syncounter[0] if syncounter is not None else None
        }
        best_err = min(errs)
    return best_seq, best_err, debug_data


def optimise(seq: Sequence,
             paramboundsmap: dict, #specifies seg, articparams and their bounds
             err_func: Callable[[Sequence, Optional[float]], float],
             p2s_func,
             s2p_func,
             algo,
             maxiter,
             synthn,
             random_init,
             postsampling_constraints: Constraints,
             large_val: float,
             seed: Optional[int]=None,
             debug=True):
    paramkeys = sorted(paramboundsmap)
    parambounds = [paramboundsmap[p] for p in paramkeys]
    #
    p2s = partial(p2s_func,
                  paramkeys=paramkeys,
                  baseseq=seq)
    initial_x = s2p_func(seq, paramkeys)
    #
    algo_lib, algo_type = algo.split(".")
    if algo_lib == "nlopt":
        if synthn is not None:
            raise NotImplementedError
        (best_seq,
         best_err,
         debug_data) = optimise_nlopt(algo_type,
                                      parambounds,
                                      initial_x,
                                      err_func,
                                      p2s,
                                      maxiter,
                                      random_init,
                                      postsampling_constraints,
                                      large_val,
                                      seed,
                                      debug)
    elif algo_lib == "hpopt":
        (best_seq,
         best_err,
         debug_data) = optimise_hpopt(algo_type,
                                      paramkeys,
                                      parambounds,
                                      initial_x,
                                      err_func,
                                      p2s,
                                      maxiter,
                                      synthn,
                                      random_init,
                                      postsampling_constraints,
                                      large_val,
                                      seed,
                                      debug)
    else:
        raise NotImplementedError(f"algo: {algo}")
    return best_seq, best_err, debug_data
