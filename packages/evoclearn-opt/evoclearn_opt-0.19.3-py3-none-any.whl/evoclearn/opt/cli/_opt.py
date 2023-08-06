#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO: When refactoring this PROPERLY, split the CLI interfaces into two:
# 1. Opt from acoustic template
# 2. Opt from perceptual vector

import os
import sys
import json
from functools import partial
import itertools
import pickle
import operator
from copy import deepcopy

import click
import librosa
import numpy as np

import evoclearn.core
import evoclearn.core.vocaltractlab as vtl
from evoclearn.core import log
from evoclearn.core import io
from evoclearn.core import definitions as defs
from evoclearn.core.samplers import tied_targets as tt
from evoclearn.core import mappings
from evoclearn.core import Sequence, Waveform
from evoclearn.core.features import ORIG_FEATS, ASR_FEATS
import evoclearn.rec
from evoclearn.rec import Ac2Vec

from .. import __version__
from .. import utils as opt
from .. import artic
from .. import SPEAKERS, SPEAKERS_DIR, TEMPLATES_DIR


ENERGY_FEATS = {
    "feature_type": "mfcc",
    "preemphasis": True,
    "win_length_s": 0.025,
    "hop_length_s": 0.005,
    "n_fft": 1024,
    "n_mels": 26,
    "mel_fmax": 10e3,
    "n_mfcc": 1,
    "lifter": True
}

FEATSETS = {"orig": ORIG_FEATS,
            "asr": ASR_FEATS,
            "energy": ENERGY_FEATS}
METRICS = {"euclidean",
           "cosine",
           "cityblock",
           "braycurtis",
           "mahalanobis"}
DEFAULT_TEMPLATES_DIR = os.path.join(TEMPLATES_DIR, "male-en_GB")


def template_consonant(template):
    return template[0]

def opttarget_is_vec(opttarget):
    return type(opttarget) is list

def parse_opttarget(opttarget):
    if "," in opttarget:
        return list(map(float, opttarget.split(",")))
    else:
        return opttarget

def dump_outputs(seq, basename, outdir, err_syn_func, err=None):
    err_, sound = err_syn_func(seq,
                               perturbdurs=None,
                               trajectcomps=None,
                               arttargettols=None,
                               debugdir=None)
    if sound is not None:
        wavoutpath = os.path.join(outdir, f"{basename}.wav")
        io.wav_write(sound, wavoutpath)
    tgtoutpath = os.path.join(outdir, f"{basename}.targets.json")
    with open(tgtoutpath, "w") as outf:
        outf.write(seq.to_json())
    erroutpath = os.path.join(outdir, f"{basename}.error.txt")
    with open(erroutpath, "w") as outf:
        outf.write(str(err or err_) + "\n")


def dump_debug_data(outdir,
                    base_seq,
                    err_syn_func,
                    best_seq,
                    best_err,
                    debug_data,
                    large_val,
                    logger):
    ### Dump some process outputs
    logger.info("Dumping outputs to %s...", outdir)
    dump_outputs(base_seq, "base", outdir, err_syn_func)
    dump_outputs(best_seq, "best", outdir, err_syn_func, best_err) #use original err calc
    if debug_data is not None:
        besterr_so_far = large_val
        for i, (seq, err) in enumerate(zip(debug_data["seqs"], debug_data["errs"])):
            if err < besterr_so_far:
                besterr_so_far = err
                dump_outputs(seq, f"iteration_{i}", outdir, err_syn_func, err=err) #use original err calc
        with open(os.path.join(outdir, "errors.txt"), "w") as outf:
            outf.write("\n".join(map(str, debug_data["errs"])) + "\n")
        if "synth_count" in debug_data and debug_data["synth_count"] is not None:
            with open(os.path.join(outdir, "synth_count.txt"), "w") as outf:
                outf.write(str(debug_data["synth_count"]) + "\n")
    logger.info("Done!")


#TODO: This function really needs to be refactored, especially now
#since the opttarget is not necessarily an audio template:
def load_check_speaker_template(speakersdir,
                                speaker,
                                optboundsfile,
                                templatesdir,
                                opttarget,
                                template_type,
                                rois,
                                cconstraints,
                                cpenalties,
                                precise_closures,
                                single_closure,
                                utathreshold,
                                oothreshold,
                                vvthreshold,
                                no_vconstraint,
                                vothreshold,
                                vopen_constraint,
                                logger):
    ### Loads the following data that specifies the process:
    ### 1. Template audio and alignment including ROIs if any
    ### 2. Speaker parameter bounds: absolute bounds and neutral parameters
    ### 3. Optimisation bounds: Specifies set of params to optimise for C and V
    ###    and bounds (possibly more limited than speaker bounds)
    ### 4. Prepare set of "post-sampling" constraint functions and kwargs for
    ###    template/consonant/speaker and selected options.
    ### 5. Define penalty functions that become part of the objective function
    ### 6. Speaker file used by VTL
    if not opttarget_is_vec(opttarget):
        # 1:
        alignfile = os.path.join(templatesdir, f"{opttarget}.TextGrid")
        soundfile = os.path.join(templatesdir, f"{opttarget}.wav")
        logger.info("Template audio file: %s", soundfile)
        logger.info("Template alignment file: %s", alignfile)
        durs = io.read_durations_from_textgrid(alignfile, tier="1")[:len(template_type)]
        rois = opt.read_roi_intervals_from_textgrid(alignfile, rois) if rois is not None else None
        ref_snd, ref_samplerate = librosa.load(soundfile)
        ref_snd = ref_snd[:int(ref_samplerate * sum(durs))]
        ref_wave = Waveform(ref_snd, ref_samplerate)
    else:
        durs = None
        rois = None
        ref_wave = None
    # 2:
    speakerboundsfilename = os.path.join(speakersdir,
                                         speaker,
                                         f"speaker.bounds.json")
    with open(speakerboundsfilename) as infh:
        speakerbounds, speakerconstraintsettings = io.load_bounds_constraints(infh)
    # 3:
    if optboundsfile is None:
        if template_type == list("CV"):
            consonant = template_consonant(opttarget) if template_type == list("CV") else None
            optboundsfilename = os.path.join(speakersdir,
                                             speaker,
                                             f"Vstd_C{consonant}.bounds.json")
            logger.info("Loading DEFAULT optbounds for CV-TEMPLATE for this speaker: %s",
                        optboundsfilename)
        elif template_type == list("V"):
            optboundsfilename = os.path.join(speakersdir,
                                             speaker,
                                             f"Vstd.bounds.json")
            logger.info("Loading DEFAULT optbounds for V-TEMPLATE for this speaker: %s",
                        optboundsfilename)
        with open(optboundsfilename) as infh:
            optbounds = json.load(infh)
    else:
        logger.info("Loading SPECIFIC optbounds file: %s", optboundsfile)
        with open(optboundsfile) as infh:
            optbounds = json.load(infh)
    # 4: DEMIT TODO: This section should look more like the
    #penaltyfuncs section, where we construct all the partial
    #functions with the relevant parameters instead of passing along a
    #conglomerate kwargs dict which relies on cooperative interfaces
    #of these functions. This was historically done to be able to use
    #different functions with similar functionality in constrained
    #optimisation algorithms which used floating point return values
    #-- OBSOLETE because all cases now use constraint functions
    #that return floats.
    constraintfuncs = ([] if no_vconstraint
                       else (["vowel_voiced"] if "V"
                             in template_type else []))
    if "C" in template_type and cconstraints is not None:
        constraintfuncs.extend(opt.C_CONSTRAINTS[cconstraints])
    if vopen_constraint:
        constraintfuncs.append("vowel_tract_open")
        speakerconstraintsettings["open_tract_area_threshold"] = vothreshold
    speakerconstraintsettings["unclosed_tract_area_threshold"] = utathreshold
    speakerconstraintsettings["volume_velocity_threshold"] = vvthreshold
    constraints = opt.Constraints(funcs=constraintfuncs, kwargs=speakerconstraintsettings)
    logger.info("Post-sampling constraints: %s", constraints)
    # 5:
    penaltyfuncs = []
    if "C" in template_type:
        if cpenalties is not None:
            penfuncs = []
            cpenfuncs = []
            for fname in opt.C_CONSTRAINTS[cpenalties]:
                f = getattr(opt.constr_float, fname)
                cpenfuncs.append(partial(f, **speakerconstraintsettings))
            if precise_closures:
                f = opt.constr_float.consonant_precise_closures
                penfuncs.append(partial(opt.and_funcs, funcs=cpenfuncs + [f]))
            if single_closure:
                f = opt.constr_float.consonant_single_closure
                penfuncs.append(partial(opt.and_funcs, funcs=cpenfuncs + [f]))
            if oothreshold is not None:
                ff = getattr(opt.constr_float, opt.C_OPEN_CONSTRAINTS[cpenalties])
                f = partial(ff,
                            other_open_tract_area_threshold=oothreshold,
                            **speakerconstraintsettings)
                penfuncs.append(partial(opt.and_funcs, funcs=cpenfuncs + [f]))
            penaltyfuncs.extend(cpenfuncs)
            penaltyfuncs.extend(penfuncs)
        elif cconstraints is not None:
            if precise_closures:
                penaltyfuncs.append(opt.constr_float.consonant_precise_closures)
            if single_closure:
                penaltyfuncs.append(opt.constr_float.consonant_single_closure)
            if oothreshold is not None:
                f = getattr(opt.constr_float, opt.C_OPEN_CONSTRAINTS[cconstraints])
                penaltyfuncs.append(partial(f,
                                            other_open_tract_area_threshold=oothreshold,
                                            **speakerconstraintsettings))
        else:
            pass #all currently depend on either cpenalties or cconstraints being defined
    penaltyfuncs = penaltyfuncs or None
    logger.info("Objective penalty functions: %s", penaltyfuncs)
    # 6:
    speakerfilename = os.path.join(speakersdir,
                                   speaker,
                                   f"speaker.xml")

    return speakerfilename, speakerbounds, constraints, penaltyfuncs, optbounds, durs, ref_wave, rois


def setup_featset(featset, winlen, hoplen):
    feat_settings = dict(FEATSETS[featset])
    if featset in {"asr", "orig"}:
        if winlen is not None:
            feat_settings["n_fft"] = None
            feat_settings["win_length_s"] = winlen
        if hoplen is not None:
            feat_settings["hop_length_s"] = hoplen
    elif featset == "est":
        if winlen is not None:
            feat_settings["winlen"] = winlen
        if hoplen is not None:
            feat_settings["winstep"] = hoplen
    return feat_settings


def make_ac_err_syn_function(featset,
                             winlen,
                             hoplen,
                             ref_wave,
                             vtln_warpfactor,
                             vtln_apply_to_template,
                             durs,
                             perturbdurs,
                             metric,
                             use_dtw,
                             rois,
                             trajectcomps,
                             seed,
                             speakerbounds,
                             proprioceptive_tolerance,
                             debugdir,
                             logger):
    ### Define target feat settings and objective function
    # Feats:
    feat_settings = setup_featset(featset, winlen, hoplen)
    logger.info("Feature settings: %s", str(feat_settings))

    def feattrack(sound_samples, articvec=None, **kwargs):
        if articvec is not None:
            raise NotImplementedError
        return mappings.feattrack(sound_samples, **kwargs)
    get_features = partial(feattrack, **feat_settings)

    if vtln_apply_to_template:
        ref_feats = get_features(ref_wave.samples,
                                 audio_samplerate=ref_wave.samplerate,
                                 warp_alpha=vtln_warpfactor)
        vtln_warpfactor = None
    else:
        ref_feats = get_features(ref_wave.samples,
                                 audio_samplerate=ref_wave.samplerate)

    # Objective:
    logger.info(f"Objective settings: "
                f"metric={metric.upper()}; use_dtw={use_dtw}; rois={rois}")
    obj_kwargs = {"reference": ref_feats}
    if use_dtw:
        obj_kwargs["distf"] = mappings.dist_dtw
        obj_kwargs["max_frames_diff"] = None
    else:
        obj_kwargs["pad_sample"] = True
        obj_kwargs["distf"] = mappings.dist_fbf
    obj_kwargs["metric"] = metric
    if metric == "mahalanobis":
        refcov = np.cov(ref_feats.to_numpy().T)
        refcovinv = np.linalg.inv(refcov)
        obj_kwargs["VI"] = refcovinv
    if metric == "braycurtis":
        obj_kwargs["aggf"] = lambda x: np.mean(x)
    if metric == "cosine":
        obj_kwargs["aggf"] = lambda x: np.mean(x)
    if rois is not None:
        obj_kwargs["rois"] = rois
    get_error = partial(mappings.objective, **obj_kwargs)

    # Construct err_synth function
    if perturbdurs is not None:
        rng = np.random.RandomState(seed)
    else:
        rng = None
    err_syn_func = partial(opt.err_synth,
                           durs=np.array(durs),
                           perturbdurs=None if perturbdurs is None else np.array(perturbdurs),
                           get_features=get_features,
                           get_error=get_error,
                           vtln_warpfactor=vtln_warpfactor,
                           trajectcomps=trajectcomps,
                           parammagnitudes=io.parammagnitudes_from_bounds(speakerbounds),
                           proprioceptive_tolerance=proprioceptive_tolerance,
                           large_val=opt.AC_LARGE_VAL,
                           rng=rng,
                           debugdir=debugdir)
    return err_syn_func


def make_articvec_func(articvecspec, speakerbounds, articcomps):
    for i in range(len(articvecspec)):
        funcname = articvecspec[i][1]
        if funcname.startswith("coart"):
            if speakerbounds is None or articcomps is None:
                raise Exception("Need speakerbounds and articcomps for artic.coart*()")
            articvecspec[i][1] = partial(getattr(artic, funcname),
                                         speakerbounds=speakerbounds,
                                         articcomps=articcomps)
    return partial(artic.articvec, spec=articvecspec)


def make_vec_err_syn_function(ac2vec,
                              opttarget,
                              durs,
                              perturbdurs,
                              metric,
                              vecwts,
                              articcomps,
                              articvecspec,
                              penaltyfuncs,
                              trajectcomps,
                              arttargettols,
                              seed,
                              speakerbounds,
                              proprioceptive_tolerance,
                              large_val,
                              debugdir,
                              logger):
    logger.info("Using Ac2Vec...")
    if opttarget_is_vec(opttarget):
        ref_vec = opttarget
    else:
        if articvecspec is not None: raise NotImplementedError
        ref_vec = opt.wave_to_vec(opttarget, ac2vec=ac2vec)
    vec_loss = partial(opt.vec_loss, ref_vec=ref_vec, metric=metric)
    if vecwts is not None:
        if articvecspec is None:
            assert vecwts is None or len(vecwts) == len(ac2vec.segdims)
            partdims = ac2vec.segdims
        else:
            assert vecwts is None or len(vecwts) == len(ac2vec.segdims) + 1
            partdims = [len(articvecspec)] + ac2vec.segdims
        vec_loss = partial(vec_loss, partdims=partdims, partwts=vecwts)

    def to_vec(samples, ac2vec, articvec=None, **kwargs):
        if articvec is None:
            retvec = opt.wave_to_vec(Waveform(samples, vtl.AUDIO_SAMPLERATE), ac2vec=ac2vec)
        else:
            veclen = len(articvec) + sum(ac2vec.segdims)
            retvec = np.zeros(veclen)
            retvec[:len(articvec)] = articvec
            if samples is not None:
                retvec[len(articvec):] = opt.wave_to_vec(Waveform(samples, vtl.AUDIO_SAMPLERATE), ac2vec=ac2vec)
            else:
                retvec[len(articvec):] = opt.VEC_LARGE_COORD
        return retvec

    if articvecspec is None:
        get_articvec = None
        articvec_is_okay = None
    else:
        get_articvec = make_articvec_func(deepcopy(articvecspec), speakerbounds, articcomps)
        def articvec_is_okay(articvec, spec):
            for i, (*_, op, thresh) in enumerate(spec):
                if thresh is not None and not getattr(operator, op)(articvec[i], thresh):
                    return False
            return True
        articvec_is_okay = partial(articvec_is_okay, spec=articvecspec)

    if articcomps is not None and articvecspec is None:
        get_artcoef = partial(opt.artcoef,
                              speakerbounds=speakerbounds,
                              articcomps=articcomps)
    else:        
        get_artcoef = None

    if arttargettols is not None or perturbdurs is not None:
        rng = np.random.RandomState(seed)
    else:
        rng = None
    err_syn_func = partial(opt.err_synth,
                           durs=np.array(durs),
                           perturbdurs=None if perturbdurs is None else np.array(perturbdurs),
                           get_features=partial(to_vec, ac2vec=ac2vec),
                           get_error=vec_loss,
                           get_artcoef=get_artcoef,
                           get_articvec=get_articvec,
                           articvec_is_okay=articvec_is_okay,
                           penaltyfuncs=penaltyfuncs,
                           trajectcomps=trajectcomps,
                           arttargettols=arttargettols,
                           parammagnitudes=io.parammagnitudes_from_bounds(speakerbounds),
                           proprioceptive_tolerance=proprioceptive_tolerance,
                           large_val=large_val,
                           rng=rng,
                           debugdir=debugdir)
    return err_syn_func


@click.command()
@click.option("--speaker",
              default="JD2",
              show_default=True,
              type=click.Choice(list(SPEAKERS)))
@click.option("--featset",
              default="asr",
              show_default=True,
              type=click.Choice(list(FEATSETS)))
@click.option("--vtln_warpfactor", type=click.FloatRange(min=opt.VTLN_MIN,
                                                         max=opt.VTLN_MAX))
@click.option("--vtln_apply_to_template", is_flag=True)
@click.option("--winlen", type=float, help="Override the window length (s) in feature settings")
@click.option("--hoplen", type=float, help="Override the step length (s) in feature settings")
@click.option("--seed", type=int)
@click.option("--maxiter",
              type=int)
@click.option("--synthn",
              type=int)
@click.option("--random_init",
              type=float)
@click.option("--syndurs",
              type=str,
              help="Use these instead of template durations (example: '0.2,0.4')")
@click.option("--perturbdurs",
              type=str,
              help="Randomly perturb duration around specified duration (deviating by max specified)")
@click.option("--use_dtw",
              is_flag=True)
@click.option("--debug",
              is_flag=True)
@click.option("--proprioceptive_tolerance",
              default=opt.PROPRIOCEPTIVE_TOLERANCE,
              show_default=True,
              type=float,
              help="This is the tolerance for a trajectory to be said to achieve a target")
@click.option("--vvthreshold",
              default=opt.VOLUME_VELOCITY_THRESHOLD,
              show_default=True,
              type=float,
              help="This affects the constraint applied to the vowel to ensure voicing")
@click.option("--no_vconstraint",
              is_flag=True,
              help="This disables the voicing constraint for vowels")
@click.option("--vothreshold",
              default=opt.OPEN_TRACT_AREA_THRESHOLD,
              show_default=True,
              type=float,
              help="This is the minimum tube area for the tract to be considered open")
@click.option("--vopen_constraint",
              is_flag=True)
@click.option("--cconstraints",
              type=click.Choice(list(opt.C_CONSTRAINTS)))
@click.option("--single_closure",
              is_flag=True,
              help="Only sensible in combination with --cconstraints")
@click.option("--cpenalties",
              type=click.Choice(list(opt.C_CONSTRAINTS)),
              help="Apply the constraint functions as in --cconstraints but still performs synthesis and just adds a penalty if not satisfied")
@click.option("--precise_closures",
              is_flag=True)
@click.option("--utathreshold",
              default=opt.UNCLOSED_TRACT_AREA_THRESHOLD,
              show_default=True,
              type=float,
              help="If not None, the c-constraint enforces an exclusive closure at the location")
@click.option("--oothreshold",
              type=float,
              help="Will add a penalty to the objfunc if multiple closures made (only usable with SPECIFIC --cconstraints or --cpenalties)")
@click.option("--copy_v",
              is_flag=True,
              help="Copies all 'V' parameters to other segments")
@click.option("--preserve_params",
              type=str,
              help="Used when specifying --copy_v to preserve certain "
              "parameters (needs to be comma-separated in 'seg-param' format)")
@click.option("--metric",
              default="euclidean",
              show_default=True,
              type=click.Choice(list(METRICS)))
@click.option("--algo",
              default="nlopt.crs",
              show_default=True,
              type=click.Choice(list(opt.ALGOS)))
@click.option("--rois",
              type=str,
              help="The template TextGrid 'rois' tier labels used by the objective calculation")
@click.option("--ac2vecfile",
              type=click.Path(exists=True))
@click.option("--vecwts",
              type=str,
              help="If specified, the loss function will weight distances by subvec (artic/segment)")
@click.option("--veclrgval",
              type=float)
@click.option("--speakersdir",
              default=SPEAKERS_DIR,
              show_default=True,
              type=click.Path(exists=True))
@click.option("--templatesdir",
              default=os.path.join(TEMPLATES_DIR, "male-en_GB"),
              show_default=True,
              type=click.Path(exists=True))
@click.option("--outdir",
              type=click.Path(exists=True))
@click.option("--optboundsfile",
              type=click.Path(exists=True))
@click.option("--articcompsfile",
              type=click.Path(exists=True))
@click.option("--articvecfile",
              type=click.Path(exists=True))
@click.option("--trajectcompsfile",
              type=click.Path(exists=True))
@click.option("--arttargettolsfile",
              type=click.Path(exists=True))
@click.option("--template_type",
              type=str)
@click.argument("opttarget", type=str)
def main(speaker,
         featset,
         vtln_warpfactor,
         vtln_apply_to_template,
         winlen,
         hoplen,
         seed,
         maxiter,
         synthn,
         random_init,
         syndurs,
         perturbdurs,
         use_dtw,
         debug,
         proprioceptive_tolerance,
         vvthreshold,
         no_vconstraint,
         vothreshold,
         vopen_constraint,
         cconstraints,
         single_closure,
         cpenalties,
         precise_closures,
         utathreshold,
         oothreshold,
         copy_v,
         preserve_params,
         metric,
         algo,
         rois,
         ac2vecfile,
         vecwts,
         veclrgval,
         speakersdir,
         templatesdir,
         outdir,
         optboundsfile,
         articcompsfile,
         articvecfile,
         trajectcompsfile,
         arttargettolsfile,
         template_type,
         opttarget):
    logger = log.getLogger("evl.opt")

    opttarget = parse_opttarget(opttarget)

    if ac2vecfile is not None:
        ### If ac2vecfile is given, then some of the settings meant for
        ### acoustic optimisation is not relevant (or implemented yet):
        if vtln_warpfactor is not None:
            raise NotImplementedError("Specifying --vtln_warpfactor with --ac2vecfile")
        if winlen is not None or hoplen is not None:
            raise click.UsageError("--winlen and --hoplen not sensible with --ac2vecfile")
        if use_dtw:
            raise click.UsageError("--use_dtw not sensible with --ac2vecfile")
        if rois is not None:
            raise click.UsageError("--rois not sensible with --ac2vecfile")
        if vecwts is not None:
            vecwts = list(map(float, vecwts.split(",")))
        featset = None
        use_dtw = None
    else:
        if precise_closures:
            raise NotImplementedError
        if oothreshold:
            raise NotImplementedError
        if cpenalties:
            raise NotImplementedError
        if vecwts:
            raise click.UsageError("--vecwts not sensible without --ac2vecfile")
        if arttargettolsfile is not None:
            raise NotImplementedError
        if articvecfile is not None:
            raise click.UsageError("--articvecfile cannot be used without --ac2vecfile")
        if not use_dtw and perturbdurs is not None:
            raise click.UsageError("Acoustic comparison cannot --perturbdurs without --use_dtw")

    if opttarget_is_vec(opttarget):
        if optboundsfile is None:
            raise click.UsageError("Need to specify --optboundsfile if optimisation target is perceptual vector")
        if ac2vecfile is None:
            raise click.UsageError("Need to specify --ac2vecfile if optimisation target is a perceptual vector")
        if syndurs is None:
            raise click.UsageError("Need to specify --syndurs if optimisation target is perceptual vector")
    else:
        if articvecfile is not None:
            raise click.UsageError("If using --articvecfile then opttarget needs to be a vec")

    if cpenalties is not None and cconstraints is not None:
        raise click.UsageError("--cconstraints not sensible with --cpenalties")

    if cconstraints is None and cpenalties is None:
        if precise_closures:
            raise click.UsageError("--precise_closures not sensible without --cconstraints or --cpenalties")
        if single_closure:
            raise click.UsageError("--single_closure not sensible without --cconstraints or --cpenalties")

    if oothreshold is not None:
        if utathreshold is not None:
            raise click.UsageError("--oothreshold not sensible with --utathreshold")
        if cconstraints not in opt.C_OPEN_CONSTRAINTS and cpenalties not in opt.C_OPEN_CONSTRAINTS:
            raise click.UsageError("--oothreshold should be used with SPECIFIC --cconstraints or --cpenalties")

    if synthn is not None:
        if maxiter is not None:
            raise click.UsageError("Choose either --maxiter or --synthn")
        if not algo == "hpopt.tpe":
            raise NotImplementedError

    ### Save all settings
    if outdir is not None:
        cli_params = json.dumps({"speaker": speaker, "featset": featset, "vtln_warpfactor": vtln_warpfactor,
                                 "vtln_apply_to_template": vtln_apply_to_template, "winlen": winlen,
                                 "hoplen": hoplen, "seed": seed, "maxiter": maxiter, "synthn": synthn, "random_init": random_init,
                                 "syndurs": syndurs, "perturbdurs": perturbdurs,
                                 "use_dtw": use_dtw, "cconstraints": cconstraints, "cpenalties": cpenalties,
                                 "precise_closures": precise_closures, "single_closure": single_closure,
                                 "utathreshold": utathreshold, "vothreshold": vothreshold, "oothreshold": oothreshold,
                                 "vvthreshold": vvthreshold, "no_vconstraint": no_vconstraint, "vopen_constraint": vopen_constraint,
                                 "proprioceptive_tolerance": proprioceptive_tolerance,
                                 "copy_v": copy_v, "preserve_params": preserve_params, "metric": metric, "algo": algo,
                                 "rois": rois, "ac2vecfile": ac2vecfile, "vecwts": vecwts,
                                 "speakersdir": speakersdir, "templatesdir": templatesdir,
                                 "outdir": outdir, "optboundsfile": optboundsfile, "articcompsfile": articcompsfile,
                                 "articvecfile": articvecfile,
                                 "trajectcompsfile": trajectcompsfile, "arttargettolsfile": arttargettolsfile,
                                 "template_type": template_type, "opttarget": opttarget,
                                 "evl_core": evoclearn.core.__version__, "evl_opt": __version__,
                                 "evl_rec": evoclearn.rec.__version__},
                                indent=2)
        with open(os.path.join(outdir, "cli_params.json"), "w") as outfh:
            outfh.write(cli_params)

    #
    if template_type is not None:
        if "," in template_type:
            template_type = template_type.split(",")
        else:
            template_type = list(template_type)

    ### Establish the base sequence, it serves two purposes:
    ### 1. Used as a fallback for any parameters that are not specified during
    ###    the optimisation process.
    ### 2. Given as the starting point for the optimisation process and
    ###    especially relevant to the local optimisation algorithms implemented
    ###    in NLOpt.
    #Try to load from STDIN first, then fall back to neutral params defined in
    #speakerbounds
    speakerboundsfilename = os.path.join(speakersdir,
                                         speaker,
                                         f"speaker.bounds.json")
    with open(speakerboundsfilename) as infh:
        speakerbounds = io.load_bounds(infh)
    if sys.stdin.isatty():
        stdin_string = ""
    else:
        stdin_string = sys.stdin.read()
    if not stdin_string.strip():
        if template_type is None:
            raise click.UsageError("Need to provide either base sequence "
                                   "via STDIN or --template_type")
        logger.info("Base sequence from speaker NEUTRAL parameters...")
        base_seq = io.default_sequence_from_bounds(speakerbounds, labels=template_type)
    else:
        if template_type is not None:
            logger.warning("Need to provide EITHER base sequence "
                           "via stdin OR --template_type (USING BASESEQ)")
        logger.info("Base sequence from STDIN...")
        base_seq = Sequence.from_json(stdin_string)
        template_type = list(base_seq.index.get_level_values("lab"))

    #
    if vtln_warpfactor is not None:
        logger.info("VTLN warpfactor: %s applied to %s",
                    vtln_warpfactor,
                    "TEMPLATE" if vtln_apply_to_template else "SYNTH")
    else:
        logger.info("No VTLN...")

    #
    rois = set(rois.split(",")) if rois is not None else None

    #
    (speakerfilename,
     speakerbounds,
     postsampling_constraints,
     objective_penalty_funcs,
     optbounds,
     durs,
     ref_wave,
     rois) = load_check_speaker_template(speakersdir,
                                         speaker,
                                         optboundsfile,
                                         templatesdir,
                                         opttarget,
                                         template_type,
                                         rois,
                                         cconstraints,
                                         cpenalties,
                                         precise_closures,
                                         single_closure,
                                         utathreshold,
                                         oothreshold,
                                         vvthreshold,
                                         no_vconstraint,
                                         vothreshold,
                                         vopen_constraint,
                                         logger)

    if syndurs is not None:
        syndurs = list(map(float, syndurs.split(",")))
        if durs is not None:
            assert len(syndurs) == len(durs)

    if perturbdurs is not None:
        perturbdurs = list(map(float, perturbdurs.split(",")))
        if durs is not None:
            assert len(perturbdurs) == len(durs)
        if syndurs is not None:
            assert len(perturbdurs) == len(syndurs)

    if articcompsfile is not None:
        with open(articcompsfile) as infh:
            articcomps = json.load(infh)
    else:
        articcomps = None

    if articvecfile is not None:
        with open(articvecfile) as infh:
            articvecspec = json.load(infh)
    else:
        articvecspec = None

    if trajectcompsfile is not None:
        with open(trajectcompsfile) as infh:
            trajectcomps = json.load(infh)
    else:
        trajectcomps = None

    if arttargettolsfile is not None:
        with open(arttargettolsfile) as infh:
            arttargettols = json.load(infh)
    else:
        arttargettols = None

    if ac2vecfile is None:
        if articcomps is not None:
            raise NotImplementedError("Not implemented --articcompsfile without --ac2vecfile")
        if articvecspec is not None:
            raise NotImplementedError("Not implemented --articvecfile without --ac2vecfile")
        if objective_penalty_funcs is not None:
            raise NotImplementedError
        err_syn_func = make_ac_err_syn_function(featset,
                                                winlen,
                                                hoplen,
                                                ref_wave,
                                                vtln_warpfactor,
                                                vtln_apply_to_template,
                                                syndurs or durs,
                                                perturbdurs,
                                                metric,
                                                use_dtw,
                                                rois,
                                                trajectcomps,
                                                seed,
                                                speakerbounds,
                                                proprioceptive_tolerance,
                                                outdir if debug else None,
                                                logger)
    else:
        ac2vec = Ac2Vec.from_file(ac2vecfile)
        large_val = veclrgval if veclrgval is not None else opt.VEC_LARGE_VAL
        err_syn_func = make_vec_err_syn_function(ac2vec,
                                                 ref_wave or opttarget,
                                                 syndurs or durs,
                                                 perturbdurs,
                                                 metric,
                                                 vecwts,
                                                 articcomps,
                                                 articvecspec,
                                                 objective_penalty_funcs,
                                                 trajectcomps,
                                                 arttargettols,
                                                 seed,
                                                 speakerbounds,
                                                 proprioceptive_tolerance,
                                                 large_val,
                                                 outdir if debug else None,
                                                 logger)
    def err_func(*args, **kwargs):
        return err_syn_func(*args, **kwargs)[0]

    ### Set up param <-> seq functions:
    if not copy_v and preserve_params is not None:
        raise click.UsageError("--preserve_params not sensible without --copy_v")
    if preserve_params == "std":
        if opttarget_is_vec(opttarget):
            raise click.NotImplementedError("Cannot determine opttarget consonant from vec (yet)...")
        preserve_params = [f"C-{param}"
                           for param
                           in opt.C_VARPARAMS[template_consonant(opttarget)]]
    elif preserve_params is not None:
        preserve_params = preserve_params.split(",")
        if not all("-" in pk for pk in preserve_params):
            raise click.UsageError("--preserve_params should use format {lab}-{param}")
    logger.info("Tied params settings: (copy_v=%s, preserve_params=%s)",
                copy_v,
                preserve_params)
    copy_src = "V" if copy_v else None
    p2s_func = partial(
        opt.params_to_seq,
        label_construction_order=tt.reorder_labels_for_construction(list(template_type),
                                                                    copy_src),
        copy=copy_src,
        preserve_params=preserve_params
    )
    s2p_func = tt.sequence_to_paramvalues

    ### Initialise and run optimisation process:
    large_val = (opt.AC_LARGE_VAL
                 if ac2vecfile is None
                 else opt.VEC_LARGE_VAL)
    vtl.initialise(speakerfilename)
    #TODO: translate opttarget into human-readable format:
    logger.info("Starting optimisation... (template_type=%s, opttarget=%s, algo=%s, maxiter=%s, synthn=%s, random_init=%s, seed=%s)",
                template_type, opttarget, algo, maxiter, synthn, random_init, seed)
    (best_seq,
     best_err,
     debug_data) = opt.optimise(base_seq,
                                optbounds,
                                err_func,
                                p2s_func,
                                s2p_func,
                                algo,
                                maxiter,
                                synthn,
                                random_init,
                                postsampling_constraints,
                                large_val,
                                seed)
    logger.info("Optimisation DONE!")
    if outdir is not None:
        dump_debug_data(outdir,
                        base_seq,
                        err_syn_func,
                        best_seq,
                        best_err,
                        debug_data,
                        large_val,
                        logger)

    if not sys.stdout.isatty():
        sys.stdout.write(best_seq.to_json())


if __name__ == "__main__":
    main()
