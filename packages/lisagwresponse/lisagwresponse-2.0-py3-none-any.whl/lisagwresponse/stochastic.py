#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stochastic sources and background.

Authors:
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
    Arianna Renzini <arenzini@caltech.edu>
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
import healpy

from numpy import pi
from scipy.interpolate import InterpolatedUnivariateSpline
from lisaconstants import c, au

from .response import Response, ResponseFromStrain


logger = logging.getLogger(__name__)


class StochasticPointSource(ResponseFromStrain):
    """Represent a point-like gravitational-wave stochastic source.

    This class generates random strain time series, following a given power
    spectral density. Alternatively, you can use ``hplus`` and ``hcross``
    to provide arrays of strain correctly sampled:

        * sampling rate must match ``dt``
        * initial time must match ``StochasticPointSource.t0_with_margin(t0)``
        * size must match ``StochasticPointSource.size_with_margin(size, dt)``

    This class is used to represent independant pixels in a whole-sky
    :class:`lisagwresponse.StochasticBackground` instance.

    Args:
        generator (callable):
            function ``(float, int) -> float`` of the sampling frequency [Hz]
            and size [samples] to generate strain time series
        hplus ((N,) array-like): +-polarized strain :math:`h_+`
        hcross ((N,) array-like): x-polarized strain :math:`h_\\times`
        strain_interp_order (int): strain spline-interpolation order [one of 1, 2, 3, 4, 5]
        **kwargs: all other args from :class:`lisagwresponse.ResponseFromStrain`
    """

    #: float: Left and right time interpolation margin for strain time series [s].
    MARGIN = 1.2 * au / c

    @classmethod
    def t0_with_margin(cls, t0):
        """Return initial time for strain time series with margin.

        :class:`lisagwresponse.ResponseFromStrain` needs to interpolation the
        strain time series at most ``1 au / c`` before and after the first
        and last simulation times. We take a 1.2 left and right margin.

        Args:
            t0 (float): initial time [s]

        Returns:
            float: Initial time for strain time series including margin for interpolation [s].
        """
        return t0 - cls.MARGIN

    @classmethod
    def size_with_margin(cls, size, dt):
        """Return total size for strain time series with margin for interpolation.

        :class:`lisagwresponse.ResponseFromStrain` needs to interpolation the
        strain time series at most ``1 au / c`` before and after the first
        and last simulation times. We take a 1.2 left and right margin.

        Args:
            size (int): simulation size [samples]
            dt (float): sampling period [s]

        Returns:
            int: Total size for strain time series with margin for interpolation [samples].
        """
        return size + 2 * int(cls.MARGIN // dt)

    def __init__(self, generator=None, hplus=None, hcross=None, strain_interp_order=5, **kwargs):
        super().__init__(**kwargs)
        self.strain_interp_order = int(strain_interp_order) #: int: ResponseFromStrain interpolation order.

        # ResponseFromStrain needs to be interpolated at most 1 au / c before
        # and after; we take 120% left and right margins
        size_with_margin = self.size_with_margin(self.size, self.dt)
        t = self.t0_with_margin(self.t0) + np.arange(size_with_margin) * self.dt

        if hplus is not None and hcross is not None:
            logger.info("Using user-provided strain time series")
            if hplus.shape != (size_with_margin,):
                raise TypeError(f"incorrect shape '{hplus.shape}' for hplus, "
                                f"must be '{(size_with_margin,)}'")
            if hcross.shape != (size_with_margin,):
                raise TypeError(f"incorrect shape '{hcross.shape}' for hcross, "
                                f"must be '{(size_with_margin,)}'")
            self.generator = None
            self._hplus = hplus
            self._hcross = hcross
        elif hplus is not None or hcross is not None:
            raise ValueError("provide both 'hplus' and 'hcross', or set both to None")
        elif callable(generator):
            logger.info("Using user-provided stochastic generator")
            self.generator = generator
            self._hplus = None
            self._hcross = None
        else:
            raise TypeError(f"invalid generator '{generator}', must be a callable")

        # Generate stochastic strain
        if self._hplus is None:
            logger.debug("Generating stochastic +-polarized strain time series")
            self._hplus = self.generator(self.fs, size_with_margin)
        if self._hcross is None:
            logger.debug("Generating stochastic x-polarized strain time series")
            self._hcross = self.generator(self.fs, size_with_margin)

        # Interpolate stochastic strain
        logger.debug("Interpolating stochastic strain time series")
        self.hplus = InterpolatedUnivariateSpline(
            t, self._hplus, k=self.strain_interp_order, ext='raise')
        """+-polarized strain :math:`h_+` interpolating function."""
        self.hcross = InterpolatedUnivariateSpline(
            t, self._hcross, k=self.strain_interp_order, ext='raise')
        """x-polarized strain :math:`h_\times` interpolating function."""

    def _write_metadata(self, hdf5, prefix=''):
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, 'strain_interp_order')

    def compute_hplus(self, t):
        try:
            return self.hplus(t)
        except ValueError as error:
            logger.error("Missing stochastic strain (hplus) to interpolate at\n%s", t)
            raise ValueError("missing stochastic strain data (hplus) to interpolate") from error

    def compute_hcross(self, t):
        try:
            return self.hcross(t)
        except ValueError as error:
            logger.error("Missing stochastic strain (hcross) to interpolate at\n%s", t)
            raise ValueError("missing stochastic strain data (hcross) to interpolate") from error


class StochasticBackground(Response):
    """Represent a whole-sky gravitational-wave stochastic background.

    The background is generated from a healpix-generated intensity sky map and a
    power spectral density. Each pixel in the sky is represented by a
    :class:`lisagwresponse.StochasticPointSource` instance, whose power is the product of
    the background PSD and the pixel intensity on the map.

    The response of each link is the superposition of the responses to each of the pixels
    (i.e., the stochastic point sources) making up the sky. Note that using a greater number
    of pixels increases the precision of the response but also the computational cost.

    .. admonition:: Memory usage

        Stochastic point sources for each pixel are created when initializating a stochastic
        background object, which triggers the generation of the random strain time series for
        the entire sky. For long simulations, we recommend you use ``optim=True`` to keep the
        memory usage to a minimum; point sources will not be created until you call
        :meth:`lisagwresponse.StochasticBackground.point_source`.

        Note that you will be limited to a single call to
        :meth:`lisagwresponse.StochasticBackground.compute_gw_response` in this case.

    Args:
        skymap: intensity sky map (from healpix)
        generator (callable):
            function ``(float, int) -> float`` of the sampling frequency [Hz]
            and size [samples] to generate strain time series
        optim (bool):
            optimize for memory usage (release pixel point sources computing response).
        **kwargs: all other args from :class:`lisagwresponse.Response`
    """

    def __init__(self, skymap, generator, optim=False, **kwargs):
        super().__init__(**kwargs)

        self.skymap = np.asarray(skymap)
        self.generator = generator
        self.npix = len(skymap) #: Number of sky pixels. Equivalently number of point sources.
        self.nside = healpy.npix2nside(self.npix) #: Healpix ``nside``.
        logger.info("Using a resolution of %s pixels (nside=%s)", self.npix, self.nside)

        self.optim = bool(optim) #: Whether memory optimization is enabled.
        if not self.optim:
            logger.info("Memory optimization disabled, building point sources")
            self.sources = []
            x, y, z, ltt = None, None, None, None
            for pixel in range(self.npix):
                source = self.point_source(pixel, x, y, z, ltt)
                if source is not None:
                    x, y, z, ltt = source.x, source.y, source.z, source.ltt
                    self.sources.append(source)
        else:
            logger.info("Memory optimization enabled, will generate point source on the fly")
            self.sources = None
            # Track if we call `compute_gw_response()` multiple times to issue a warning
            self.called_once = False

    def _write_metadata(self, hdf5, prefix=''):
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, 'skymap', 'npix', 'nside', 'optim')

    def compute_gw_response(self, t, link):
        """Compute link response to stochastic background.

        The response is computed as the sum of each pixel's response, see
        :meth:`lisagwresponse.StochasticPointSource.compute_gw_response`.

        .. warning:: Memory optimization

            If memory optimization is enabled (see :attr:`lisagwresponse.StochasticBackground.optim`),
            each call to this function will return a new stochastic point source with new
            strain time series, even for the same pixel.

            You will get inconsistent results (simulate a different sky) if you call this method
            multiple times.

        Args:
            t ((N,) or (N, M) array-like): TCB times [s]
            link ((M,) array-like): link indices

        Returns:
            (N, M) ndarray: Link responses [strain or relative frequency shifts]
        """
        gw_response = 0
        if not self.optim:
            # Simply iterate over sources, and sum responses
            for source in self.sources:
                gw_response += source.compute_gw_response(t, link) # (N, M)
        else:
            # We use memory optimization, i.e., will destroy each source after it's been used
            # Check that we haven't called `compute_gw_response()` before
            if self.called_once:
                logger.warning("Multiple calls to `compute_gw_response()` when memory optimization "
                               "is enabled may lead to inconsistent results")
            else:
                self.called_once = True

            x, y, z, ltt = None, None, None, None
            # Loop over pixels and add contributions
            for pixel in range(self.npix):
                source = self.point_source(pixel, x, y, z, ltt)
                if source is not None:
                    gw_response += source.compute_gw_response(t, link) # (N, M)
                    # We rely on the first pixel to interpolate the orbits,
                    # and reuse this interpolation for all remaining pixels
                    x, y, z, ltt = source.x, source.y, source.z, source.ltt
                    del source
        # Return sum of pixel's response
        return gw_response # (N, M)

    def point_source(self, pixel, x=None, y=None, z=None, ltt=None):
        """Return stochastic point source corresponding to the desired pixel.

        The spectrum of the pixel is computed as the product of the sky modulation `skymap` at
        this pixel, and the stochastic background spectrum `generator`.

        .. warning:: Memory optimization

            If memory optimization is enabled (see :attr:`lisagwresponse.StochasticBackground.optim`),
            each call to this function will return a new stochastic point source with new
            strain time series, even for the same pixel.

            You will get inconsistent results (simulate a different sky) if you call this method
            multiple times.

        Args:
            pixel (int): pixel index
            x (callable): spacecraft x-position interpolating functions, overrides orbits [m]
            y (callable): spacecraft y-position interpolating functions, overrides orbits [m]
            z (callable): spacecraft z-position interpolating functions, overrides orbits [m]
            ltt (callable): light travel times interpolating functions, overrides orbits [s]
        """
        if pixel not in range(self.npix):
            raise ValueError(f"pixel '{pixel}' out of range")

        # Bypass black pixel
        if not self.skymap[pixel]:
            logger.info("Bypassing black pixel %s", pixel)
            return None

        logger.info("Initializing stochastic point source for pixel %s", pixel)

        # Theta and phi are colatitude and longitude, respectively (healpy conventions)
        # They are converted to beta and lambda, latitude and longitude (LDC conventions)
        gw_theta, gw_phi= healpy.pix2ang(self.nside, pixel)
        gw_beta, gw_lambda = pi / 2 - gw_theta, gw_phi

        # Compute the generator for the pixel
        pixel_generator = lambda fs, size: self.skymap[pixel] * self.generator(fs, size) / self.npix

        return StochasticPointSource(
            generator=pixel_generator,
            gw_lambda=gw_lambda, gw_beta=gw_beta,
            orbits=self.orbits_path, orbit_interp_order=self.orbit_interp_order,
            x=x, y=y, z=z, ltt=ltt,
            dt=self.dt, size=self.size, t0=self.t0)

    def plot(self, t, output=None, gw_name='stochastic gravitational-wave background'):
        """Plot gravitational-wave response and intensity sky map.

        Args:
            t (array-like): TCB times [s]
            output (str or None): output file, None to show the plots
            gw_name (str): optional gravitational-wave source name
        """
        # Initialize the plot
        _, axes = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [1, 1.5]})
        axes[0].set_xlabel("Time [s]")
        axes[0].set_title(f"Power sky map and link response to {gw_name}")
        # Computing and plotting response
        logger.info("Plotting gravitational-wave response")
        axes[0].set_ylabel("Link response")
        response = self.compute_gw_response(t, self.LINKS) # (N, M)
        for link_index, link in enumerate(self.LINKS):
            axes[0].plot(t, response[:, link_index], label=link)
        axes[0].legend()
        axes[0].grid()
        # Plotting sky map
        plt.axes(axes[1])
        logger.info("Plotting sky map of power spectral density")
        healpy.mollview(self.skymap, hold=True, title=None, unit='Power spectral density at 1 Hz')
        # Save or show glitch
        if output is not None:
            logger.info("Saving plot to %s", output)
            plt.savefig(output, bbox_inches='tight')
        else:
            plt.show()
