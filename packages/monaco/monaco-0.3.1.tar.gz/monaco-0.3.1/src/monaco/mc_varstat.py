# mc_varstat.py
from __future__ import annotations

# Somewhat hacky type checking to avoid circular imports:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from monaco.mc_var import Var

import numpy as np
from copy import copy
from statistics import mode
from scipy.stats.mstats import gmean
from monaco.helper_functions import get_list
from monaco.gaussian_statistics import pct2sig, sig2pct
from monaco.order_statistics import (order_stat_P_k, order_stat_TI_k, get_iP)
from monaco.mc_enums import StatBound, VarStatType, VarStatSide
from typing import Any, Callable


class VarStat:
    """
    A variable statistic for a Monte-Carlo variable.

    Parameters
    ----------
    var : monaco.mc_var.Var
        The variable to generate statistics for.
    stat : monaco.mc_enums.VarStatType | Callable
        The statistic to generate. Can be custom.
    statkwargs : dict[str:Any]
        The keyword arguments for the variable statistic.
    name : str
        The name of this variable statistic.

    Attributes
    ----------
    nums : numpy.ndarray
        The output of the variable statistic function applied to `var.nums`
    vals : list[Any]
        The values for the `nums` as determined by `var.nummap`

    Notes
    -----
    These are the valid stats with their statkwargs

    max()
        No kwargs
    min()
        No kwargs
    median()
        No kwargs
    mean()
        No kwargs
    geomean()
        No kwargs
    mode()
        No kwargs
    sigma(sig : float, bound : monaco.mc_enums.StatBound)
        `sig` is the gaussian sigma value, `-inf < sig < inf`.

        `bound` is the statistical bound, ether `'1-sided'` or `'2-sided'`.
        Default is `'2-sided'`.
    gaussianP(p : float, bound : monaco.mc_enums.StatBound)
        `p` is the percentile, `0 < p < 1`.

        `bound` is the statistical bound, ether `'1-sided'` or `'2-sided'`.
        Default is `'2-sided'`.
    orderstatTI(p : float, c : float, bound : monaco.mc_enums.StatBound)
        `p` is the percentage, `0 < p < 1`

        `c` is the confidence, `0 < c < 1`. Default is `0.95`.

        `bound` is the statistical bound, ether `'1-sided'`, `'2-sided'`, or
        `'all'`. Default is `'2-sided'`.
    orderstatP(p : float, c : float, bound : monaco.mc_enums.StatBound)
        `p` is the percentage, `0 < p < 1`

        `c` is the confidence, `0 < c < 1`. Default is `0.95`.

        `bound` is the statistical bound, ether `'1-sided lower'`,
        `'1-sided upper'`, `'2-sided'`, `'all'`, or '`nearest'`. Default is
        `'2-sided'`.
    """
    def __init__(self,
                 var         : Var,
                 stat        : VarStatType | Callable,
                 statkwargs  : dict[str, Any] = None,
                 bootstrap   : bool = False,
                 bootstrap_k : int = 10,
                 conf        : float = 0.95,
                 name        : str = None,
                 seed        : int = np.random.get_state(legacy=False)['state']['key'][0],
                 ):

        self.var = var
        self.stat = stat
        if statkwargs is None:
            statkwargs = dict()
        self.statkwargs = statkwargs

        self.nums : np.ndarray = np.array([])
        self.vals : list[Any] | np.ndarray = []
        self.name = name

        self.bootstrap = bootstrap
        self.bootstrap_k = bootstrap_k
        self.conf = conf

        if isinstance(stat, Callable):
            self.setName(str(stat))
            self.genStatsFunction(fcn=stat, fcnkwargs=statkwargs)
        elif stat == VarStatType.MAX:
            self.setName('Max')
            self.genStatsFunction(fcn=np.max)
        elif stat == VarStatType.MIN:
            self.setName('Min')
            self.genStatsFunction(fcn=np.min)
        elif stat == VarStatType.MEDIAN:
            self.setName('Median')
            self.genStatsFunction(fcn=np.median)
        elif stat == VarStatType.MEAN:
            self.setName('Mean')
            self.genStatsFunction(fcn=np.mean)
        elif stat == VarStatType.GEOMEAN:
            self.setName('Geometric Mean')
            self.genStatsFunction(fcn=gmean)
        elif stat == VarStatType.MODE:
            self.setName('Mode')
            self.genStatsFunction(fcn=mode)
        elif stat == VarStatType.SIGMA:
            self.genStatsSigma()
        elif stat == VarStatType.GAUSSIANP:
            self.genStatsGaussianP()
        elif stat == VarStatType.ORDERSTATTI:
            self.genStatsOrderStatTI()
        elif stat == VarStatType.ORDERSTATP:
            self.genStatsOrderStatP()
        else:
            raise ValueError(f'stat={stat} must be callable, or one of the following: ' +
                             f'{VarStatType.MAX}, {VarStatType.MIN}, {VarStatType.MEDIAN}, ' +
                             f'{VarStatType.MEAN}, {VarStatType.GEOMEAN}, {VarStatType.MODE}, ' +
                             f'{VarStatType.SIGMA}, {VarStatType.GAUSSIANP}, ' +
                             f'{VarStatType.ORDERSTATTI}, {VarStatType.ORDERSTATP}')


    def genStatsSigma(self) -> None:
        """
        Get the value of the variable at the inputted sigma value, assuming
        a gaussian distribution.
        """
        if 'sig' not in self.statkwargs:
            raise ValueError(f'{self.stat} requires the kwarg ''sig''')
        if 'bound' not in self.statkwargs:
            self.bound = StatBound.TWOSIDED
        else:
            self.bound = self.statkwargs['bound']

        self.sig = self.statkwargs['sig']
        self.p = sig2pct(self.sig, bound=self.bound)
        self.setName(f'{self.sig} Sigma')
        self.genStatsFunction(self.sigma)


    def genStatsGaussianP(self) -> None:
        """
        Get the value of the variable at the inputted percentile value,
        assuming a gaussian distribution.
        """
        if 'p' not in self.statkwargs:
            raise ValueError(f'{self.stat} requires the kwarg ''p''')
        if 'bound' not in self.statkwargs:
            self.bound = StatBound.TWOSIDED
        else:
            self.bound = self.statkwargs['bound']

        self.p = self.statkwargs['p']
        self.sig = pct2sig(self.p, bound=self.bound)
        self.setName(f'Guassian {self.p*100}%')
        self.genStatsFunction(self.sigma)


    def sigma(self,
              x,  # TODO: explicit typing here
              ) -> float:
        """
        Calculate the sigma value of a normally distributed list of numbers.

        Parameters
        ----------
        x : TODO typing
            The numbers to calculate the sigma value for.
        """
        std = np.std(x)
        return np.mean(x) + self.sig*std


    def genStatsFunction(self,
                         fcn       : Callable,
                         fcnkwargs : dict[str, Any] = None,
                         ) -> None:
        """
        A wrapper function to generate statistics via a generic function.

        Parameters
        ----------
        fcn : Callable
            The function used to generate the desired statistics.
        fcnkwargs : dict[str, Any]
            The keyword arguments for the function.
        """
        if fcnkwargs is None:
            fcnkwargs = dict()

        if self.var.isscalar:
            self.nums = fcn(self.var.nums, **fcnkwargs)
            self.vals = copy(self.nums)
            if self.var.nummap is not None:
                self.vals = [self.var.nummap[num] for num in self.nums]
            '''
            if self.bootstrap:
                from scipy.stats import bootstrap
                n = order_stat_TI_n(self.bootstrap_k, p=0.5, c=self.conf)
                res = bootstrap(self.var.nums, fcn, **fcnkwargs,
                                 confidence_level=self.conf, n_resamples=n,
                                 random_state=self.var.seed)
            '''

        elif self.var.maxdim == 1:
            nums_list = get_list(self.var.nums)
            npoints = max(len(x) for x in nums_list)
            self.nums = np.empty(npoints)
            for i in range(npoints):
                numsatidx = [x[i] for x in nums_list if len(x) > i]
                self.nums[i] = fcn(numsatidx, **fcnkwargs)
            self.vals = copy(self.nums)
            if self.var.nummap is not None:
                self.vals = np.array([[self.var.nummap[x] for x in y] for y in self.nums])

        else:
            # Suppress warning since this will become valid when Var is split
            # warn('VarStat only available for scalar or 1-D data')
            pass


    def genStatsOrderStatTI(self) -> None:
        """Get the order statistic tolerance interval value of the variable."""
        self.checkOrderStatsKWArgs()

        if self.bound == StatBound.ONESIDED and self.p >= 0.5:
            self.side = VarStatSide.HIGH
        elif self.bound == StatBound.ONESIDED:
            self.side = VarStatSide.LOW
        elif self.bound == StatBound.TWOSIDED:
            self.side = VarStatSide.BOTH
        elif self.bound == StatBound.ALL:
            self.bound = StatBound.TWOSIDED
            self.side = VarStatSide.ALL
        else:
            raise ValueError(f'{self.bound} is not a valid bound for genStatsOrderStatTI')

        self.setName(f'{self.bound} P{round(self.p*100,4)}/{round(self.c*100,4)}% ' +
                      'Confidence Interval')

        self.k = order_stat_TI_k(n=self.var.ncases, p=self.p, c=self.c, bound=self.bound)

        if self.var.isscalar:
            sortednums = sorted(self.var.nums)
            if self.side == VarStatSide.LOW:
                sortednums.reverse()
            if self.side in (VarStatSide.HIGH, VarStatSide.LOW):
                self.nums = np.array(sortednums[-self.k])
                if self.var.nummap is not None:
                    self.vals = self.var.nummap[self.nums.item()]
            elif self.side == VarStatSide.BOTH:
                self.nums = np.array([sortednums[self.k-1], sortednums[-self.k]])
                if self.var.nummap is not None:
                    self.vals = np.array([self.var.nummap[self.nums[0]],
                                          self.var.nummap[self.nums[1]]])
            elif self.side == VarStatSide.ALL:
                self.nums = np.array([sortednums[self.k-1],
                                      np.median(sortednums),
                                      sortednums[-self.k]])
                if self.var.nummap is not None:
                    self.vals = np.array([self.var.nummap[self.nums[0]],
                                          self.var.nummap[self.nums[1]],
                                          self.var.nummap[self.nums[2]]])
            if self.var.nummap is None:
                self.vals = copy(self.nums)

        elif self.var.maxdim == 1:
            npoints = max(x.shape[0] if len(x.shape) > 0 else 0 for x in self.var.nums)
            self.nums = np.empty(npoints)
            if self.side == VarStatSide.BOTH:
                self.nums = np.empty((npoints, 2))
            elif self.side == VarStatSide.ALL:
                self.nums = np.empty((npoints, 3))
            for i in range(npoints):
                numsatidx = [x[i] for x in self.var.nums
                             if (len(x.shape) > 0 and x.shape[0] > i)]
                sortednums = sorted(numsatidx)
                if self.side == VarStatSide.LOW:
                    sortednums.reverse()
                if self.side in (VarStatSide.HIGH, VarStatSide.LOW):
                    self.nums[i] = sortednums[-self.k]
                elif self.side == VarStatSide.BOTH:
                    self.nums[i, :] = [sortednums[self.k - 1], sortednums[-self.k]]
                elif self.side == VarStatSide.ALL:
                    self.nums[i, :] = [sortednums[self.k - 1],
                                       sortednums[int(np.round(len(sortednums)/2)-1)],
                                       sortednums[-self.k]]
            if self.var.nummap is not None:
                self.vals = np.array([[self.var.nummap[x] for x in y] for y in self.nums])
            else:
                self.vals = copy(self.nums)

        else:
            # Suppress warning since this will become valid when Var is split
            # warn('VarStat only available for scalar or 1-D data')
            pass


    def genStatsOrderStatP(self) -> None:
        """Get the order statistic percentile value of the variable."""
        self.checkOrderStatsKWArgs()

        bound = self.bound
        if self.bound not in (StatBound.ONESIDED_UPPER, StatBound.ONESIDED_LOWER,
                              StatBound.TWOSIDED, StatBound.NEAREST, StatBound.ALL):
            raise ValueError(f'{self.bound} is not a valid bound for genStatsOrderStatP')
        elif self.bound in (StatBound.NEAREST, StatBound.ALL):
            bound = StatBound.TWOSIDED

        self.setName(f'{self.bound} {self.c*100}% Confidence Bound around ' +
                     f'{self.p*100}th Percentile')

        self.k = order_stat_P_k(n=self.var.ncases, P=self.p, c=self.c, bound=bound)

        (iPl, iP, iPu) = get_iP(n=self.var.ncases, P=self.p)
        if self.var.isscalar:
            sortednums = sorted(self.var.nums)
            if self.bound == StatBound.ONESIDED_LOWER:
                self.nums = np.array(sortednums[iPl - self.k])
            elif self.bound == StatBound.ONESIDED_UPPER:
                self.nums = np.array(sortednums[iPu + self.k])
            elif self.bound == StatBound.NEAREST:
                self.nums = np.array(sortednums[iP])
            if self.bound in (StatBound.ONESIDED_LOWER,
                              StatBound.ONESIDED_UPPER,
                              StatBound.NEAREST):
                if self.var.nummap is not None:
                    self.vals = self.var.nummap[self.nums.item()]
            elif self.bound == StatBound.TWOSIDED:
                self.nums = np.array([sortednums[iPl - self.k], sortednums[iPu + self.k]])
                if self.var.nummap is not None:
                    self.vals = np.array([self.var.nummap[self.nums[0]],
                                          self.var.nummap[self.nums[1]]])
            elif self.bound == StatBound.ALL:
                self.nums = np.array([sortednums[iPl - self.k],
                                      sortednums[iP],
                                      sortednums[iPu + self.k]])
                if self.var.nummap is not None:
                    self.vals = np.array([self.var.nummap[self.nums[0]],
                                          self.var.nummap[self.nums[1]],
                                          self.var.nummap[self.nums[2]]])
            if self.var.nummap is None:
                self.vals = copy(self.nums)

        elif self.var.maxdim == 1:
            npoints = max(len(get_list(x)) for x in self.var.nums)
            self.nums = np.empty(npoints)
            if self.bound == StatBound.TWOSIDED:
                self.nums = np.empty((npoints, 2))
            elif self.bound == StatBound.ALL:
                self.nums = np.empty((npoints, 3))
            for i in range(npoints):
                numsatidx = [get_list(x)[i] for x in self.var.nums if len(get_list(x)) > i]
                sortednums = sorted(numsatidx)
                if self.bound == StatBound.ONESIDED_LOWER:
                    self.nums[i] = sortednums[iPl - self.k]
                elif self.bound == StatBound.ONESIDED_UPPER:
                    self.nums[i] = sortednums[iPu + self.k]
                elif self.bound == StatBound.NEAREST:
                    self.nums[i] = sortednums[iP]
                elif self.bound == StatBound.TWOSIDED:
                    self.nums[i, :] = [sortednums[iPl - self.k], sortednums[iPu + self.k]]
                elif self.bound == StatBound.ALL:
                    self.nums[i, :] = [sortednums[iPl - self.k],
                                       sortednums[iP],
                                       sortednums[iPu + self.k]]
            if self.var.nummap is not None:
                self.vals = np.array([[self.var.nummap[x] for x in y] for y in self.nums])
            else:
                self.vals = copy(self.nums)

        else:
            # Suppress warning since this will become valid when Var is split
            # warn('VarStat only available for scalar or 1-D data')
            pass


    def checkOrderStatsKWArgs(self) -> None:
        """Check the order statistic keyword arguments."""
        if 'p' not in self.statkwargs:
            raise ValueError(f'{self.stat} requires the kwarg ''p''')
        else:
            self.p = self.statkwargs['p']
        if 'c' not in self.statkwargs:
            self.c = 0.95
        else:
            self.c = self.statkwargs['c']
        if 'bound' not in self.statkwargs:
            self.bound = StatBound.TWOSIDED
        else:
            self.bound = self.statkwargs['bound']


    def setName(self,
                name : str,
                ) -> None:
        """
        Set the name for this variable statistic.

        Parameters
        ----------
        name : str
            The new name.
        """
        if self.name is None:
            self.name = name
