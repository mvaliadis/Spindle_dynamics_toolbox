"""
Convert raw EEG + stage data to a binned data dictionary.

Ported from:
    helper_function/utils/rawToBinData.m
    helper_function/utils/eegToEventSignal.m (the binning parts)

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

import numpy as np
from .utils import (
    modified_cardinal_spline,
    hist_basis,
    raw_phase_to_bin_phase,
    stage_raw_to_bin,
)


def raw_to_bin_data(res_table, fs, binsize=0.1, hard_cutoffs=(12, 16),
                    hist_choice='long'):
    """
    Convert a res_table (from eeg_to_event_signal) to a binned data dictionary.

    Parameters
    ----------
    res_table : dict
        Output of eeg_to_event_signal with keys:
        'peak_ctimes', 'peak_freqs', 'SOphase', 'SOpow',
        't', 'stages'.
    fs : float
        Sampling frequency (Hz).
    binsize : float
        Bin size in seconds (default 0.1).
    hard_cutoffs : (float, float)
        Frequency range [low, high] Hz to select fast spindles.
    hist_choice : str
        'long' (up to 90 s history) or 'short' (up to 15 s).

    Returns
    -------
    bin_data : dict
        Keys: y, sta, sop, phase, sp_hist, sp, RW, real_time,
              spindle_time_raw, isis, N2_rate, N3_rate, Fs.
    """
    # --- Unpack res_table ---
    peak_ctimes = np.asarray(res_table['peak_ctimes'], dtype=float).ravel()
    peak_freqs = np.asarray(res_table['peak_freqs'], dtype=float).ravel()
    phase_raw = np.asarray(res_table['SOphase'], dtype=float).ravel()
    sop_raw = np.asarray(res_table['SOpow'], dtype=float).ravel()
    stagetime_raw = np.asarray(res_table['t'], dtype=float).ravel()
    stages_raw = np.asarray(res_table['stages'], dtype=float).ravel()

    # Guard against missing SO covariates
    if phase_raw.size == 0:
        phase_raw = np.zeros_like(stagetime_raw)
    if sop_raw.size == 0:
        sop_raw = np.zeros_like(stagetime_raw)

    # --- Select fast spindles ---
    fast_mask = (peak_freqs >= hard_cutoffs[0]) & (peak_freqs < hard_cutoffs[1])
    spindle_time_raw = peak_ctimes[fast_mask]

    # --- Build bin edges ---
    if len(stagetime_raw) < 2:
        raise ValueError(
            "res_table['t'] must contain at least 2 time points to infer epoch length.")
    epoch = stagetime_raw[1] - stagetime_raw[0]
    total_time = stagetime_raw[-1] - stagetime_raw[0] + epoch
    timestamps = np.arange(0, total_time + binsize / 2, binsize)

    # --- Response: binary spindle train ---
    spindle_train, _ = np.histogram(spindle_time_raw, bins=timestamps)
    spindle_train = spindle_train.astype(float)

    # --- Predictors ---
    # 1) Sleep stage
    stage, stagetrain = stage_raw_to_bin(stages_raw, stagetime_raw,
                                         binsize, epoch, timestamps)

    # 2) SO phase
    phase_time_raw = np.arange(1, len(phase_raw) + 1) / fs
    SO_phase = raw_phase_to_bin_phase(
        phase_raw, fs, spindle_time_raw, spindle_train, timestamps)

    # 3) SO power
    SO_power = np.interp(
        np.arange(binsize, total_time + binsize / 2, binsize),
        phase_time_raw,
        sop_raw,
    )

    # --- Cut 5-min lights-on / lights-off buffer ---
    buffer = 300  # seconds
    nonwake = np.where(stagetrain != 5)[0]
    if len(nonwake) == 0:
        light_off_idx = 0
        light_on_idx = len(stagetrain) - 1
    else:
        light_off_idx = max(nonwake[0] - int(buffer / binsize), 0)
        light_on_idx = min(nonwake[-1] + int(buffer / binsize),
                           len(stagetrain) - 1)

    spindle_train_c = spindle_train[light_off_idx: light_on_idx + 1]
    stage_c = stage[light_off_idx: light_on_idx + 1, :]
    stagetrain_c = stagetrain[light_off_idx: light_on_idx + 1]
    sop_c = SO_power[light_off_idx: light_on_idx + 1]
    phase_c = SO_phase[light_off_idx: light_on_idx + 1]
    timestamps_c = timestamps[light_off_idx: light_on_idx + 1]

    # --- History order ---
    if hist_choice.lower() == 'short':
        hist_ord = int(15 / binsize)
        control_pt = np.concatenate([np.arange(0, 91, 15), [120, hist_ord]])
    else:
        hist_ord = int(90 / binsize)
        control_pt = np.concatenate([
            np.arange(0, 91, 15),
            [120],
            np.arange(150, 751, 100),
            [hist_ord],
        ])

    # --- History component ---
    indi_hist = hist_basis(hist_ord, spindle_train_c)

    s_tension = 0.5
    sp = modified_cardinal_spline(hist_ord, control_pt, s_tension)
    sp_hist = indi_hist @ sp

    # --- Align all arrays to history window ---
    y = spindle_train_c[hist_ord:]
    sta = stage_c[hist_ord:, :]
    sop = sop_c[hist_ord:]
    phase = phase_c[hist_ord:]
    real_time = timestamps_c[hist_ord:]
    RW = sta[:, 3] + sta[:, 4]   # REM + Wake indicator

    # --- Spindle density summaries ---
    n_bins_total = len(spindle_train_c)
    N2_mask = stagetrain_c == 2
    N3_mask = stagetrain_c == 1
    n2_denom = N2_mask.sum()
    n3_denom = N3_mask.sum()
    N2_rate = (((spindle_train_c >= 1) & N2_mask).sum() / n2_denom
               * 60 / binsize) if n2_denom > 0 else 0.0
    N3_rate = (((spindle_train_c >= 1) & N3_mask).sum() / n3_denom
               * 60 / binsize) if n3_denom > 0 else 0.0

    bin_data = {
        'y': y,
        'sta': sta,
        'sop': sop,
        'phase': phase,
        'sp_hist': sp_hist,
        'sp': sp,
        'RW': RW,
        'real_time': real_time,
        'spindle_time_raw': spindle_time_raw,
        'isis': np.diff(spindle_time_raw),
        'N2_rate': N2_rate,
        'N3_rate': N3_rate,
        'Fs': fs,
    }
    return bin_data
