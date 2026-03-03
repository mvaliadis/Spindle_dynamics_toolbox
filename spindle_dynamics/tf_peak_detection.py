"""
TF-sigma peak detector.

Ported from helper_function/TFsigma_peak_detector/:
    TF_peak_detection.m
    find_frequency_peaks.m
    find_time_peaks.m
    select_signal_TFpeaks.m
    extract_event_centroid.m

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from sklearn.cluster import KMeans

from .multitaper import multitaper_spectrogram
from .artifact_detection import detect_artifacts


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def tf_peak_detection(
    eeg,
    fs,
    sleep_stages,
    detection_stages=(1, 2, 3),
    artifact_detect=True,
    spindle_freq_range=(9.0, 17.0),
    peak_freq_range=(9.0, 17.0),
    findpeaks_freq_range=(6.0, 30.0),
    min_peak_width_sec=0.3,
    min_peak_distance_sec=0.0,
    smooth_sec=0.3,
    verbose=True,
):
    """
    Detect time-frequency (TF) sigma peaks (spindles) in an EEG signal.

    Parameters
    ----------
    eeg : array_like, shape (N,)
        Raw EEG data.
    fs : float
        Sampling frequency (Hz).
    sleep_stages : array_like, shape (N, 2) or (2, N)
        Sleep stage information as [times; stage_values] or [[t0,s0],[t1,s1]…].
        Stage conventions: 1=N3, 2=N2, 3=N1, 4=REM, 5=Wake.
    detection_stages : tuple of int
        Stages in which to run detection (default: (1, 2, 3) = NREM).
    artifact_detect : bool or array_like
        If True, run artifact detection.  If an array, treat as pre-computed
        artifact boolean mask.
    spindle_freq_range : (float, float)
        Final frequency range filter for the output spindle table (Hz).
    peak_freq_range : (float, float)
        Frequency range to search for spectral peaks (Hz).
    findpeaks_freq_range : (float, float)
        Wider frequency range used when running find_peaks (Hz).
    min_peak_width_sec : float
        Minimum spindle duration in seconds (default 0.3).
    min_peak_distance_sec : float
        Minimum separation between spindles in seconds (default 0).
    smooth_sec : float
        Smoothing (moving-average) applied to the prominence curve (s).
    verbose : bool

    Returns
    -------
    spindle_table : pd.DataFrame
        Detected spindles with columns:
        Start_Time, End_Time, Max_Prominence_Time, Freq_Central,
        Freq_Low, Freq_High, Prominence_Value, Duration, Stage, Peak_Volume.
    mt_spect : dict
        Keys: 'spect', 'stimes', 'sfreqs', 'stages_in_stimes'.
    """
    eeg = np.asarray(eeg, dtype=float).ravel()
    N = len(eeg)
    t = np.arange(N) / fs

    # Parse sleep stages
    sleep_stages = np.asarray(sleep_stages, dtype=float)
    if sleep_stages.shape[0] == 2:
        stage_times = sleep_stages[0]
        stage_vals = sleep_stages[1]
    else:
        stage_times = sleep_stages[:, 0]
        stage_vals = sleep_stages[:, 1]
    stage_val_t = np.interp(t, stage_times, stage_vals,
                             left=stage_vals[0], right=stage_vals[-1])

    # Artifact mask
    if isinstance(artifact_detect, (np.ndarray, list, tuple)):
        artifacts = np.asarray(artifact_detect, dtype=bool).ravel()
    elif artifact_detect is True:
        artifacts = detect_artifacts(eeg, fs, verbose=verbose)
    else:
        artifacts = np.zeros(N, dtype=bool)

    # Multitaper spectrogram
    if verbose:
        print("Computing multitaper spectrogram...")
    spect, stimes, sfreqs = multitaper_spectrogram(
        eeg, fs,
        freq_range=(0, 35),
        taper_params=(2, 3),
        window_params=(1, 0.05),
        verbose=verbose,
    )

    # Stage at each spectrogram window
    stages_in_stimes = np.interp(stimes, stage_times, stage_vals).round().astype(int)

    # Valid time indices (detection stages, non-artifact)
    artifact_in_stimes = _resample_mask_to_stimes(artifacts, t, stimes)
    detection_mask = (np.isin(stages_in_stimes, list(detection_stages))
                      & ~artifact_in_stimes)

    mt_spect = {
        'spect': spect,
        'stimes': stimes,
        'sfreqs': sfreqs,
        'stages_in_stimes': stages_in_stimes,
    }

    # Find frequency peaks
    if verbose:
        print("Finding frequency peaks...")
    fpeak_proms, fpeak_freqs, fpeak_bws, fpeak_bw_bounds = find_frequency_peaks(
        spect, stimes, sfreqs,
        detection_mask,
        peak_freq_range=peak_freq_range,
        findpeaks_freq_range=findpeaks_freq_range,
    )

    # Find time peaks
    if verbose:
        print("Finding time peaks...")
    (tpeak_proms, tpeak_times, tpeak_durations, tpeak_center_times,
     tpeak_freqs, tpeak_bws, tpeak_bw_bounds) = find_time_peaks(
        fpeak_proms, fpeak_freqs, fpeak_bws, fpeak_bw_bounds, stimes,
        detection_mask=detection_mask,
        min_peak_width_sec=min_peak_width_sec,
        min_peak_distance_sec=min_peak_distance_sec,
        smooth_sec=smooth_sec,
    )

    if len(tpeak_proms) == 0:
        # Return empty table
        spindle_table = pd.DataFrame(columns=[
            'Start_Time', 'End_Time', 'Max_Prominence_Time',
            'Freq_Central', 'Freq_Low', 'Freq_High',
            'Prominence_Value', 'Duration', 'Stage', 'Peak_Volume',
        ])
        return spindle_table, mt_spect

    # Build tpeak_properties dict for select_signal_TFpeaks
    tpeak_props = {
        'proms': tpeak_proms,
        'times': tpeak_times,             # (n_events, 2)  [start, end]
        'center_times': tpeak_center_times,
        'durations': tpeak_durations,
        'central_frequencies': tpeak_freqs,
        'bandwidths': tpeak_bws,
        'bandwidth_bounds': tpeak_bw_bounds,  # (n_events, 2) [f_low, f_high]
    }

    # Signal selection via k-means
    if verbose:
        print("Selecting TF peaks...")
    signal_idx = select_signal_tf_peaks(tpeak_props)

    # Extract event centroids for selected spindles
    tpeak_center_times, tpeak_freqs = extract_event_centroid(
        mt_spect, tpeak_props, signal_idx)

    # Stage assignment for selected events
    sel_times = tpeak_center_times
    sel_stages = np.interp(sel_times, stimes, stages_in_stimes).round().astype(int)

    # Peak volume = prom * duration * bandwidth
    sel_vol = (tpeak_props['proms'][signal_idx]
               * tpeak_props['durations'][signal_idx]
               * tpeak_props['bandwidths'][signal_idx])

    spindle_table = pd.DataFrame({
        'Start_Time':           tpeak_props['times'][signal_idx, 0],
        'End_Time':             tpeak_props['times'][signal_idx, 1],
        'Max_Prominence_Time':  tpeak_center_times,
        'Freq_Central':         tpeak_freqs,
        'Freq_Low':             tpeak_props['bandwidth_bounds'][signal_idx, 0],
        'Freq_High':            tpeak_props['bandwidth_bounds'][signal_idx, 1],
        'Prominence_Value':     tpeak_props['proms'][signal_idx],
        'Duration':             tpeak_props['durations'][signal_idx],
        'Stage':                sel_stages,
        'Peak_Volume':          sel_vol,
    })

    # Filter to spindle_freq_range
    mask = ((spindle_table['Freq_Central'] >= spindle_freq_range[0])
            & (spindle_table['Freq_Central'] <= spindle_freq_range[1]))
    spindle_table = spindle_table[mask].reset_index(drop=True)

    if verbose:
        print(f"Detected {len(spindle_table)} spindles.")

    return spindle_table, mt_spect


# ---------------------------------------------------------------------------
# find_frequency_peaks  (find_frequency_peaks.m)
# ---------------------------------------------------------------------------

def find_frequency_peaks(
    spect,
    stimes,
    sfreqs,
    detection_mask,
    peak_freq_range=(9.0, 17.0),
    findpeaks_freq_range=(6.0, 30.0),
):
    """
    For each time window find the most prominent spectral peak
    inside peak_freq_range.

    Returns
    -------
    fpeak_proms  : ndarray, shape (n_times,) - peak prominence at each time
    fpeak_freqs  : ndarray, shape (n_times,) - frequency of peak
    fpeak_bws    : ndarray, shape (n_times,) - bandwidth (Hz)
    fpeak_bw_bounds : ndarray, shape (n_times, 2) - [f_low, f_high]
    """
    n_times = len(stimes)
    fpeak_proms = np.full(n_times, np.nan)
    fpeak_freqs = np.full(n_times, np.nan)
    fpeak_bws = np.full(n_times, np.nan)
    fpeak_bw_bounds = np.full((n_times, 2), np.nan)

    # Frequency indices
    fp_mask = (sfreqs >= findpeaks_freq_range[0]) & (sfreqs <= findpeaks_freq_range[1])
    fp_freqs = sfreqs[fp_mask]
    peak_mask_rel = (fp_freqs >= peak_freq_range[0]) & (fp_freqs <= peak_freq_range[1])

    for k in range(n_times):
        if not detection_mask[k]:
            continue
        row = spect[k, fp_mask]
        if np.any(np.isnan(row)):
            continue

        peaks, props = find_peaks(row, prominence=0)
        if len(peaks) == 0:
            continue

        # Keep only peaks inside peak_freq_range
        in_range = peak_mask_rel[peaks]
        if not in_range.any():
            continue
        peaks = peaks[in_range]
        proms = props['prominences'][in_range]

        best = np.argmax(proms)
        p_idx = peaks[best]
        prom = proms[best]
        freq = fp_freqs[p_idx]

        # Bandwidth: find half-prominence crossing on each side
        half_h = row[p_idx] - prom / 2
        left = p_idx
        while left > 0 and row[left] > half_h:
            left -= 1
        right = p_idx
        while right < len(row) - 1 and row[right] > half_h:
            right += 1

        bw = fp_freqs[right] - fp_freqs[left]
        fpeak_proms[k] = prom
        fpeak_freqs[k] = freq
        fpeak_bws[k] = max(bw, 0.0)
        fpeak_bw_bounds[k, :] = [fp_freqs[left], fp_freqs[right]]

    return fpeak_proms, fpeak_freqs, fpeak_bws, fpeak_bw_bounds


# ---------------------------------------------------------------------------
# find_time_peaks  (find_time_peaks.m)
# ---------------------------------------------------------------------------

def find_time_peaks(
    fpeak_proms,
    fpeak_freqs,
    fpeak_bws,
    fpeak_bw_bounds,
    stimes,
    detection_mask=None,
    min_peak_width_sec=0.3,
    min_peak_distance_sec=0.0,
    smooth_sec=0.3,
):
    """
    Detect time-domain peaks in the frequency-prominence time series.

    Returns
    -------
    tpeak_proms      : ndarray (n_events,)
    tpeak_times      : ndarray (n_events, 2) – [start_time, end_time]
    tpeak_durations  : ndarray (n_events,)
    tpeak_center_t   : ndarray (n_events,)
    tpeak_freqs      : ndarray (n_events,)
    tpeak_bws        : ndarray (n_events,)
    tpeak_bw_bounds  : ndarray (n_events, 2)
    """
    prom_curve = fpeak_proms.copy()
    if detection_mask is not None:
        prom_curve[~detection_mask] = np.nan

    dt = stimes[1] - stimes[0]

    # Smooth
    if smooth_sec > 0:
        k = max(1, int(np.ceil(smooth_sec / dt)))
        kernel = np.ones(k) / k
        valid = ~np.isnan(prom_curve)
        smoothed = np.where(valid, prom_curve, 0.0)
        smoothed = np.convolve(smoothed, kernel, mode='same')
        # Re-apply NaN mask conservatively
        nan_expanded = np.convolve(~valid, kernel, mode='same') > 0
        prom_curve = np.where(nan_expanded, np.nan, smoothed)

    # Replace NaN with 0 for find_peaks, then restore mask
    finite_mask = ~np.isnan(prom_curve)
    curve = np.where(finite_mask, prom_curve, 0.0)

    min_distance = max(1, int(round(min_peak_distance_sec / dt))) if min_peak_distance_sec > 0 else 1
    min_width = max(1, int(round(min_peak_width_sec / dt)))

    peaks, props = find_peaks(
        curve,
        prominence=0,
        width=min_width,
        distance=min_distance,
    )

    if len(peaks) == 0:
        empty = np.array([])
        return (empty, np.empty((0, 2)), empty, empty, empty, empty,
                np.empty((0, 2)))

    tpeak_center_t = stimes[peaks]
    tpeak_proms = prom_curve[peaks]

    # Start / end times from half-width
    widths = props['widths'] * dt
    left_ips = props['left_ips'] * dt + stimes[0]
    right_ips = props['right_ips'] * dt + stimes[0]
    tpeak_times = np.column_stack([left_ips, right_ips])
    tpeak_durations = widths

    # Frequency, bandwidth at peak centres
    tpeak_freqs = fpeak_freqs[peaks]
    tpeak_bws = fpeak_bws[peaks]
    tpeak_bw_bounds = fpeak_bw_bounds[peaks, :]

    return (tpeak_proms, tpeak_times, tpeak_durations, tpeak_center_t,
            tpeak_freqs, tpeak_bws, tpeak_bw_bounds)


# ---------------------------------------------------------------------------
# select_signal_TFpeaks  (select_signal_TFpeaks.m)
# ---------------------------------------------------------------------------

def select_signal_tf_peaks(tpeak_props):
    """
    Separate signal spindles from noise using k-means on 5 features:
    log_prominence, log_volume, duration, central_frequency, bandwidth.

    Returns
    -------
    signal_idx : ndarray, shape (n_events,), dtype bool
    """
    proms = tpeak_props['proms']
    durs = tpeak_props['durations']
    freqs = tpeak_props['central_frequencies']
    bws = tpeak_props['bandwidths']

    vols = proms * durs * bws
    with np.errstate(divide='ignore', invalid='ignore'):
        log_proms = np.log(np.maximum(proms, 1e-30))
        log_vols = np.log(np.maximum(vols, 1e-30))

    X = np.column_stack([log_proms, log_vols, durs, freqs, bws])
    n = len(proms)

    if n < 3:
        return np.ones(n, dtype=bool)

    # K-means on each feature dimension, relabel clusters by descending mean
    idx_mat = np.zeros((n, 5), dtype=int)
    for pp in range(5):
        col = X[:, pp].reshape(-1, 1)
        n_clust = 3 if pp in (2, 4) else 2  # duration and bandwidth use 3 clusters
        try:
            km = KMeans(n_clusters=n_clust, n_init=10, random_state=42)
            raw_labels = km.fit_predict(col)
        except Exception:
            idx_mat[:, pp] = 0
            continue
        # Reorder clusters: 0 = largest mean, 1 = next, …
        means = np.array([col[raw_labels == c, 0].mean()
                          for c in range(n_clust)])
        order = np.argsort(means)[::-1]   # descending
        new_labels = np.empty_like(raw_labels)
        for new_c, old_c in enumerate(order):
            new_labels[raw_labels == old_c] = new_c
        idx_mat[:, pp] = new_labels

    # Signal = cluster-0 on both duration (col 2) and bandwidth (col 4)
    signal_idx = (idx_mat[:, 2] == 0) & (idx_mat[:, 4] == 0)
    return signal_idx


# ---------------------------------------------------------------------------
# extract_event_centroid  (extract_event_centroid.m)
# ---------------------------------------------------------------------------

def extract_event_centroid(mt_spect, tpeak_props, signal_idx=None):
    """
    Compute the power-weighted centroid (time, frequency) of each TF peak.

    Parameters
    ----------
    mt_spect : dict with keys 'spect', 'stimes', 'sfreqs'
    tpeak_props : dict with keys 'times' (n_events, 2) and 'bandwidth_bounds' (n_events, 2)
    signal_idx : bool array of length n_events (None → use all)

    Returns
    -------
    center_times : ndarray (n_sel,)
    center_freqs : ndarray (n_sel,)
    """
    spect = mt_spect['spect']
    stimes = mt_spect['stimes']
    sfreqs = mt_spect['sfreqs']

    time_bounds = tpeak_props['times']
    freq_bounds = tpeak_props['bandwidth_bounds']

    if signal_idx is None:
        signal_idx = np.ones(len(time_bounds), dtype=bool)

    sel_times = time_bounds[signal_idx]
    sel_freqs = freq_bounds[signal_idx]
    n_sel = sel_times.shape[0]

    center_t = np.zeros(n_sel)
    center_f = np.zeros(n_sel)

    for ii in range(n_sel):
        t0, t1 = sel_times[ii]
        f0, f1 = sel_freqs[ii]

        t_mask = (stimes >= t0) & (stimes <= t1)
        f_mask = (sfreqs >= f0) & (sfreqs <= f1)

        S = spect[np.ix_(t_mask, f_mask)]
        t_sub = stimes[t_mask]
        f_sub = sfreqs[f_mask]

        if S.size == 0 or np.nansum(S) == 0:
            # Fall back to midpoints
            center_t[ii] = (t0 + t1) / 2
            center_f[ii] = (f0 + f1) / 2
            continue

        total = np.nansum(S)
        # Weighted centroid along time axis
        t_weights = np.nansum(S, axis=1)
        center_t[ii] = np.sum(t_sub * t_weights) / np.sum(t_weights)
        # Weighted centroid along freq axis
        f_weights = np.nansum(S, axis=0)
        center_f[ii] = np.sum(f_sub * f_weights) / np.sum(f_weights)

    return center_t, center_f


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resample_mask_to_stimes(mask, t, stimes):
    """Convert sample-level boolean mask to spectrogram time resolution."""
    out = np.zeros(len(stimes), dtype=bool)
    for k, st in enumerate(stimes):
        idx = np.argmin(np.abs(t - st))
        out[k] = mask[idx]
    return out
