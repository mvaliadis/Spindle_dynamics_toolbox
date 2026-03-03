"""
Multitaper spectrogram implementation using scipy DPSS tapers.

Ported from helper_function/multitaper/multitaper_spectrogram.m

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

import numpy as np
from scipy.signal import windows


def multitaper_spectrogram(
    eeg,
    fs,
    freq_range=(0, None),
    taper_params=(2, 3),
    window_params=(1, 0.05),
    nfft=None,
    detrend='constant',
    weighting='unity',
    verbose=True,
):
    """
    Compute a multitaper spectrogram of an EEG signal.

    Parameters
    ----------
    eeg : array_like, shape (N,)
        Raw EEG signal.
    fs : float
        Sampling frequency (Hz).
    freq_range : tuple (f_min, f_max)
        Frequency range to return.  f_max=None → fs/2.
    taper_params : tuple (time_half_bandwidth, num_tapers)
        e.g., (2, 3) → time-half-bandwidth product = 2, number of tapers = 3.
    window_params : tuple (window_length_s, step_s)
        Window length and step in seconds.
    nfft : int or None
        FFT length.  None → next power of 2 ≥ window_samples.
    detrend : str
        Detrend mode passed to numpy ('constant', 'linear', or None).
    weighting : str
        'unity' for uniform taper weighting (eigenvalue weighting not yet
        implemented).
    verbose : bool

    Returns
    -------
    spect : ndarray, shape (n_times, n_freqs)
        Power spectrogram (linear scale).
    stimes : ndarray, shape (n_times,)
        Centre times of each window (s).
    sfreqs : ndarray, shape (n_freqs,)
        Frequency axis (Hz).
    """
    eeg = np.asarray(eeg, dtype=float).ravel()
    N = len(eeg)
    t = np.arange(N) / fs

    time_half_bw, num_tapers = taper_params
    win_len_s, step_s = window_params

    win_samples = int(round(win_len_s * fs))
    step_samples = int(round(step_s * fs))

    if nfft is None:
        nfft = int(2 ** np.ceil(np.log2(win_samples)))

    f_max = fs / 2 if freq_range[1] is None else freq_range[1]
    f_min = freq_range[0]

    # DPSS tapers
    tapers, _ = windows.dpss(win_samples, time_half_bw, Kmax=num_tapers, return_ratios=True)
    # tapers shape: (num_tapers, win_samples)

    # Frequency axis
    freqs = np.fft.rfftfreq(nfft, d=1.0 / fs)
    freq_mask = (freqs >= f_min) & (freqs <= f_max)
    sfreqs = freqs[freq_mask]

    # Sliding window indices
    starts = np.arange(0, N - win_samples + 1, step_samples)
    stimes = (starts + win_samples / 2) / fs

    spect = np.full((len(starts), np.sum(freq_mask)), np.nan)

    for k, start in enumerate(starts):
        seg = eeg[start: start + win_samples].copy()

        # Detrend
        if detrend == 'constant':
            seg -= np.mean(seg)
        elif detrend == 'linear':
            seg -= np.polyval(np.polyfit(np.arange(win_samples), seg, 1),
                              np.arange(win_samples))

        # NaN check
        if np.any(np.isnan(seg)):
            continue

        # Multitaper FFT
        mt_power = np.zeros(nfft // 2 + 1)
        for taper in tapers:
            tapered = seg * taper
            fft_seg = np.fft.rfft(tapered, n=nfft)
            mt_power += np.abs(fft_seg) ** 2

        mt_power /= num_tapers          # uniform (unity) weighting
        # Correct one-sided spectrum (double non-DC, non-Nyquist bins)
        if nfft % 2 == 0:
            mt_power[1:-1] *= 2
        else:
            mt_power[1:] *= 2
        mt_power /= (fs * win_samples)  # normalise to power spectral density

        spect[k, :] = mt_power[freq_mask]

    if verbose:
        print(f"Multitaper spectrogram: {len(stimes)} windows × {len(sfreqs)} freqs")

    return spect, stimes, sfreqs
