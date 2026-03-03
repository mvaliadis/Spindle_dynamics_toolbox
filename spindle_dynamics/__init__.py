"""
spindle_dynamics
================

Python port of the Spindle Dynamics MATLAB toolbox.

Main public API::

    from spindle_dynamics import specify_model, preprocess_to_design_matrix

Workflow::

    model_spec = specify_model([1, 1, 0, 1], interact_select=['stage:SOphase'])

    # Default: run TF-sigma spindle detector, compute SO covariates
    X, bin_data, res_table = preprocess_to_design_matrix(
        eeg, fs, stage_val, stage_time, model_spec)

    # Optional config examples:
    cfg = {'spindle_source': 'precomputed', 'res_table': my_res_table,
           'so_covariates': 'precomputed'}
    X, bin_data, res_table = preprocess_to_design_matrix(
        eeg, fs, stage_val, stage_time, model_spec, cfg=cfg)

    cfg = {'spindle_source': 'tf_sigma', 'so_covariates': 'none'}
    X, bin_data, res_table = preprocess_to_design_matrix(
        eeg, fs, stage_val, stage_time, model_spec, cfg=cfg)

    cfg = {'spindle_source': 'tf_sigma', 'use_stim': True,
           'stim_times': my_stim_times}
    X, bin_data, res_table = preprocess_to_design_matrix(
        eeg, fs, stage_val, stage_time, model_spec, cfg=cfg)

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

from .model import specify_model, build_design_matrix
from .pipeline import preprocess_to_design_matrix, eeg_to_event_signal
from .binning import raw_to_bin_data
from .tf_peak_detection import tf_peak_detection
from .so_power import compute_so_power
from .artifact_detection import detect_artifacts
from .multitaper import multitaper_spectrogram

__all__ = [
    'specify_model',
    'build_design_matrix',
    'preprocess_to_design_matrix',
    'eeg_to_event_signal',
    'raw_to_bin_data',
    'tf_peak_detection',
    'compute_so_power',
    'detect_artifacts',
    'multitaper_spectrogram',
]
