"""
Model specification and design-matrix construction.

Ported from:
    helper_function/major_function/specify_mdl.m   → specify_model()
    helper_function/utils/build_design_mt.m        → build_design_matrix()

Please provide the following citation for all use:
    Shuqiang Chen, Mingjian He, Ritchie E. Brown, Uri T. Eden, Michael J Prerau,
    "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
    PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
"""

import numpy as np


# ---------------------------------------------------------------------------
# specify_model  (specify_mdl.m)
# ---------------------------------------------------------------------------

_ALL_FACTORS = ['SOphase', 'stage', 'SOpower', 'history']
_VALID_INTERACTIONS = {'stage:SOphase', 'SOphase:SOpower', 'stage:history'}


def specify_model(
    binary_select,
    interact_select=None,
    hist_choice='long',
    control_pt=None,
    binsize=0.1,
    hard_cutoffs=(12, 16),
):
    """
    Wrap model specifications into a model_spec dict.

    Parameters
    ----------
    binary_select : array_like of int, length 4
        Binary flags for [SOphase, stage, SOpower, history].
        1 = include, 0 = exclude.
    interact_select : list of str or None
        Interaction terms, e.g. ['stage:SOphase'].
        Valid options: 'stage:SOphase', 'SOphase:SOpower', 'stage:history'.
    hist_choice : str
        'long' (90 s) or 'short' (15 s).
    control_pt : array_like or None
        Cardinal-spline knot locations.  None → default for hist_choice.
    binsize : float
        Point-process bin size in seconds (default 0.1).
    hard_cutoffs : (float, float)
        Frequency cutoffs for fast-spindle selection (default (12, 16) Hz).

    Returns
    -------
    model_spec : dict
    """
    binary_select = np.asarray(binary_select, dtype=int).ravel()
    if len(binary_select) != 4:
        raise ValueError('binary_select must have exactly 4 elements '
                         '[SOphase, stage, SOpower, history].')

    if interact_select is None:
        interact_select = []

    # Normalise interaction strings: lower-case, colon separator
    def _norm_interaction(s):
        for sep in ('&', '-', ':'):
            s = s.replace(sep, ':')
        parts = sorted(p.strip().lower() for p in s.split(':'))
        return ':'.join(parts)

    valid_norm = {_norm_interaction(v) for v in _VALID_INTERACTIONS}
    normed = [_norm_interaction(i) for i in interact_select]
    invalid = [i for i in normed if i not in valid_norm]
    if invalid:
        raise ValueError(
            f"Invalid interaction(s): {invalid}. "
            f"Allowed: {sorted(_VALID_INTERACTIONS)}")

    # Default control points
    if control_pt is None:
        if hist_choice.lower() == 'short':
            hist_ord = int(15 / binsize)
            control_pt = np.concatenate([np.arange(0, 91, 15), [120, hist_ord]])
        else:
            hist_ord = int(90 / binsize)
            control_pt = np.concatenate([
                np.arange(0, 91, 15), [120],
                np.arange(150, 751, 100), [hist_ord]])
    else:
        control_pt = np.asarray(control_pt, dtype=float)
        hist_ord = int(control_pt[-1])

    selected_factors = [f for f, b in zip(_ALL_FACTORS, binary_select) if b == 1]
    factor_select_str = ', '.join(selected_factors)

    print(f"Selected modeling components: {factor_select_str}")
    if interact_select:
        print(f"Selected interactions → {', '.join(interact_select)}")
    else:
        print("Selected interactions → None")

    model_spec = {
        'BinarySelect': binary_select,
        'InteractSelect': interact_select,
        'hist_choice': hist_choice,
        'control_pt': control_pt,
        'binsize': binsize,
        'hard_cutoffs': hard_cutoffs,
        'FactorSelect': factor_select_str,
        'hist_ord': hist_ord,
        'hist_ord_s': hist_ord * binsize,
    }
    return model_spec


# ---------------------------------------------------------------------------
# build_design_matrix  (build_design_mt.m)
# ---------------------------------------------------------------------------

def build_design_matrix(model_spec, bin_data):
    """
    Construct the design matrix X from model_spec and bin_data.

    The factor order (fixed) is: SOphase, stage, SOpower, history.

    Parameters
    ----------
    model_spec : dict
        Output of specify_model().
    bin_data : dict
        Output of raw_to_bin_data().

    Returns
    -------
    X : ndarray, shape (n_bins, n_covariates)
    """
    interactions = model_spec['InteractSelect']
    bs = model_spec['BinarySelect']
    bs_str = ''.join(str(b) for b in bs)

    sta = bin_data['sta']                     # (N, 5)
    sop = bin_data['sop'] / 5.0              # rescale
    phase = bin_data['phase']
    sp_hist = bin_data['sp_hist']
    RW = bin_data['RW'].reshape(-1, 1)

    scale_factor = 10.0

    # Normalise interaction strings for comparison
    def _ni(s):
        for sep in ('&', '-', ':'):
            s = s.replace(sep, ':')
        return ':'.join(sorted(p.strip().lower() for p in s.split(':')))

    normed_interactions = {_ni(i) for i in interactions}

    # Helper: does the interactions set match exactly these terms?
    def _only(*terms):
        return normed_interactions == {_ni(t) for t in terms}

    cos_p = np.cos(phase).reshape(-1, 1)
    sin_p = np.sin(phase).reshape(-1, 1)
    sta_sub = sta[:, [0, 2, 3, 4]]           # N1, N3, REM, Wake (cols 0,2,3,4)
    sop1 = sop.reshape(-1, 1)
    sop2 = (sop ** 2 / scale_factor).reshape(-1, 1)

    X = None

    if not interactions:
        # ── No interactions ───────────────────────────────────────────────
        if bs_str == '0000':
            X = RW
        elif bs_str == '1000':
            X = np.hstack([RW, cos_p, sin_p])
        elif bs_str == '0100':
            X = sta_sub
        elif bs_str == '0010':
            X = np.hstack([RW, sop1, sop2])
        elif bs_str == '0001':
            X = np.hstack([RW, sp_hist])
        elif bs_str == '1100':
            X = np.hstack([sta_sub, cos_p, sin_p])
        elif bs_str == '1010':
            X = np.hstack([RW, sop1, sop2, cos_p, sin_p])
        elif bs_str == '1001':
            X = np.hstack([RW, cos_p, sin_p, sp_hist])
        elif bs_str == '0101':
            X = np.hstack([sta_sub, sp_hist])
        elif bs_str == '0011':
            X = np.hstack([RW, sop1, sop2, sp_hist])
        elif bs_str == '1101':
            X = np.hstack([sta_sub, cos_p, sin_p, sp_hist])
        elif bs_str == '1011':
            X = np.hstack([RW, sop1, sop2, cos_p, sin_p, sp_hist])

    elif _only('stage:SOphase'):
        if bs_str == '1100':
            X = np.hstack([cos_p, sin_p, sta_sub,
                            sta_sub * cos_p, sta_sub * sin_p])
        elif bs_str == '1101':
            X = np.hstack([cos_p, sin_p, sta_sub,
                            sta_sub * cos_p, sta_sub * sin_p,
                            sp_hist])

    elif _only('SOphase:SOpower') or _only('SOpower:SOphase'):
        if bs_str == '1010':
            X = np.hstack([RW, sop1, sop2, cos_p, sin_p,
                            cos_p * sop1, cos_p * sop2,
                            sin_p * sop1, sin_p * sop2])
        elif bs_str == '1011':
            X = np.hstack([RW, sop1, sop2, cos_p, sin_p,
                            cos_p * sop1, cos_p * sop2,
                            sin_p * sop1, sin_p * sop2,
                            sp_hist])

    elif _only('stage:SOphase', 'stage:history'):
        if bs_str == '1101':
            X = np.hstack([cos_p, sin_p, sta_sub,
                            sta_sub * cos_p, sta_sub * sin_p,
                            sp_hist,
                            sta[:, 1:2] * sp_hist,    # N2 * hist
                            sta[:, 2:3] * sp_hist])   # N3 * hist

    if X is None:
        raise ValueError(
            "Model components or interaction terms are not properly specified. "
            f"BinarySelect={bs_str}, interactions={interactions}")

    return X
