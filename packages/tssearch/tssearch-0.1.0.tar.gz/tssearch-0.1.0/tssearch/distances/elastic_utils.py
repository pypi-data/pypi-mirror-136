import numpy as np
from numba import njit, prange, double
from tssearch.utils.preprocessing import standardization
from tssearch.distances.lockstep_distances import euclidean_distance  # added to calculate LCSS matrix


@njit(parallel=True, fastmath=True)
def _cost_matrix(x, y):
    l1 = x.shape[0]
    l2 = y.shape[0]
    cum_sum = np.zeros((l1, l2), dtype=np.float32)

    for i in prange(l1):
        for j in prange(l2):
            cum_sum[i, j] = (x[i] - y[j]) ** 2

    return cum_sum


@njit(parallel=True, fastmath=True)
def _multidimensional_cost_matrix(subseq, longseq, weight):
    """Helper function for fast computation of cost matrix in cost_matrix_diff_vec.
    Defined outside to prevent recompilation from numba
    Parameters
    ----------
    subseq: nd-array
        Short sequence
    longseq: nd-array
        Long sequence

    Returns
    -------
        Cost matrix
    """
    l1 = subseq.shape[0]
    l2 = longseq.shape[0]
    l3 = subseq.shape[1]
    cum_sum = np.zeros((l1, l2), dtype=np.float32)

    for i in prange(l1):
        for j in prange(l2):
            dist = 0.0
            for di in range(l3):
                diff = subseq[i, di] - longseq[j, di]
                dist += weight[i, di] * (diff * diff)
            cum_sum[i, j] = dist ** 0.5

    return cum_sum


@njit(nogil=True, fastmath=True)
def _accumulated_cost_matrix(D):
    """
    Fast computation of accumulated cost matrix using cost matrix.
    Parameters
    ----------
    D: nd-array
        Given cost matrix C, D = acc_initialization(...), D[1:, 1:] = C

    Returns
    -------
        Accumulated cost matrix
    """
    for i in range(D.shape[0] - 1):
        for j in range(D.shape[1] - 1):
            D[i + 1, j + 1] += min(D[i, j + 1], D[i + 1, j], D[i, j])
    return D


def acc_initialization(xl, yl, _type, tolerance=0):
    """Initializes the cost matrix according to the dtw type.

    Parameters
    ----------
    xl: N1*M array
    yl: N2*M array
    _type: string
        Name of dtw type
    tolerance: int
        Tolerance value

    Returns
    -------

    """
    ac = np.zeros((xl + 1, yl + 1))
    if _type == "dtw":
        ac[0, 1:] = np.inf
        ac[1:, 0] = np.inf
    elif _type == "oe-dtw":
        ac[0, 1:] = np.inf
        ac[1:, 0] = np.inf
    elif _type == "obe-dtw" or _type == "sub-dtw" or _type == "search":
        ac[1:, 0] = np.inf
    elif _type == "psi-dtw":
        ac[0, tolerance + 1 :] = np.inf
        ac[tolerance + 1 :, 0] = np.inf
    else:
        ac[0, 1:] = np.inf
        ac[1:, 0] = np.inf

    return ac


def cost_matrix(x, y, alpha=1, weight=None):
    """Computes cost matrix using a specified distance (dist) between two time series.
    x: nd-array
        The reference signal.
    y: nd-array
        The estimated signal.
    dist: function
        The distance used as a local cost measure. None defaults to the squared euclidean distance

    \**kwargs:
    See below:

    * *do_sign_norm* (``bool``) --
      If ``True`` the signals will be normalized before computing the DTW,
      (default: ``False``)

    * *do_dist_norm* (``bool``) --
      If ``True`` the DTW distance will be normalized by dividing the summation of the path dimension.
      (default: ``True``)

    * *window* (``String``) --
      Selects the global window constrains. Available options are ``None`` and ``sakoe-chiba``.
      (default: ``None``)

    * *factor* (``Float``) --
      Selects the global constrain factor.
      (default: ``min(xl, yl) * .50``)
    """

    if weight is None:
        weight = np.ones_like(x)

    if len(np.shape(weight)) == 1:
        weight = weight.reshape(-1, 1)

    if alpha == 1:
        C_d = 1
        if len(np.shape(x)) == 1:
            C_n = (_cost_matrix(x, y) * weight) / np.max(weight)
        else:
            C_n = _multidimensional_cost_matrix(x, y, weight)
    else:
        # standardization parameters
        abs_norm = np.mean(x, axis=0), np.std(x, axis=0)
        diff_norm = np.mean(np.diff(x, axis=0), axis=0), np.std(np.diff(x, axis=0), axis=0)

        # Derivative calculation and standardization
        _x = standardization(np.diff(x, axis=0), param=diff_norm)
        _y = standardization(np.diff(y, axis=0), param=diff_norm)
        # same length of derivative
        x = standardization(x[:-1], param=abs_norm)
        y = standardization(y[:-1], param=abs_norm)

        weight = weight[:-1]

        if len(np.shape(x)) == 1:
            C_d = _cost_matrix(_x, _y) * weight
            C_n = _cost_matrix(x, y) * weight
        else:
            C_d = _multidimensional_cost_matrix(_x, _y, weight)
            C_n = _multidimensional_cost_matrix(x, y, weight)

    C = alpha * C_n + (1 - alpha) * C_d

    return C


def accumulated_cost_matrix(C, **kwargs):
    """

    Parameters
    ----------
    C
    kwargs

    Returns
    -------

    """
    xl, yl = np.shape(C)

    window = kwargs.get("window", None)
    factor = kwargs.get("factor", np.min((xl, yl)) * 0.50)
    dtw_type = kwargs.get("dtw_type", "dtw")
    tolerance = kwargs.get("tolerance", 0)

    if window == "sakoe-chiba":
        C[np.abs(np.diff(np.indices(C.shape), axis=0))[0] > factor] = np.inf

    D = acc_initialization(xl, yl, dtw_type, tolerance)
    D[1:, 1:] = C.copy()
    D = _accumulated_cost_matrix(D)[1:, 1:]

    return D


@njit(nogil=True, fastmath=True)
def traceback(D):
    """
    Computes the traceback path of the matrix D.

    Parameters
    ----------
    D: nd-array
        Matrix

    Returns
    -------
        Coordinates p and q of the minimum path.

    """

    i, j = np.array(D.shape) - 2
    p, q = [i], [j]
    while (i > 0) and (j > 0):
        tb = 0
        if D[i, j + 1] < D[i, j]:
            tb = 1
        if D[i + 1, j] < D[i, j + tb]:
            tb = 2
        if tb == 0:
            i -= 1
            j -= 1
        elif tb == 1:
            i -= 1
        else:
            j -= 1
        p.insert(0, i)
        q.insert(0, j)
    while j > 0:
        j -= 1
        p.insert(0, i)
        q.insert(0, j)
    while i > 0:
        i -= 1
        p.insert(0, i)
        q.insert(0, j)

    return np.array(p), np.array(q)


@njit(nogil=True, fastmath=True)
def traceback_adj(D):
    """
    Computes the adjusted traceback path of the matrix D.

    Parameters
    ----------
    D: nd-array
        Matrix

    Returns
    -------
        Coordinates p and q of the minimum path adjusted.

    """
    i, j = np.array(D.shape) - 2
    p, q = [i], [j]
    while (i > 0) and (j > 0):
        tb = 0
        if D[i, j + 1] < D[i, j]:
            tb = 1
        if D[i + 1, j] < D[i, j + tb]:
            tb = 2
        if tb == 0:
            i -= 1
            j -= 1
        elif tb == 1:
            i -= 1
        else:  # (tb == 2):
            j -= 1
        p.insert(0, i)
        q.insert(0, j)
    while i > 0:
        i -= 1
        p.insert(0, i)
        q.insert(0, j)
    return np.array(p), np.array(q)


def backtracking(DP):
    # [ best_path ] = BACKTRACKING ( DP )
    # Compute the most cost-efficient path
    # DP := DP matrix of the TWED function

    x = np.shape(DP)
    i = x[0] - 1
    j = x[1] - 1

    # The indices of the paths are save in opposite direction
    # path = np.ones((i + j, 2 )) * np.inf;
    best_path = []

    steps = 0
    while i != 0 or j != 0:

        best_path.append((i - 1, j - 1))

        C = np.ones((3, 1)) * np.inf

        # Keep data points in both time series
        C[0] = DP[i - 1, j - 1]
        # Deletion in A
        C[1] = DP[i - 1, j]
        # Deletion in B
        C[2] = DP[i, j - 1]

        # Find the index for the lowest cost
        idx = np.argmin(C)

        if idx == 0:
            # Keep data points in both time series
            i = i - 1
            j = j - 1
        elif idx == 1:
            # Deletion in A
            i = i - 1
            j = j
        else:
            # Deletion in B
            i = i
            j = j - 1
        steps = steps + 1

    best_path.append((i - 1, j - 1))

    best_path.reverse()
    best_path = np.array(best_path[1:])

    return best_path[:, 0], best_path[:, 1]


# DTW SW
def dtw_sw(x, y, winlen, alpha=0.5, **kwargs):
    """Computes Dynamic Time Warping (DTW) of two time series using a sliding window.
    TODO: Check if this needs to be sped up.
    Parameters
    ----------
    x: nd-array
        The reference signal.
    y: (nd-array
        The estimated signal.
    winlen: int
        The sliding window length
    alpha: float
        A factor between 0 and 1 which weights the amplitude and derivative contributions.
        A higher value will favor amplitude and a lower value will favor the first derivative.

    \**kwargs:
        See below:

        * *do_sign_norm* (``bool``) --
          If ``True`` the signals will be normalized before computing the DTW,
          (default: ``False``)

        * *do_dist_norm* (``bool``) --
          If ``True`` the DTW distance will be normalized by dividing the summation of the path dimension.
          (default: ``True``)

        * *window* (``String``) --
          Selects the global window constrains. Available options are ``None`` and ``sakoe-chiba``.
          (default: ``None``)

        * *factor* (``Float``) --
          Selects the global constrain factor.
          (default: ``min(xl, yl) * .50``)


    Returns
    -------
           d: float
            The SW-DTW distance.
           C: nd-array
            The local cost matrix.
           ac: nd-array
            The accumulated cost matrix.
           path nd-array
            The optimal warping path between the two sequences.

    """
    xl, yl = len(x), len(y)

    do_sign_norm = kwargs.get("normalize", False)
    do_dist_norm = kwargs.get("dist_norm", True)
    window = kwargs.get("window", None)
    factor = kwargs.get("factor", np.min((xl, yl)) * 0.50)

    if do_sign_norm:
        x, y = standardization(x), standardization(y)

    ac = np.zeros((xl + 1, yl + 1))
    ac[0, 1:] = np.inf
    ac[1:, 0] = np.inf
    tmp_ac = ac[1:, 1:]

    nx = get_mirror(x, winlen)
    ny = get_mirror(y, winlen)

    dnx = np.diff(nx)
    dny = np.diff(ny)

    nx = nx[:-1]
    ny = ny[:-1]

    # Workaround to deal with even window sizes
    if winlen % 2 == 0:
        winlen -= 1

    swindow = np.hamming(winlen)
    swindow = swindow / np.sum(swindow)

    for i in range(xl):
        for j in range(yl):
            pad_i, pad_j = i + winlen, j + winlen
            # No window selected
            if window is None:
                tmp_ac[i, j] = sliding_dist(
                    nx[pad_i - (winlen // 2) : pad_i + (winlen // 2) + 1],
                    ny[pad_j - (winlen // 2) : pad_j + (winlen // 2) + 1],
                    dnx[pad_i - (winlen // 2) : pad_i + (winlen // 2) + 1],
                    dny[pad_j - (winlen // 2) : pad_j + (winlen // 2) + 1],
                    alpha,
                    swindow,
                )

            # Sakoe-Chiba band
            elif window == "sakoe-chiba":
                if abs(i - j) < factor:
                    tmp_ac[i, j] = sliding_dist(
                        nx[pad_i - (winlen // 2) : pad_i + (winlen // 2) + 1],
                        ny[pad_j - (winlen // 2) : pad_j + (winlen // 2) + 1],
                        dnx[pad_i - (winlen // 2) : pad_i + (winlen // 2) + 1],
                        dny[pad_j - (winlen // 2) : pad_j + (winlen // 2) + 1],
                        alpha,
                        swindow,
                    )
                else:
                    tmp_ac[i, j] = np.inf

            # As last resource, the complete window is calculated
            else:
                tmp_ac[i, j] = sliding_dist(
                    nx[pad_i - (winlen / 2) : pad_i + (winlen / 2) + 1],
                    ny[pad_j - (winlen / 2) : pad_j + (winlen / 2) + 1],
                    dnx[pad_i - (winlen / 2) : pad_i + (winlen / 2) + 1],
                    dny[pad_j - (winlen / 2) : pad_j + (winlen / 2) + 1],
                    alpha,
                    swindow,
                )

    c = tmp_ac.copy()

    for i in range(xl):
        for j in range(yl):
            tmp_ac[i, j] += min([ac[i, j], ac[i, j + 1], ac[i + 1, j]])

    path = traceback(ac)

    if do_dist_norm:
        d = ac[-1, -1] / np.sum(np.shape(path))
    else:
        d = ac[-1, -1]

    return d, c, ac, path


def sliding_dist(xw, yw, dxw, dyw, alpha, win):
    """
    Computes the sliding distance
    xw: nd-array
        x coords window
    yw: nd-array
        y coords window
    dxw: nd-array
        x coords diff window
    dyw: nd-array
        y coords diff window
    alpha: float
        Rely more on absolute or difference values 1- abs, 0 - diff
    win: nd-array
        Signal window used for sliding distance

    Returns
    -------
        Sliding distance
    """
    return (1 - alpha) * np.sqrt(np.sum((((dxw - dyw) * win) ** 2.0))) + alpha * np.sqrt(
        np.sum((((xw - yw) * win) ** 2.0))
    )


def get_mirror(s, ws):
    """Performs a signal windowing based on a double inversion from the start and end segments.

    Parameters
    ----------
    s: nd-array
            the input-signal.
    ws: int
            window size.

    Returns
    -------
        Signal windowed
    """

    return np.r_[2 * s[0] - s[ws:0:-1], s, 2 * s[-1] - s[-2 : -ws - 2 : -1]]


@njit()
def _lcss_point_dist(x, y):
    dist = 0.
    for di in range(x.shape[0]):
        diff = (x[di] - y[di])
        dist += diff * diff
    dist = dist ** 0.5
    return dist


def lcss_accumulated_matrix(x, y, eps):
    """Computes the LCSS similarity matrix using the euclidean distance (dist) between two time series.

    Parameters
    ----------
    x: nd-array
            The reference signal.
    y: nd-array
            The estimated signal.
    eps : float
            Amplitude matching threshold.

    Returns
    -------
    sim_mat : float
            Similarity matrix between both time series.
    """

    xl, yl = len(x), len(y)

    sim_mat = np.zeros((xl + 1, yl + 1))

    for i in range(1, xl + 1):
        for j in range(1, yl + 1):
            if _lcss_point_dist(x[i - 1, :], y[j - 1, :]) <= eps:
                sim_mat[i, j] = 1 + sim_mat[i - 1, j - 1]
            else:
                sim_mat[i, j] = max(sim_mat[i, j - 1], sim_mat[i - 1, j])

    return sim_mat


def lcss_path(x, y, sim_mat, eps):
    """Computes the LCSS matching path between two time series.

    Parameters
    ----------
    x: nd-array
            The reference signal.
    y: nd-array
            The estimated signal.
    sim_mat : float
            Similarity matrix between both time series.
    eps : float
            Matching threshold.

    Returns
    -------
    lcss_path : float
        LCSS matching path.
    """
    i, j = len(x), len(y)
    path = []

    while i > 0 and j > 0:
        if _lcss_point_dist(x[i - 1, :], y[j - 1, :]) <= eps:
            path.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif sim_mat[i - 1, j] > sim_mat[i, j - 1]:
            i -= 1
        else:
            j -= 1

    path = np.array(path[::-1])
    return path[1:, 0], path[1:, 1]


def lcss_score(sim_mat):
    """Computes the LCSS similarity score between two time series.

    Parameters
    ----------
    sim_mat : float
            Similarity matrix between both time series.

    Returns
    -------
    lcss : float
        LCSS score.
    """

    xl = sim_mat.shape[0] - 1
    yl = sim_mat.shape[1] - 1

    return float(sim_mat[-1, -1]) / min([xl, yl])
