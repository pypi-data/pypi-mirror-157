import numpy as np
from time import perf_counter as tpc


from .ttopt import TTOpt
from .ttopt_index_map import TTOptIndexMap


class TTOptBinary():
    """Multidimensional binary tensor minimizer based on TTOpt.

    Wrapper for computation of the minimum for the implicitly given
    d-dimensional array of the shape 2 x 2 x ... x 2. The constraint (such as
    "exactly equals" or "no more than") on the maximum number of non-zero
    indices in the found multi-index of the optimum is also supported.

    Args:
        f (function): the function that returns the tensor element (float) for
            the given multi-index (1D numpy array of the shape [d] of int).
        d (int): number of tensor dimensions.
        evals (int): the possible number of requests to the function "f".
        k (int): optional constraint (such as "exactly equals" or "no more
            than") on the maximum number of non-zero indices in the found
            multi-index of the tensor optimum. It is None by default.
        name (str): optional display name for the tensor of interest. It is
            the "Tensor" string by default.
        with_cache (bool): if flag is True, then all requested values are
            stored and retrieved from the storage upon repeated requests.
            It is True by default.
        with_less (bool): if flag is True, then "no more than" constraint will
            be applied (if "k" argument is set). Otherwise, the "exactly equals"
            constraint will be applied (if "k" argument is set). It is False by
            default.
        with_log (bool): if flag is True, then text messages will be displayed
            during the optimizer query process. It is False by default.
        with_simple_constraint (bool): if flag is True and "k" is not None,
            then target function will be modified as f = 0 if constraint is not
            satisfied. Otherwise, the index mapping (TTOptIndexMap) will be
            used. It is False by default.
        value_none (float): the value that will be used when requesting unused
            elements of the transformed tensor (from TTOptIndexMap). It must be
            greater than the real minimum value. It is used in the case of
            optimization in the presence of a constraint and when the flag
            "with_simple_constraint" is off.

    Note:
        Call, if necessary, "set_opts_init" and "set_opts_spec" methods to
        refine the additional TTOpt parameters. To start the process of finding
        the optimum, the "minimize" method should be called after creating an
        instance of the class. When the calculation process is completed, call
        the "info" method to display information about the calculation. The
        optimization result will be available in "i_min" (multi-index of the
        original tensor) and "y_min" (tensor value) variables.

    """

    def __init__(self, f, d, evals, k=None, name='Tensor', with_cache=False, with_less=False, with_log=False, with_simple_constraint=False, value_none=0.):
        self.f = f
        self.d = int(d)
        self.evals = int(evals)
        self.k = int(k) if k else None
        self.name = str(name)
        self.with_cache =  bool(with_cache)
        self.with_less =  bool(with_less)
        self.with_log =  bool(with_log)
        self.with_constraint = self.k is not None
        self.with_simple_constraint = bool(with_simple_constraint)
        self.value_none = value_none

        self.set_opts_init()
        self.set_opts_spec()
        self._init()

    @property
    def i_min(self):
        """Current multi-index of approximation of min of the tensor."""
        if self.ttopt is not None and self.ttopt.i_min is not None:
            if self.with_constraint and not self.with_simple_constraint:
                return self.im.get(self.ttopt.i_min)
            else:
                return self.ttopt.i_min

    @property
    def y_min(self):
        """Current approximation of min of the tensor."""
        if self.ttopt is not None:
            return self.ttopt.y_min

    def info(self, t_real=None, k_real=None, is_final=True, with_print=True):
        text = '-'*70 + '\n' if is_final else ''
        text += self.ttopt.info(is_final=is_final)
        if t_real is not None:
            text += f' | t_real: {t_real:-7.3f}'
        if k_real is not None:
            text += f' | k: {k_real:-6d} / {self.d:-6d} |'

        if with_print:
            print(text)
        else:
            return text

    def minimize(self, rmax=4, fs_opt=1.):
        self._init()

        self.t0 = tpc()

        if self.with_constraint and not self.with_simple_constraint:
            # Use map into small tensor:
            self.im = TTOptIndexMap(self.d, self.k, None, self.with_less)
            self.im.prep()
            d = self.im.d
        else:
            d = self.d

        self.ttopt = TTOpt(f=self._func, d=d, n=2, evals=self.evals,
            name=self.name, callback=self._callback,
            is_func=False, is_vect=False, with_cache=self.with_cache)

        self.ttopt.minimize(rmax=rmax, Y0=self.Y0, fs_opt=fs_opt,
            add_opt_inner=self.add_opt_inner, add_opt_outer=self.add_opt_outer,
            add_opt_rect=self.add_opt_rect, add_rnd_inner=self.add_rnd_inner,
            add_rnd_outer=self.add_rnd_outer, J0=self.J0)

    def set_opts_init(self):
        # TODO: add args and formulate for the case of constraint with map.
        self.Y0 = None
        self.J0 = None

    def set_opts_spec(self, add_opt_inner=True, add_opt_outer=False, add_opt_rect=False, add_rnd_inner=False, add_rnd_outer=False):
        self.add_opt_inner = add_opt_inner
        self.add_opt_outer = add_opt_outer
        self.add_opt_rect = add_opt_rect
        self.add_rnd_inner = add_rnd_inner
        self.add_rnd_outer = add_rnd_outer

    def _callback(self, info):
        """Function is called whenever the optimization result is improved."""
        y_min = info['last'][1] # Current found optimum
        i_min = info['last'][2] # Multi-index, which relates to current optimum
        evals = info['last'][4] # Current number of the target function calls

        if self.with_constraint and not self.with_simple_constraint:
            i_min = self.im.get(i_min)

        t_real = tpc() - self.t0
        k_real = int(np.sum(i_min))

        self.k_hist.append(k_real)
        self.m_hist.append(evals)
        self.t_hist.append(t_real)
        self.y_hist.append(y_min)

        if self.with_log:
            self.info(None, k_real, is_final=False)

    def _func(self, i):
        if self.with_constraint and self.with_simple_constraint:
            if self.with_less and np.sum(i) > self.k:
                return self.value_none
            if not self.with_less and np.sum(i) != self.k:
                return self.value_none
            return self.f(i)
        elif self.with_constraint:
            i_full = self.im.get(i)
            if i_full is None:
                return self.value_none
            return self.f(i_full)
        else:
            return self.f(i)

    def _init(self):
        self.ttopt = None
        self.k_hist = []
        self.m_hist = []
        self.t_hist = []
        self.y_hist = []
