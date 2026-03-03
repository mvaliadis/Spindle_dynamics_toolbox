"""
Main preprocessing pipeline: raw EEG → design matrix.

Ported from helper_function/major_function/preprocessToDesignMatrix.m
with the addition of an optional ``cfg`` configuration dict that controls
three previously hard-coded workflow stages:

    cfg['spindle_source']  : 'tf_sigma' | 'precomputed'   (default 'tf_sigma')
    cfg['so_covariates']   : 'compute'  | 'precomputed' | 'none'  (default 'compute')
    cfg['use_stim']        : bool                          (default False)

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

import numpy as np
from scipy.signal import filtfilt, butter, sosfilt
from scipy.signal import hilbert as scipy_hilbert

from .tf_peak_detection import tf_peak_detection
from .so_power import compute_so_power
from .artifact_detection import detect_artifacts
from .binning import raw_to_bin_data
from .model import build_design_matrix


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def eeg_to_event_signal(eeg, fs, stage_val, stage_time, so_covariates='compute'):
    """
    Extract spindle events and SO covariates from raw EEG.

    Ported from helper_function/utils/eegToEventSignal.m

    Parameters
    ----------
    eeg : array_like, shape (N,)
        Raw EEG.
    fs : float
        Sampling frequency (Hz).
    stage_val : array_like
        Stage values (1=N3, 2=N2, 3=N1, 4=REM, 5=Wake).
    stage_time : array_like
        Corresponding times for stage_val (s).
    so_covariates : str
        'compute' – compute SO power and phase from EEG (default).
        'none'    – skip SO computation; SOpow and SOphase are set to zero.

    Returns
    -------
    res_table : dict
        Keys: peak_ctimes, peak_freqs, peak_stimes, peak_etimes,
              peak_maxprom_times, peak_stages, peak_proms, peak_durs,
              peak_freqHi, peak_freqLo, peak_vol,
              SOpow, SOphase, t, stages.
    """
    valid_so = ('compute', 'none')
    if so_covariates not in valid_so:
        raise ValueError(f"so_covariates must be one of {valid_so}, "
                         f"got '{so_covariates}'.")

    eeg = np.asarray(eeg, dtype=float).ravel()
    N = len(eeg)
    t = np.arange(N) / fs
    stage_val = np.asarray(stage_val, dtype=float).ravel()
    stage_time = np.asarray(stage_time, dtype=float).ravel()
    stage_val_t = np.interp(t, stage_time, stage_val,
                             left=stage_val[0], right=stage_val[-1])

    # Artifact detection
    print("Detecting artifacts...")
    artifacts = detect_artifacts(eeg, fs)

    # TF peak detection
    print("Running TF-sigma spindle detection...")
    sleep_stages = np.column_stack([t, stage_val_t])   # (N, 2)
    spindle_table, _ = tf_peak_detection(
        eeg, fs, sleep_stages, artifact_detect=artifacts, verbose=True)

    # SO covariates
    if so_covariates == 'compute':
        print("Computing SO power and phase...")
        so_power_norm, _ = compute_so_power(
            eeg, fs,
            stage_vals=stage_val_t, stage_times=t,
            is_excluded=artifacts,
        )
        # SO phase via bandpass → Hilbert
        sos = butter(4, [0.4 / (fs / 2), 1.5 / (fs / 2)],
                     btype='bandpass', output='sos')
        so_filt = sosfilt(sos, eeg)
        phase_raw = np.angle(scipy_hilbert(so_filt))
    else:
        # 'none': zero-fill
        so_power_norm = np.zeros(N)
        phase_raw = np.zeros(N)

    # Build res_table
    res_table = {
        'ID': 1,
        'night': 1,
        'channel': 'central',
        'stages': stage_val_t,
        't': t,
        'peak_ctimes': ((spindle_table['Start_Time'].values
                         + spindle_table['End_Time'].values) / 2
                        if len(spindle_table) > 0 else np.array([])),
        'peak_stimes': spindle_table['Start_Time'].values if len(spindle_table) > 0 else np.array([]),
        'peak_etimes': spindle_table['End_Time'].values if len(spindle_table) > 0 else np.array([]),
        'peak_maxprom_times': spindle_table['Max_Prominence_Time'].values if len(spindle_table) > 0 else np.array([]),
        'peak_freqs': spindle_table['Freq_Central'].values if len(spindle_table) > 0 else np.array([]),
        'peak_stages': spindle_table['Stage'].values if len(spindle_table) > 0 else np.array([]),
        'peak_proms': spindle_table['Prominence_Value'].values if len(spindle_table) > 0 else np.array([]),
        'peak_durs': spindle_table['Duration'].values if len(spindle_table) > 0 else np.array([]),
        'peak_freqHi': spindle_table['Freq_High'].values if len(spindle_table) > 0 else np.array([]),
        'peak_freqLo': spindle_table['Freq_Low'].values if len(spindle_table) > 0 else np.array([]),
        'peak_vol': spindle_table['Peak_Volume'].values if len(spindle_table) > 0 else np.array([]),
        'SOpow': so_power_norm,
        'SOphase': phase_raw,
    }
    return res_table


def preprocess_to_design_matrix(eeg, fs, stage_val, stage_time, model_spec,
                                  cfg=None):
    """
    Preprocess raw EEG data to a design matrix for GLM fitting.

    This is the main entry point, equivalent to preprocessToDesignMatrix.m,
    extended with an optional ``cfg`` dict that controls which parts of the
    workflow are executed.

    Parameters
    ----------
    eeg : array_like, shape (N,)
        Raw EEG data.
    fs : float
        Sampling frequency (Hz).
    stage_val : array_like
        Stage values (1=N3, 2=N2, 3=N1, 4=REM, 5=Wake).
    stage_time : array_like
        Corresponding times for stage_val (s).
    model_spec : dict
        Output of :func:`specify_model`.
    cfg : dict or None
        Optional configuration with the following keys and defaults:

        spindle_source : str, default ``'tf_sigma'``
            ``'tf_sigma'``    – run TF-sigma peak detection on the EEG.
            ``'precomputed'`` – use pre-detected spindles; requires
                                ``cfg['res_table']`` to be provided.

        so_covariates : str, default ``'compute'``
            ``'compute'``     – compute SO power and phase from EEG.
            ``'precomputed'`` – use SO covariates already present in
                                ``cfg['res_table']`` (no-op when spindle_source
                                is also 'precomputed').
            ``'none'``        – omit SO covariates (SOpow/SOphase = 0).

        use_stim : bool, default ``False``
            When ``True``, bin ``cfg['stim_times']`` and append the resulting
            column to the design matrix X.  Requires ``cfg['stim_times']``.

        res_table : dict
            Pre-built event/signal table.  Required when
            ``spindle_source == 'precomputed'``.  Must also contain
            ``SOpow`` / ``SOphase`` when ``so_covariates == 'precomputed'``.

        stim_times : array_like
            Stimulation event times in seconds.  Required when
            ``use_stim == True``.

    Returns
    -------
    X : ndarray, shape (n_bins, n_covariates)
        Design matrix.
    bin_data : dict
        Binned data (output of :func:`raw_to_bin_data`).
    res_table : dict
        Event information and raw signals.
    """
    # ── Resolve cfg defaults ──────────────────────────────────────────────
    if cfg is None:
        cfg = {}

    spindle_source = cfg.get('spindle_source', 'tf_sigma')
    so_covariates = cfg.get('so_covariates', 'compute')
    use_stim = cfg.get('use_stim', False)

    _valid_spindle = ('tf_sigma', 'precomputed')
    _valid_so = ('compute', 'precomputed', 'none')

    if spindle_source not in _valid_spindle:
        raise ValueError(f"cfg['spindle_source'] must be one of {_valid_spindle}, "
                         f"got '{spindle_source}'.")
    if so_covariates not in _valid_so:
        raise ValueError(f"cfg['so_covariates'] must be one of {_valid_so}, "
                         f"got '{so_covariates}'.")
    if use_stim and ('stim_times' not in cfg or not len(cfg.get('stim_times', []))):
        raise ValueError("cfg['stim_times'] must be provided when cfg['use_stim'] is True.")
    if spindle_source == 'precomputed' and 'res_table' not in cfg:
        raise ValueError("cfg['res_table'] must be provided when "
                         "cfg['spindle_source'] is 'precomputed'.")

    binsize = model_spec['binsize']
    hard_cutoffs = model_spec['hard_cutoffs']
    hist_choice = model_spec['hist_choice']

    # ── Spindle detection / loading ───────────────────────────────────────
    if spindle_source == 'tf_sigma':
        print("May take minutes ... Extracting spindles ...")
        res_table = eeg_to_event_signal(
            eeg, fs, stage_val, stage_time,
            so_covariates=so_covariates,
        )

    else:  # 'precomputed'
        res_table = dict(cfg['res_table'])   # shallow copy to avoid mutation

        if so_covariates == 'compute':
            print("Computing SO covariates for precomputed spindles...")
            res_table = _append_so_covariates(
                eeg, fs, stage_val, stage_time, res_table)

        elif so_covariates == 'none':
            N = len(np.asarray(eeg, dtype=float).ravel())
            res_table['SOpow'] = np.zeros(N)
            res_table['SOphase'] = np.zeros(N)
        # 'precomputed': res_table already has SOpow / SOphase → no action

    # ── Binning ───────────────────────────────────────────────────────────
    bin_data = raw_to_bin_data(res_table, fs, binsize, hard_cutoffs, hist_choice)

    # ── Design matrix ─────────────────────────────────────────────────────
    X = build_design_matrix(model_spec, bin_data)

    # ── Optional stim covariate ───────────────────────────────────────────
    if use_stim:
        stim_col = _build_stim_covariate(cfg['stim_times'], bin_data)
        X = np.hstack([X, stim_col.reshape(-1, 1)])
        print("Stimulation covariate appended to design matrix.")

    return X, bin_data, res_table


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _append_so_covariates(eeg, fs, stage_val, stage_time, res_table):
    """Compute SO power and phase and add them to res_table in-place."""
    eeg = np.asarray(eeg, dtype=float).ravel()
    N = len(eeg)
    t = np.arange(N) / fs
    stage_val = np.asarray(stage_val, dtype=float).ravel()
    stage_time = np.asarray(stage_time, dtype=float).ravel()
    stage_val_t = np.interp(t, stage_time, stage_val,
                             left=stage_val[0], right=stage_val[-1])

    artifacts = detect_artifacts(eeg, fs)

    so_power_norm, _ = compute_so_power(
        eeg, fs,
        stage_vals=stage_val_t, stage_times=t,
        is_excluded=artifacts,
    )
    sos = butter(4, [0.4 / (fs / 2), 1.5 / (fs / 2)],
                 btype='bandpass', output='sos')
    so_filt = sosfilt(sos, eeg)
    phase_raw = np.angle(scipy_hilbert(so_filt))

    res_table['SOpow'] = so_power_norm
    res_table['SOphase'] = phase_raw
    return res_table


def _build_stim_covariate(stim_times, bin_data):
    """Bin stimulation event times into the same bins as bin_data."""
    real_time = bin_data['real_time']
    if len(real_time) < 2:
        raise ValueError("bin_data['real_time'] must have at least 2 elements.")

    binsize = real_time[1] - real_time[0]
    t_start = real_time[0]
    t_end = real_time[-1] + binsize
    timestamps = np.arange(t_start, t_end + binsize / 2, binsize)

    stim_times = np.asarray(stim_times, dtype=float).ravel()
    stim_col, _ = np.histogram(stim_times, bins=timestamps)
    stim_col = stim_col.astype(float)

    n = len(bin_data['y'])
    if len(stim_col) > n:
        stim_col = stim_col[:n]
    elif len(stim_col) < n:
        stim_col = np.concatenate([stim_col, np.zeros(n - len(stim_col))])

    return stim_col
