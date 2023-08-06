#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core module.

Implements the base class to compute LISA response to gravitational waves,
plot them and write a gravitational-wave file.

Authors:
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

import abc
import logging
import os.path
import numpy as np
import matplotlib.pyplot as plt
import h5py

from numpy import pi, cos, sin
from scipy.interpolate import InterpolatedUnivariateSpline
from packaging.version import Version
from packaging.specifiers import SpecifierSet
from lisaconstants import c

from .utils import dot, norm, arrayindex, emitter, receiver

from .meta import __version__
from .meta import __author__


logger = logging.getLogger(__name__)


class Response(abc.ABC):
    """Abstract base class representing a GW source.

    Sampling parameters (``dt``, ``size``, and ``t0``) are used to generate when creating a GW file.
    Note that they are ignored when writing to an existing GW file.

    Args:
        orbits (str): path to orbit file
        orbit_interp_order (int): orbits spline-interpolation order [one of 1, 2, 3, 4, 5]
        dt (float): simulation sampling period [s]
        size (int): simulation size [samples]
        t0 (int): simulation initial time [s]
    """

    SC = [1, 2, 3] #: List of spacecraft indices.
    LINKS = [12, 23, 31, 13, 32, 21] #: List of link indices.

    def __init__(self, orbits, orbit_interp_order=1, dt=0.3, size=259200, t0=0):

        self.git_url = 'https://gitlab.in2p3.fr/lisa-simulation/gw-response'
        self.version = __version__
        self.classname = self.__class__.__name__
        logger.info("Initializing gravitational-wave response (lisagwresponse verion %s)", self.version)

        self.orbits_path = str(orbits) #: str: Path to orbit file.
        self.orbit_interp_order = int(orbit_interp_order) #: int: Orbits spline-interpolation order.

        self.dt = float(dt) #: float: Sampling period [s].
        self.t0 = float(t0) #: float: Initial time [s].
        self.size = int(size) #: int: Simulation size [samples].
        self.fs = 1 / self.dt #: float: Sampling frequency [Hz].
        self.duration = self.size * self.dt #: float: Simulation duration [s].
        self.t = self.t0 + np.arange(self.size) * self.dt #: array: Time array [s].

    @abc.abstractmethod
    def compute_gw_response(self, t, link):
        """Compute link response to gravitational waves.

        If ``t`` is of shape ``(N,)``, the same time array is used for all links;
        otherwise a different time array is used for each link, and ``t`` should have
        the shape ``(N, M)``, if ``(M,)`` is the shape of ``link``.

        The link esponses are expressed as dimensionless relative frequency fluctuations,
        or Doppler shifts, or strain units.

        Args:
            t ((N,) or (N, M) array-like): TCB times [s]
            link ((M,) array-like): link indices

        Returns:
            (N, M) ndarray: Link responses [strain or relative frequency shifts]
        """
        raise NotImplementedError

    def plot(self, t, output=None, gw_name='gravitational wave'):
        """Plot gravitational-wave response.

        Args:
            t (array-like): TCB times [s]
            output (str or None): output file, ``None`` to show the plots
            gw_name (str): optional gravitational-wave source name
        """
        logger.info("Plotting gravitational-wave response")
        plt.figure(figsize=(12, 4))
        response = self.compute_gw_response(t, self.LINKS)
        for link_index, link in enumerate(self.LINKS):
            plt.plot(t, response[:, link_index], label=link)
        plt.grid()
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Link response")
        plt.title(f"Link response to {gw_name}")
        # Save or show glitch
        if output is not None:
            logger.info("Saving plot to %s", output)
            plt.savefig(output, bbox_inches='tight')
        else:
            plt.show()

    def _interpolate_tps(self, tau, sc):
        r"""Return TCB times corresponding to TPS times.

        GW responses :math:`H_{ij}^{t}(\tau)` are computed as functions of TCB.

        To compute GW responses as functions of the receiving spacecraft TPS
        :math:`H_{ij}^{\tau_i}(\tau)`, one needs to convert those reception TPSs
        :math:`\tau` to their TCB equivalent :math:`t^{\tau_i}`, such that

        .. code-block :: python

            H_{ij}^{\tau_i}(\tau) = H_{ij}^{t}(t^{\tau_i}(\tau)) \qs

        Orbit files contain a vector of TCB times for a regularly sampled TPS time grid.

        Use this method to interpolate between these values and obtain the TCB equivalent
        times for an arbitrary vector of TPS times, and for each spacecraft.

        Args:
            tau ((N,) array-like): TPS times [s]
            sc ((M,) array-like): spacecraft indices

        Returns:
            (N, M) ndarray: Equivalent TPS times [s].

        Raises:
            ValueError: If ``tau`` lies outside of the orbit valid range (no extrapolation).
        """
        logger.info("Computing spline interpolation for TPS times")
        interpolate = lambda t, data: InterpolatedUnivariateSpline(t, data, ext='raise')

        with h5py.File(self.orbits_path, 'r') as orbitf:

            # Warn for orbit file development version
            version = Version(orbitf.attrs['version'])
            logger.debug("Using orbit file version %s", version)
            if version.is_devrelease:
                logger.warning("You are using an orbit file in a development version")

            if version in SpecifierSet('== 1.*', True):
                tps = [
                    interpolate(orbitf['/tps/tau'], orbitf[f'/tps/sc_{sci}'])(tau)
                    for sci in sc
                ]
            elif version in SpecifierSet('== 2.*', True):
                times = orbitf.attrs['t0'] + np.arange(orbitf.attrs['size']) * orbitf.attrs['dt']
                orbit_sc = [1, 2, 3]
                tps = [
                    interpolate(times, times + orbitf['tps/delta_t'][:, arrayindex(sci, orbit_sc)])(tau)
                    for sci in sc
                ]
            else:
                raise ValueError(f"unsupported orbit file version '{version}'")

        return np.stack(tps, axis=-1) # (N, M)

    def _write_attr(self, hdf5, prefix, *names):
        """Write a single object attribute as metadata on ``hdf5``.

        This method is used in :meth:`lisagwresponse.Response._write_metadata`
        to write Python self's attributes as HDF5 attributes.

        >>> response = ConcreteResponse()
        >>> response.parameter = 42
        >>> response._write_attr(hdf5, 'prefix_', 'parameter')

        Args:
            hdf5 (:obj:`h5py.Group`): an HDF5 file, or a dataset
            prefix (str): prefix for attribute names
            names* (str): attribute names
        """
        for name in names:
            hdf5.attrs[f'{prefix}{name}'] = self.__getattribute__(name)

    def _write_metadata(self, hdf5, prefix=''):
        """Write relevant object's attributes as metadata on ``hdf5``.

        This is for tracability and reproducibility. All parameters
        necessary to re-instantiate the response object and reproduce the
        exact same simulation should be written to file.

        Use the :meth:`lisagwresponse.Response._write_attr` method.

        .. admonition:: Suclassing notes
            This class is intended to be overloaded by subclasses to write
            additional attributes.

        .. important::
            You MUST call super implementation in subclasses.

        Args:
            hdf5 (:obj:`h5py.Group`): an HDF5 file, or a dataset
            prefix (str): prefix for attribute names
        """
        self._write_attr(hdf5, prefix,
            'git_url', 'version', 'classname',
            'orbits_path', 'orbit_interp_order',
            'dt', 't0', 'size', 'fs', 'duration',
        )

    def write(self, path='gw.h5', mode='a', timeframe='both'):
        """Compute and write the response to a GW file.

        If the GW file does not exist, it is created with the source's sampling parameters and the
        6 link responses are computed according to these parameters and written to file. If the GW
        file already exists, the 6 link responses are computed according to the GW file's sampling
        parameters and added to the file.

        When creating the GW file, metadata are saved as attributes.

        When writing a GW response, we add attributes for each local variable, prefixed with ``gw<i>``,
        where i is the index of the GW response in the file.

        Args:
            path (str): path to the GW file
            mode (str): opening mode
            timeframe (str): timetime to compute responses ('tps', 'tcb', or 'both')
        """
        # pylint: disable=too-many-branches,too-many-statements

        # Open GW file
        logger.info("Opening or creating gravitational-wave file '%s'", path)
        exists = os.path.isfile(path) and mode != 'w'
        with h5py.File(path, mode) as hdf5:

            if exists:
                # If file exists, check version
                version = Version(hdf5.attrs['version'])
                logger.debug("Using already-existing GW file with version %s", version)
                # Warn if development version (might create incompatibilities)
                if version.is_devrelease:
                    logger.warning("You are using a GW file in a development version")
                # Only accept to append to a GW of same version
                if version not in SpecifierSet('== 2.*', True):
                    raise ValueError(f"unsupported GW file version '{version}'")
                # Only accept ``timeframe`` value that matches the file's
                if timeframe != hdf5.attrs['timeframe']:
                    raise ValueError(
                        f"timeframe parameter '{timeframe}' does not match that "
                        f"of the GW file '{hdf5.attrs['timeframe']}'")
                # Create time vector from file's sampling parameters
                t = hdf5.attrs['t0'] + np.arange(hdf5.attrs['size']) * hdf5.attrs['dt']
                logger.debug(
                    "Using file's sampling parameters (t0=%.1f, size=%d, dt=%.2f)",
                    hdf5.attrs['t0'], hdf5.attrs['size'], hdf5.attrs['dt'])
            else:
                # File does not exist:
                logger.debug("Creating new GW file with version %s", self.version)
                # Warn if development version (might create incompatibilities)
                if Version(self.version).is_devrelease:
                    logger.warning("You are using a GW file in a development version")
                # Set global metadata
                logger.debug("Setting global metadata")
                self._write_metadata(hdf5)
                hdf5.attrs['gw_count'] = 0
                hdf5.attrs['timeframe'] = timeframe
                # Create link response datasets
                if timeframe in ['both', 'tcb']:
                    hdf5['tcb/y'] = np.zeros((self.size, 6))
                if timeframe in ['both', 'tps']:
                    hdf5['tps/y'] = np.zeros((self.size, 6))
                # Use instance's time vector
                t = self.t

            # Setting metadata for this source
            logger.debug("Setting new source metadata")
            ngw = int(hdf5.attrs['gw_count'])
            hdf5.attrs['gw_count'] = ngw + 1
            self._write_metadata(hdf5, prefix=f'gw{ngw}_')

            # Compute equivalent TCB times for TPSs
            receivers = arrayindex(receiver(self.LINKS), self.SC)
            if timeframe == 'both':
                tau = self._interpolate_tps(t, self.SC) # (N, 3)
                tau_links = tau[:, receivers] # (N, 6)
                t_links = np.tile(t[:, np.newaxis], 6) # (N, 6)
                times = np.concatenate([t_links, tau_links], axis=0) # (2N, 6)
            elif timeframe == 'tcb':
                times = t # (N)
            elif timeframe == 'tps':
                tau = self._interpolate_tps(t, self.SC) # (N, 3)
                tau_links = tau[:, receivers] # (N, 6)
                times = np.tile(t[:, np.newaxis], 6) # (N, 6)
            else:
                raise ValueError(f"invalid timeframe '{timeframe}'")

            # Compute link response
            response = self.compute_gw_response(times, self.LINKS) # (2N, 6) or (N, 6)

            # Add response to link datasets
            logger.info("Writing link response datasets")
            if timeframe == 'tcb':
                hdf5['tcb/y'][:] += response # (N, 6)
            if timeframe == 'tps':
                hdf5['tps/y'][:] += response # (N, 6)
            if timeframe == 'both':
                hdf5['tcb/y'][:] += response[:len(t)] # (N, 6)
                hdf5['tps/y'][:] += response[len(t):] # (N, 6)

        # Closing file
        logger.info("Closing gravitational-wave file '%s'", path)


class ReadResponse(Response):
    """Read already-computed link responses.

    Use this class if the link responses are available as Numpy arrays,
    and you want to use GW files or the interface offered by this package.

    To honor the source's sampling parameters, the input data may be resampled using
    spline interpolation. If you do not wish to interpolate, make sure to instantiate
    the source with sampling parameters matching your data.

    Args:
        t ((N,) array-like): TCB times associated with link responses [s]
        y_12 ((N,) array-like): response of link 12
        y_23 ((N,) array-like): response of link 23
        y_31 ((N,) array-like): response of link 31
        y_13 ((N,) array-like): response of link 13
        y_32 ((N,) array-like): response of link 32
        y_21 ((N,) array-like): response of link 21
        interp_order (int): response spline-interpolation order [one of 1, 2, 3, 4, 5]
        **kwargs: all other args from :class:`lisagwresponse.Response`
    """

    def __init__(self, t, y_12, y_23, y_31, y_13, y_32, y_21, interp_order=1, **kwargs):
        super().__init__(**kwargs)
        self.interp_order = int(interp_order) #: int: Response spline-interpolation order.

        # Compute spline interpolation
        logger.info("Computing spline interpolation from time series")
        data = {12: y_12, 23: y_23, 31: y_31, 13: y_13, 32: y_32, 21: y_21}
        self.interpolants = {
            link: InterpolatedUnivariateSpline(t, data[link], k=self.interp_order, ext='zeros')
            for link in self.LINKS
        } #: Dictionary of interpolating spline functions (link indices as keys).

    def compute_gw_response(self, t, link):
        # Interpolate strain
        t = np.asarray(t)
        if t.ndim == 1:
            responses = [self.interpolants[a_link](t) for a_link in link]
        elif t.ndim == 2:
            responses = [self.interpolants[a_link](t[:, i]) for i, a_link in enumerate(link)]
        else:
            raise TypeError(f"invalid time array shape '{t.shape}'")
        return np.stack(responses, axis=-1) # (N, M)


class ResponseFromStrain(Response, abc.ABC):
    """Abstract base that computes link responses from GW strain time series.

    Args:
        gw_beta (float): ecliptic latitude [rad]
        gw_lambda (float): ecliptic longitude [rad]
        x (callable): spacecraft x-position interpolating functions, overrides orbits [m]
        y (callable): spacecraft y-position interpolating functions, overrides orbits [m]
        z (callable): spacecraft z-position interpolating functions, overrides orbits [m]
        ltt (callable): light travel time interpolating functions, overrides orbits [s]
        t0 (float or str): initial time [s], or ``'orbits'`` to match orbit file's initial time
        **kwargs: all other args from :class:`lisagwresponse.Response`
    """

    def __init__(self,
                 gw_beta,
                 gw_lambda,
                 x=None,
                 y=None,
                 z=None,
                 ltt=None,
                 t0='orbits',
                 **kwargs):

        # Forward numerical values of t0 to superclass
        if t0 != 'orbits':
            kwargs['t0'] = t0

        super().__init__(**kwargs)
        self.gw_beta = float(gw_beta)
        self.gw_lambda = float(gw_lambda)

        # Handle orbits
        if x is not None or y is not None or z is not None or ltt is not None:
            logger.info("Using provided functions for orbits")
            self._set_orbits(x, y, z, ltt)
        else:
            logger.info("Reading orbits from file '%s'", self.orbits_path)
            self._interpolate_orbits()
            if t0 == 'orbits':
                logger.debug("Reading initial time from orbit file '%s'", self.orbits_path)
                with h5py.File(self.orbits_path, 'r') as orbitf:
                    # Warn for orbit file development version
                    version = Version(orbitf.attrs['version'])
                    logger.debug("Using orbit file version %s", version)
                    if version.is_devrelease:
                        logger.warning("You are using an orbit file in a development version")
                    # Switch between versions
                    if version in SpecifierSet('== 1.*', True):
                        self.t0 = float(orbitf.attrs['tau0'])
                    elif version in SpecifierSet('== 2.*', True):
                        self.t0 = float(orbitf.attrs['t0'])
                    else:
                        raise ValueError(f"unsupported orbit file version '{version}'")

        # Compute source-localization vector basis
        self.k = np.array([
            -cos(self.gw_beta) * cos(self.gw_lambda),
            -cos(self.gw_beta) * sin(self.gw_lambda),
            -sin(self.gw_beta),
        ]) #: Wave propagation unit vector.
        self.u = np.array([
            sin(self.gw_lambda),
            -cos(self.gw_lambda),
            0
        ])
        self.v = np.array([
            -sin(self.gw_beta) * cos(self.gw_lambda),
            -sin(self.gw_beta) * sin(self.gw_lambda),
            cos(self.gw_beta),
        ])

    def _write_metadata(self, hdf5, prefix=''):
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, 'gw_beta', 'gw_lambda')

    def _interpolate_orbits(self):
        """Interpolate orbit data (spacecraft positions and light travel times).

        Also check that orbit file is valid and supported.

        Raises:
            ValueError if orbit file is not supported.
        """
        logger.info("Computing spline interpolation for orbits")
        interpolate = lambda t, data: InterpolatedUnivariateSpline(
                t, data, k=self.orbit_interp_order, ext='raise')

        with h5py.File(self.orbits_path, 'r') as orbitf:

            # Warn for orbit file development version
            version = Version(orbitf.attrs['version'])
            logger.debug("Using orbit file version %s", version)
            if version.is_devrelease:
                logger.warning("You are using an orbit file in a development version")

            if version in SpecifierSet('== 1.*', True):
                self.x = {
                    sc: interpolate(orbitf['tcb/t'], orbitf[f'tcb/sc_{sc}']['x'])
                    for sc in self.SC
                }
                self.y = {
                    sc: interpolate(orbitf['tcb/t'], orbitf[f'tcb/sc_{sc}']['y'])
                    for sc in self.SC
                }
                self.z = {
                    sc: interpolate(orbitf['tcb/t'], orbitf[f'tcb/sc_{sc}']['z'])
                    for sc in self.SC
                }
                self.ltt = {
                    link: interpolate(orbitf['tcb/t'], orbitf[f'tcb/l_{link}']['tt'])
                    for link in self.LINKS
                }
            elif version in SpecifierSet('== 2.*', True):
                times = orbitf.attrs['t0'] + np.arange(orbitf.attrs['size']) * orbitf.attrs['dt']
                self.x = {
                    sc: interpolate(times, orbitf['tcb/x'][:, i, 0])
                    for i, sc in enumerate(self.SC)
                }
                self.y = {
                    sc: interpolate(times, orbitf['tcb/x'][:, i, 1])
                    for i, sc in enumerate(self.SC)
                }
                self.z = {
                    sc: interpolate(times, orbitf['tcb/x'][:, i, 2])
                    for i, sc in enumerate(self.SC)
                }
                self.ltt = {
                    link: interpolate(times, orbitf['tcb/ltt'][:, i])
                    for i, link in enumerate(self.LINKS)
                }
            else:
                raise ValueError(f"unsupported orbit file version '{version}'")

    def _set_orbits(self, x, y, z, ltt):
        """Set orbit data from dictionaries (spacecraft positions and light travel times).

        Args:
            x (callable): spacecraft x-position interpolating functions, overrides orbits [m]
            y (callable): spacecraft y-position interpolating functions, overrides orbits [m]
            z (callable): spacecraft z-position interpolating functions, overrides orbits [m]
            ltt (callable): light travel time interpolating functions, overrides orbits [s]
        """
        # pylint: disable=cell-var-from-loop
        # We use default values for `val` in lambdas to capture the values
        self.x = {
            sc: x[sc] if callable(x[sc]) else lambda t, val=x[sc]: float(val)
            for sc in self.SC
        }
        self.y = {
            sc: y[sc] if callable(y[sc]) else lambda t, val=y[sc]: float(val)
            for sc in self.SC
        }
        self.z = {
            sc: z[sc] if callable(z[sc]) else lambda t, val=z[sc]: float(val)
            for sc in self.SC
        }
        self.ltt = {
            link: ltt[link] if callable(ltt[link]) else lambda t, val=ltt[link]: float(val)
            for link in self.LINKS
        }

    @abc.abstractmethod
    def compute_hplus(self, t):
        """Compute +-polarized gravitational-wave strain :math:`h_+(t)` in the BCRS.

        Args:
            t (array-like): TCB times [s]
        """
        raise NotImplementedError

    @abc.abstractmethod
    def compute_hcross(self, t):
        """Compute x-polarized gravitational-wave strain :math:`h_\\times(t)` in the BCRS.

        Args:
            t (array-like): TCB times [s]
        """
        raise NotImplementedError

    def compute_gw_response(self, t, link):
        """Compute link response to gravitational waves (see :doc:`model`).

        If ``t`` is of shape ``(N,)``, the same time array is used for all links;
        otherwise a different time array is used for each link, and ``t`` should have
        the shape ``(N, M)``, if ``(M,)`` is the shape of ``link``.

        The link esponses are expressed as dimensionless relative frequency fluctuations,
        or Doppler shifts, or strain units.

        Args:
            t ((N,) or (N, M) array-like): TCB times [s]
            link ((M,) array-like): link indices

        Returns:
            (N, M) ndarray: Link responses [strain or relative frequency shifts]
        """
        # pylint: disable=too-many-locals
        logger.info("Computing gravitational-wave response for links %s", link)

        # Broadcast times if needed
        t = np.asarray(t)
        if t.ndim == 1:
            t = np.tile(t[:, np.newaxis], len(link)) # (N, M)

        # Compute emission and reception time at spacecraft
        logger.debug("Computing emission time at spacecraft")
        trec = t # (N, M)
        temi = np.copy(t) # (N, M)
        for link_index, a_link in enumerate(link):
            temi[:, link_index] -= self.ltt[a_link](t[:, link_index]) # (N, M)

        # Compute spacecraft positions at emission and reception
        try:
            logger.debug("Computing receiver position at reception time")
            xrec = np.empty((*t.shape, 3)) # (N, M, 3)
            for i, (a_link, a_receiver) in enumerate(zip(link, receiver(link))):
                xrec[:, i, 0] = self.x[a_receiver](trec[:, i]) # (N,)
                xrec[:, i, 1] = self.y[a_receiver](trec[:, i]) # (N,)
                xrec[:, i, 2] = self.z[a_receiver](trec[:, i]) # (N,)
            logger.debug("Computing emitter position at emission time")
            xemi = np.empty((*t.shape, 3)) # (N, M, coord)
            for i, (a_link, an_emitter) in enumerate(zip(link, emitter(link))):
                xemi[:, i, 0] = self.x[an_emitter](temi[:, i]) # (N,)
                xemi[:, i, 1] = self.y[an_emitter](temi[:, i]) # (N,)
                xemi[:, i, 2] = self.z[an_emitter](temi[:, i]) # (N,)
        except ValueError as error:
            logger.error("Missing orbit information")
            raise ValueError("missing orbit information, use longer orbit file or adjust sampling") from error

        # Compute link unit vector
        logger.debug("Computing link unit vector")
        n = (xrec - xemi) # (N, M, 3)
        n /= norm(n)[..., np.newaxis] # (N, M, 3)

        # Compute equivalent emission and reception time at the Sun
        logger.debug("Computing equivalent reception time at the Sun")
        trec_sun = trec - dot(xrec, self.k) / c # (N, M)
        logger.debug("Computing equivalent emission time at the Sun")
        temi_sun = temi - dot(xemi, self.k) / c # (N, M)

        # Compute antenna pattern functions
        logger.debug("Computing antenna pattern functions")
        xiplus = dot(n, self.u)**2 - dot(n, self.v)**2 # (N, M)
        xicross = 2 * dot(n, self.u) * dot(n, self.v) # (N, M)

        # Compute hplus and hcross contributions
        logger.debug("Computing gravitational-wave response")
        termplus = np.empty_like(temi_sun) # (N, M)
        termcross = np.empty_like(trec_sun) # (N, M)
        for i in range(len(link)):
            termplus[:, i] = self.compute_hplus(temi_sun[:, i]) - self.compute_hplus(trec_sun[:, i]) # (N,)
            termcross[:, i] = self.compute_hcross(temi_sun[:, i]) - self.compute_hcross(trec_sun[:, i]) # (N,)
        return (termplus * xiplus + termcross * xicross) / (2 * (1 - dot(n, self.k)))

    def plot(self, t, output=None, gw_name='gravitational wave'):
        """Plot gravitational-wave response and strain.

        Args:
            t (array-like): TCB times [s]
            output (str or None): output file, None to show the plots
            gw_name (str): optional gravitational-wave source name
        """
        # Initialize the plot
        _, axes = plt.subplots(2, 1, figsize=(12, 8))
        axes[1].set_xlabel("Time [s]")
        axes[0].set_title(f"ResponseFromStrain and link response to {gw_name}")
        # Computing and plotting response
        logger.info("Plotting gravitational-wave response")
        axes[0].set_ylabel("Link response")
        response = self.compute_gw_response(t, self.LINKS) # (N, 6)
        for link_index, link in enumerate(self.LINKS):
            axes[0].plot(t, response[:, link_index], label=link)
        # Computing and plotting strain
        logger.info("Plotting gravitational-wave strain")
        axes[1].set_ylabel("Gravitational-wave strain")
        hplus = self.compute_hplus(t) # (N,)
        hcross = self.compute_hcross(t) # (N,)
        axes[1].plot(t, hplus, label=r'$h_+$')
        axes[1].plot(t, hcross, label=r'$h_\times$')
        # Add legend and grid
        for axis in axes:
            axis.legend()
            axis.grid()
        # Save or show glitch
        if output is not None:
            logger.info("Saving plot to %s", output)
            plt.savefig(output, bbox_inches='tight')
        else:
            plt.show()


class ReadStrain(ResponseFromStrain):
    """Reads already-computed strain.

    Use this class if you wish to use your own waveform generator code but want to compute
    the link responses and and use the interface offered by this package.

    To honor the source's sampling parameters, the input data may be resampled using
    spline interpolation. If you do not wish to interpolate, make sure to instantiate
    the source with sampling parameters matching your data.

    Args:
        t ((N,) array-like): TCB times [s]
        hplus ((N,) array-like): +-polarized strain :math:`h_+` in the BCRS
        hcross ((N,) array-like): x-polarized strain :math:`h_\\times` in the BCRS
        strain_interp_order (int): strain spline-interpolation order [one of 1, 2, 3, 4, 5]
        **kwargs: all other args from :class:`lisagwresponse.Response`
    """

    def __init__(self, t, hplus, hcross, strain_interp_order=5, **kwargs):
        super().__init__(**kwargs)
        self.strain_interp_order = int(strain_interp_order) #: int: ResponseFromStrain interpolation order.

        # Interpolate strain
        logger.info("Computing spline interpolation for gravitational-wave strain")
        self.hplus = self._interpolate_strain(t, hplus)
        """+-polarized strain :math:`h_+` interpolating function."""
        self.hcross = self._interpolate_strain(t, hcross)
        """x-polarized strain :math:`h_\\times` interpolating function."""

    def _write_metadata(self, hdf5, prefix=''):
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, 'strain_interp_order')

    def _interpolate_strain(self, t, data):
        """Interpolate strain data.

        Args:
            t (array-like): timestamps
            data (array-like): data to interpolate

        Returns:
            Interpolating spline function.
        """
        return InterpolatedUnivariateSpline(t, data, k=self.strain_interp_order, ext='zeros')

    def compute_hplus(self, t):
        return self.hplus(t)

    def compute_hcross(self, t):
        return self.hcross(t)


class GalacticBinary(ResponseFromStrain):
    """Represent a chirping galactic binary.

    Args:
        A (float): strain amplitude
        f (float): frequency [Hz]
        df (float): frequency derivative [Hz/s]
        phi0 (float): initial phase [rad]
        iota (float): inclination angle [rad]
        psi (float): polarization angle [rad]
        **kwargs: all other args from :class:`lisagwrespons.ResponseFromStrain`
    """

    def __init__(self, A, f, df=0, phi0=0, iota=0, psi=0, **kwargs):
        super().__init__(**kwargs)
        self.A = float(A)
        self.f = float(f)
        self.df = float(df)
        self.phi0 = float(phi0)
        self.iota = float(iota)
        self.psi = float(psi)

    def _write_metadata(self, hdf5, prefix=''):
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, 'A', 'f', 'df', 'phi0', 'iota', 'psi')

    def compute_strain_in_source_frame(self, t):
        """Compute strain in the source frame.

        Args:
            t (array-like): TCB times [s]

        Returns:
            tuple: Couple of arrays ``(hplus, hcross)``, each of shape ``(len(t))``.
        """
        logger.info("Compute gravitational-wave strain in the source frame")
        phase = pi * self.df * t**2 + 2 * pi * self.f * t - self.phi0
        hplus = -self.A * (1 + cos(self.iota)**2) * cos(phase)
        hcross = -2 * self.A * cos(self.iota) * sin(phase)
        return (hplus, hcross)

    def compute_hplus(self, t):
        logger.info("Compute +-polarized gravitational-wave strain in the BCRS")
        hplus_source, hcross_source = self.compute_strain_in_source_frame(t)
        return hplus_source * cos(2 * self.psi) - hcross_source * sin(2 * self.psi)

    def compute_hcross(self, t):
        logger.info("Compute x-polarized gravitational-wave strain in the BCRS")
        hplus_source, hcross_source = self.compute_strain_in_source_frame(t)
        return hplus_source * sin(2 * self.psi) + hcross_source * cos(2 * self.psi)
