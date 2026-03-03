"""
Utility functions ported from the MATLAB helper_function/utils directory.

Includes:
    - modified_cardinal_spline  (ModifiedCardinalSpline.m)
    - hist_basis                (Hist.m)
    - raw_phase_to_bin_phase    (RawPhase2BinPhase.m)
    - stage_raw_to_bin          (stageraw2bin.m)
    - consecutive_runs          (consecutive_runs.m)
    - nanpow2db / nanzscore     (nanpow2db.m / nanzscore.m)

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

import numpy as np


# ---------------------------------------------------------------------------
# Modified Cardinal Spline  (ModifiedCardinalSpline.m)
# ---------------------------------------------------------------------------

def modified_cardinal_spline(ord_, c_pt_times_all, s=0.5):
    """
    Compute a modified cardinal spline basis matrix.

    Parameters
    ----------
    ord_ : int
        History order (number of lag bins).
    c_pt_times_all : array_like
        Knot (control-point) locations.
    s : float, optional
        Tension parameter (default 0.5).

    Returns
    -------
    Sp : ndarray, shape (ord_, len(c_pt_times_all))
        Spline basis matrix.
    """
    c_pt = np.asarray(c_pt_times_all, dtype=float)
    num_knots = len(c_pt)
    Sp = np.zeros((ord_, num_knots))

    lb = (c_pt[2] - c_pt[0]) / (c_pt[1] - c_pt[0])
    le = (c_pt[-1] - c_pt[-3]) / (c_pt[-1] - c_pt[-2])

    for i in range(1, ord_ + 1):          # 1-indexed to match MATLAB
        idx = np.searchsorted(c_pt, i, side='right') - 1  # nearest_c_pt_index (0-based)
        if idx < 0:
            idx = 0
        if idx >= num_knots - 1:
            idx = num_knots - 2

        nearest = c_pt[idx]
        nxt = c_pt[idx + 1]
        u = (i - nearest) / (nxt - nearest)
        uv = np.array([u**3, u**2, u, 1.0])

        if nearest == c_pt[0]:
            # Beginning knot
            M = np.array([
                [2 - s / lb, -2,        s / lb],
                [s / lb - 3,  3,       -s / lb],
                [0,           0,        0],
                [1,           0,        0],
            ])
            p = uv @ M
            Sp[i - 1, idx:idx + 3] = p

        elif nearest == c_pt[-2]:
            # End knot
            M = np.array([
                [-s / le,     2,    -2 + s / le],
                [2 * s / le, -3,     3 - 2 * s / le],
                [-s / le,     0,     s / le],
                [0,           1,     0],
            ])
            p = uv @ M
            Sp[i - 1, idx - 1:idx + 2] = p

        else:
            # Interior knot
            prev = c_pt[idx - 1]
            nxt2 = c_pt[idx + 2]
            l1 = (nxt - prev) / (nxt - nearest)
            l2 = (nxt2 - nearest) / (nxt - nearest)
            M = np.array([
                [-s / l1,       2 - s / l2,   s / l1 - 2,  s / l2],
                [2 * s / l1,    s / l2 - 3,   3 - 2 * s / l1, -s / l2],
                [-s / l1,       0,            s / l1,      0],
                [0,             1,            0,           0],
            ])
            p = uv @ M
            Sp[i - 1, idx - 1:idx + 3] = p

    return Sp


# ---------------------------------------------------------------------------
# History indicator basis  (Hist.m)
# ---------------------------------------------------------------------------

def hist_basis(lag, spike_train):
    """
    Generate an indicator-basis history matrix.

    Parameters
    ----------
    lag : int
        History lag in bins.
    spike_train : array_like, shape (N,)
        Binary spike train.

    Returns
    -------
    SpikeHist : ndarray, shape (N - lag, lag)
        Each column i contains the spike train shifted by i bins.
    """
    y = np.asarray(spike_train, dtype=float).ravel()
    N = len(y)
    SpikeHist = np.zeros((N - lag, lag))
    for i in range(1, lag + 1):                      # i = 1..lag
        SpikeHist[:, i - 1] = y[lag - i: N - i]     # matches MATLAB indexing
    return SpikeHist


# ---------------------------------------------------------------------------
# Raw phase → bin phase  (RawPhase2BinPhase.m)
# ---------------------------------------------------------------------------

def raw_phase_to_bin_phase(phase_raw, fs, spindle_times, spindle_train, timestamps):
    """
    Map raw SO phase to binned spindle train bins.

    When a spindle occurs the exact sample phase is used;
    for empty bins the circular mean phase of all samples in that bin is used.

    Parameters
    ----------
    phase_raw : array_like, shape (N,)
        Instantaneous SO phase (radians) at every EEG sample.
    fs : float
        Sampling frequency of phase_raw (Hz).
    spindle_times : array_like
        Times of detected spindle events (s).
    spindle_train : array_like
        Binned spindle train (length = len(timestamps) - 1).
    timestamps : array_like
        Bin-edge timestamps produced by rawToBinData (s).

    Returns
    -------
    SO_phase : ndarray, shape (len(spindle_train),)
        Binned SO phase.
    """
    phase_raw = np.asarray(phase_raw, dtype=float).ravel()
    spindle_times = np.asarray(spindle_times, dtype=float).ravel()
    spindle_train = np.asarray(spindle_train, dtype=float).ravel()
    timestamps = np.asarray(timestamps, dtype=float).ravel()

    N = len(phase_raw)
    phase_raw = np.unwrap(phase_raw)
    phase_time_raw = np.arange(1, N + 1) / fs          # 1/Fs .. N/Fs

    n_bins = len(spindle_train)

    # 1) Exact phase for spindle-event bins
    spindle_idx = np.searchsorted(phase_time_raw, spindle_times) - 1
    spindle_idx = np.clip(spindle_idx, 0, N - 1)
    spindle_phase = phase_raw[spindle_idx]

    # 2) Mean phase in each bin for non-spindle bins
    bin_counts = np.histogram(phase_time_raw, bins=timestamps)[0]   # samples per bin
    cum_counts = np.cumsum(bin_counts)
    start_counts = cum_counts - (bin_counts - 1)

    phase_train = np.zeros(n_bins)
    for i in range(n_bins):
        s = int(start_counts[i]) - 1
        e = int(cum_counts[i])
        if s < e and s < N:
            e = min(e, N)
            phase_train[i] = np.mean(phase_raw[s:e])

    # 3) Replace with exact phase at spindle bins
    SO_phase = phase_train.copy()
    total_spikes = int(np.sum(spindle_train == 1))
    SO_phase[spindle_train == 1] = spindle_phase[:total_spikes]

    return SO_phase


# ---------------------------------------------------------------------------
# Stage raw → bin  (stageraw2bin.m)
# ---------------------------------------------------------------------------

def stage_raw_to_bin(stages_raw, stagetime_raw, binsize, epoch, timestamps):
    """
    Convert raw stage vector to binned stage train and stage matrix.

    Parameters
    ----------
    stages_raw : array_like
        Stage values at each epoch (1=N3, 2=N2, 3=N1, 4=REM, 5=Wake).
    stagetime_raw : array_like
        Corresponding times of stage epochs (s).
    binsize : float
        Bin size in seconds.
    epoch : float
        Duration of one stage epoch in seconds.
    timestamps : array_like
        Bin-edge timestamps.

    Returns
    -------
    stage : ndarray, shape (n_bins, 5)
        Binary stage matrix [N1, N2, N3, REM, Wake].
    stagetrain : ndarray, shape (n_bins,)
        Integer stage label per bin.
    """
    stages_raw = np.asarray(stages_raw, dtype=float).ravel()
    stagetime_raw = np.asarray(stagetime_raw, dtype=float).ravel()
    timestamps = np.asarray(timestamps, dtype=float).ravel()

    n_bins = len(timestamps) - 1

    if binsize <= epoch:
        steps_per_epoch = int(round(epoch / binsize))
        stagetrain = np.zeros(n_bins)
        for i, s in enumerate(stages_raw):
            start = i * steps_per_epoch
            end = min((i + 1) * steps_per_epoch, n_bins)
            stagetrain[start:end] = s
    else:
        # Each output bin corresponds to possibly multiple epochs.
        # Assign the stage at the centre of each bin.
        bin_centres = (timestamps[:-1] + timestamps[1:]) / 2
        idx = np.searchsorted(stagetime_raw, bin_centres, side='right') - 1
        idx = np.clip(idx, 0, len(stages_raw) - 1)
        stagetrain = stages_raw[idx]

    # Stage matrix: [N1, N2, N3, REM, Wake]
    stage = np.zeros((n_bins, 5))
    stage[stagetrain == 3, 0] = 1   # N1
    stage[stagetrain == 2, 1] = 1   # N2
    stage[stagetrain == 1, 2] = 1   # N3
    stage[stagetrain == 4, 3] = 1   # REM
    wake_mask = (stagetrain == 5) | (stagetrain == 0) | np.isnan(stagetrain)
    stage[wake_mask, 4] = 1         # Wake

    return stage, stagetrain


# ---------------------------------------------------------------------------
# Consecutive runs  (consecutive_runs.m)
# ---------------------------------------------------------------------------

def consecutive_runs(bool_arr):
    """
    Find start/end indices of consecutive True runs in a boolean array.

    Returns
    -------
    list of (start, end) tuples (inclusive, 0-based).
    """
    bool_arr = np.asarray(bool_arr, dtype=bool).ravel()
    padded = np.concatenate(([False], bool_arr, [False]))
    diff = np.diff(padded.astype(int))
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0] - 1
    return list(zip(starts, ends))


# ---------------------------------------------------------------------------
# nanpow2db / nanzscore
# ---------------------------------------------------------------------------

def nanpow2db(x):
    """Convert power to dB, ignoring NaNs."""
    x = np.asarray(x, dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        out = 10.0 * np.log10(x)
    return out


def nanzscore(x):
    """Z-score ignoring NaNs."""
    x = np.asarray(x, dtype=float)
    mu = np.nanmean(x)
    sigma = np.nanstd(x)
    if sigma == 0:
        return np.zeros_like(x)
    return (x - mu) / sigma
