"""
Artifact detection in the time domain.

Ported from helper_function/utils/detect_artifacts.m

Uses iterative z-score thresholding on the smoothed Hilbert envelope of
high-pass filtered EEG to flag artifact time points.

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

import numpy as np
from scipy.signal import butter, sosfilt, hilbert


def detect_artifacts(
    data,
    fs,
    hf_crit=4.0,
    hf_pass=35.0,
    bb_crit=4.0,
    bb_pass=2.0,
    smooth_duration=2.0,
    detrend_duration=300.0,
    verbose=False,
):
    """
    Detect EEG artifacts by iteratively thresholding the filtered signal envelope.

    Parameters
    ----------
    data : array_like, shape (N,)
        EEG time series.
    fs : float
        Sampling frequency (Hz).
    hf_crit : float
        High-frequency criterion in standard deviations (default 4).
    hf_pass : float
        High-frequency high-pass cutoff in Hz (default 35).
    bb_crit : float
        Broadband criterion in standard deviations (default 4).
    bb_pass : float
        Broadband high-pass cutoff in Hz (default 2).
    smooth_duration : float
        Smoothing window length in seconds (default 2).
    detrend_duration : float
        Detrending window length in seconds (default 300).
    verbose : bool

    Returns
    -------
    artifacts : ndarray, shape (N,), dtype bool
        True at time points flagged as artifacts.
    """
    data = np.asarray(data, dtype=float).ravel()
    N = len(data)

    # Mark obviously bad samples
    bad_inds = np.isnan(data) | np.isinf(data)
    # Flat line detection
    if N > 100:
        diff_data = np.abs(np.diff(data, prepend=data[0]))
        bad_inds |= (diff_data == 0)

    # Outlier removal (10-sigma)
    mu = np.nanmean(data[~bad_inds])
    sigma = np.nanstd(data[~bad_inds])
    bad_inds |= (data < mu - 10 * sigma) | (data > mu + 10 * sigma)

    # Interpolate bad samples
    t = np.arange(N)
    good = ~bad_inds
    if good.sum() > 1:
        data_fixed = np.interp(t, t[good], data[good])
    else:
        data_fixed = data.copy()

    hf_artifacts = _band_artifacts(data_fixed, fs, hf_pass, hf_crit,
                                   smooth_duration, detrend_duration,
                                   bad_inds, verbose, 'high-frequency')
    bb_artifacts = _band_artifacts(data_fixed, fs, bb_pass, bb_crit,
                                   smooth_duration, detrend_duration,
                                   bad_inds, verbose, 'broadband')

    return hf_artifacts | bb_artifacts


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _highpass(data, fs, cutoff):
    """4th-order Butterworth high-pass filter."""
    sos = butter(4, cutoff / (fs / 2), btype='high', output='sos')
    return sosfilt(sos, data)


def _band_artifacts(data, fs, hp_cutoff, crit, smooth_dur, detrend_dur,
                    bad_inds, verbose, label):
    """Detect artifacts in a single frequency band."""
    filt = _highpass(data, fs, hp_cutoff)

    # Envelope via Hilbert
    envelope = np.abs(hilbert(filt))

    # Smooth
    smooth_samples = max(1, int(round(smooth_dur * fs)))
    smoothed = np.convolve(envelope,
                           np.ones(smooth_samples) / smooth_samples,
                           mode='same')

    # Log
    with np.errstate(divide='ignore'):
        log_env = np.log(np.maximum(smoothed, 1e-30))

    # Moving-median detrend
    detrend_samples = max(1, int(round(detrend_dur * fs)))
    from scipy.ndimage import median_filter
    trend = median_filter(log_env, size=detrend_samples, mode='reflect')
    y_signal = log_env - trend

    # Iterative z-score thresholding
    detected = bad_inds.copy()
    over_crit = np.ones(len(data), dtype=bool)    # force first iteration

    while over_crit.any():
        valid = ~detected
        if valid.sum() < 2:
            break
        mu = y_signal[valid].mean()
        std = y_signal[valid].std()
        if std == 0:
            break
        z = (y_signal - mu) / std
        over_crit = (np.abs(z) > crit) & ~detected
        detected[over_crit] = True

    if verbose:
        print(f"  {label}: {detected.sum()} artifact samples detected")

    return detected
