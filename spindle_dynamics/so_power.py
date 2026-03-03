"""
Slow-oscillation (SO) power computation.

Ported from helper_function/utils/compute_SOP.m and compute_mtspect_power.m

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

import re

import numpy as np
from .multitaper import multitaper_spectrogram
from .utils import nanzscore


def compute_so_power(
    eeg,
    fs,
    stage_vals=None,
    stage_times=None,
    so_freq_range=(0.4, 1.5),
    so_power_outlier_threshold=3.0,
    norm_method='p2shift1234',
    eeg_times=None,
    time_range=None,
    is_excluded=None,
    window_params=(4, 1),
    tapers=(2, 3),
):
    """
    Compute normalised slow-oscillation power.

    Parameters
    ----------
    eeg : array_like, shape (N,)
        Raw EEG data.
    fs : float
        Sampling frequency (Hz).
    stage_vals : array_like or None
        Stage values (1=N3,2=N2,3=N1,4=REM,5=Wake).
    stage_times : array_like or None
        Corresponding times for stage_vals.
    so_freq_range : (float, float)
        Band used to compute SO power (Hz).
    so_power_outlier_threshold : float
        z-score threshold for excluding SO power outliers (default 3).
    norm_method : str
        Normalisation method.  Currently supports the 'p{N}shift{S}' family
        (e.g. 'p2shift1234') and 'none'.
    eeg_times : array_like or None
        Time axis for EEG samples.  None → (0..N-1)/fs.
    time_range : (float, float) or None
        Sub-range of the recording to use for normalisation.
    is_excluded : array_like of bool or None
        Artifact mask (same length as eeg).  Artifact samples become NaN.
    window_params : (float, float)
        (window_length_s, step_s) for multitaper power estimation.
    tapers : (int, int)
        (time_half_bandwidth, num_tapers).

    Returns
    -------
    so_power_norm : ndarray, shape (N,)
        Normalised SO power, interpolated back to EEG sample rate.
    so_power_times : ndarray, shape (N,)
        Time axis (same as eeg_times).
    """
    eeg = np.asarray(eeg, dtype=float).ravel()
    N = len(eeg)

    if eeg_times is None:
        eeg_times = np.arange(N) / fs
    else:
        eeg_times = np.asarray(eeg_times, dtype=float).ravel()

    if time_range is None:
        time_range = (eeg_times[0], eeg_times[-1])

    if is_excluded is None:
        is_excluded = np.zeros(N, dtype=bool)
    else:
        is_excluded = np.asarray(is_excluded, dtype=bool).ravel()

    # Replace artifact samples with NaN
    nan_eeg = eeg.copy()
    nan_eeg[is_excluded] = np.nan

    # Multitaper power in the SO band
    spect, stimes, sfreqs = multitaper_spectrogram(
        nan_eeg, fs,
        freq_range=so_freq_range,
        taper_params=tapers,
        window_params=window_params,
        verbose=False,
    )

    # Adjust time axis to eeg_times origin
    stimes = stimes + eeg_times[0]

    # SO power = integrated band power (sum over SO frequencies)
    so_power = np.nansum(spect, axis=1)   # shape (n_windows,)

    # Stage at spectrogram windows
    if stage_vals is not None and stage_times is not None:
        stage_vals = np.asarray(stage_vals, dtype=float).ravel()
        stage_times = np.asarray(stage_times, dtype=float).ravel()
        sop_stages = np.interp(stimes, stage_times, stage_vals).round().astype(int)
    else:
        sop_stages = None

    # Exclude outlier windows
    z = nanzscore(so_power)
    so_power[np.abs(z) >= so_power_outlier_threshold] = np.nan

    # Normalise
    so_power_norm = _normalize_so_power(
        so_power, stimes, sop_stages, time_range, norm_method)

    # Upsample to EEG sample rate
    valid = ~np.isnan(so_power_norm)
    if valid.sum() > 1:
        t_valid = np.concatenate([[eeg_times[0]],
                                   stimes[valid],
                                   [eeg_times[-1]]])
        v_valid = np.concatenate([[so_power_norm[valid][0]],
                                   so_power_norm[valid],
                                   [so_power_norm[valid][-1]]])
        so_power_up = np.interp(eeg_times, t_valid, v_valid)
    else:
        so_power_up = np.zeros(N)

    so_power_up[is_excluded] = np.nan
    return so_power_up, eeg_times


# ---------------------------------------------------------------------------
# Normalisation helper
# ---------------------------------------------------------------------------

def _normalize_so_power(so_power, stimes, sop_stages, time_range, norm_method):
    """Apply normalisation to raw SO power values."""
    in_range = (stimes >= time_range[0]) & (stimes <= time_range[1])

    if norm_method.lower() == 'none':
        return so_power.copy()

    # Parse 'p{N}shift{S}' format, e.g. 'p2shift1234'
    m = re.match(r'p(\d+)shift(\d*)', norm_method, re.IGNORECASE)
    if m:
        shift_ptile = float(m.group(1))
        stage_str = m.group(2)
        shift_stages = [int(c) for c in stage_str] if stage_str else [1, 2, 3, 4]

        if sop_stages is not None:
            valid_stage = np.isin(sop_stages, shift_stages)
        else:
            valid_stage = np.ones(len(so_power), dtype=bool)

        sel = in_range & valid_stage & ~np.isnan(so_power)
        if sel.sum() > 0:
            ptile = np.nanpercentile(so_power[sel], shift_ptile)
        else:
            ptile = 0.0
        return so_power - ptile

    raise ValueError(f"Unsupported norm_method: '{norm_method}'. "
                     "Use 'none' or 'p{{N}}shift{{stages}}' (e.g. 'p2shift1234').")
