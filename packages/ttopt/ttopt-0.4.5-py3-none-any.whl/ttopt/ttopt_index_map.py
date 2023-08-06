import numpy as np
import scipy as sp
from scipy.special import comb


class TTOptIndexMap:
    def __init__(self, d, k, ind_none=None, with_less=False):
        # Base (long) index:
        self.d0 = int(d)
        self.n0 = int(2**self.d0)

        # What return if unused element is requested:
        self.ind_none = ind_none

        # New (short) index (will be changed later in "prep" function):
        self.d = self.d0      # Dimension of short tensor
        self.n = self.n0      # Total number of elements of short tensor
        self.n_used = self.n0 # Number of used (real) elements of short tensor

        # Number of selected elements:
        self.k = int(k)
        if self.k > self.d0:
            raise ValueError('Invalid fraction (k > d)')

        # Do we use "less or equal than k" mode
        # ("equal to k" will be used instead):
        self.with_less = with_less

    def prep(self):
        self.n_used = _calc_comb_num(self.d0, self.k, self.with_less)
        self.d = int(np.ceil(np.log2(float(self.n_used))))
        self.n = 2**self.d

        _get = lambda k_: [comb(d_, k_, exact=True) for d_ in range(self.d0+1)]
        self.combs = np.array([_get(k_) for k_ in range(0, self.k+1)])
        self.pows2 = np.array([2**d_ for d_ in range(self.d)])

    def get(self, ind):
        """Get long multi-index for given short multi-index "ind"."""
        num = int(np.asanyarray(ind) @ self.pows2) + 1
        return self.get_flat(num)

    def get_flat(self, num):
        """Get long multi-index for given element number "num" (1, 2, ...)."""
        if num > self.n_used:
            return self.ind_none

        if self.with_less:
            return self._get_flat_exact_with_less(num, self.k)
        else:
            return self._get_flat_exact(num, self.k)

    def _get_flat_exact(self, num, k):
        res = np.zeros(self.d0, dtype=int)

        while num > 0:
            i = np.searchsorted(self.combs[k], num) - 1
            if i < 0:
                break
            if i >= self.d0:
                raise ValueError('Invalid element number')

            res[i] = 1
            num -= self.combs[k][i]
            k -= 1

        return res

    def _get_flat_exact_with_less(self, num, k):
        # TODO: maybe precompute the combs...
        comb_curr = comb(self.d0, k, exact=True)
        while num > comb_curr and k > 0:
            num -= comb_curr
            k -= 1
            comb_curr = comb(self.d0, k, exact=True)

        return self._get_flat_exact(num, k)

    def info(self):
        text = ''
        text += f'd long       : {self.d0:-12d}\n'
        text += f'n long       : {self.n0:-12d}\n'
        text += f'd short      : {self.d:-12d}\n'
        text += f'n short      : {self.n:-12d}\n'
        text += f'n short used : {self.n_used:-12d}\n'
        print(text)


def _calc_comb_num(d, k, with_less=False):
    if not with_less:
        return int(comb(d, k))

    n = int(sum([comb(d, k_, exact=True) for k_ in range(1, k+1)]))
    n += 1 # TODO: check (it relates to [0, 0, ..., 0])
    return n
