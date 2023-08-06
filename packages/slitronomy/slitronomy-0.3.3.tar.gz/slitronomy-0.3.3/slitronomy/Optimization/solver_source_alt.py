__author__ = 'aymgal'

# class that implements SLIT algorithm

import copy
import numpy as np
import math as ma

from slitronomy.Optimization.solver_base import SparseSolverBase
from slitronomy.Optimization import algorithms
from slitronomy.Util import util


class SparseSolverSourceAlt(SparseSolverBase):

    """Implements an improved version of the original SLIT algorithm (https://github.com/herjy/SLIT)"""

    def __init__(self, data_class, image_numerics_class, source_numerics_class, 
                 source_model_class, lens_model_class,
                 num_iter_source=10, num_iter_weights=3, **base_kwargs):
        """
        :param data_class: lenstronomy.imaging_data.ImageData instance describing the data.
        :param lens_model_class: lenstronomy.lens_model.LensModel instance describing the lens mass model.
        :param image_numerics_class: lenstronomy.ImSim.Numerics.numerics_subframe.NumericsSubFrame instance for image plane.
        :param source_numerics_class: lenstronomy.ImSim.Numerics.numerics_subframe.NumericsSubFrame instance for source plane.        :param source_model_class: lenstronomy.light_model.LightModel instance describing the source light.
        :param num_iter_source: number of iterations for sparse optimization of the source light. 
        :param num_iter_lens: number of iterations for sparse optimization of the lens light. 
        :param num_iter_weights: number of iterations for l1-norm re-weighting scheme.
        :param base_kwargs: keyword arguments for SparseSolverBase.

        If not set or set to None, 'threshold_decrease_type' in base_kwargs defaults to 'exponential'.
        """
        # remove settings not related to this solver
        # _ = base_kwargs.pop('num_iter_lens', None)
        # _ = base_kwargs.pop('num_iter_global', None)

        super(SparseSolverSourceAlt, self).__init__(data_class, image_numerics_class, source_numerics_class,
                                                 lens_model_class=lens_model_class, **base_kwargs)

        # define default threshold decrease strategy
        if 'threshold_decrease_type' not in base_kwargs:
            self._threshold_decrease_type = 'exponential'

        self.add_source_light(source_model_class)
        self._n_iter_source = num_iter_source
        if self._sparsity_prior_norm == 1:
            self._n_iter_weights = num_iter_weights
        else:
            self._n_iter_weights = 1   # reweighting scheme only defined for l1-norm sparsity

    def _ready(self):
        return not self.no_source_light

    def _solve(self, kwargs_lens=None, kwargs_ps=None, kwargs_special=None):
        """
        implements the SLIT algorithm
        """
        # set the gradient step: 0 < mu < 2/spectral_norm
        mu = 1. / self.spectral_norm_source

        # get the gradient of the cost function, which is f = || Y - HFS ||^2_2
        grad_f = lambda x : self.gradient_loss_source(x)

        # initial guess as background random noise
        S, alpha_S = self.generate_initial_source()
        if self._show_steps:
            self._plotter.plot_init(S)

        # initialise weights
        weights = 1.

        # initialise tracker
        self._tracker.init()

        ######### Loop to update weights ########
        loss_list = []
        red_chi2_list = []
        step_diff_list = []
        for j in range(self._n_iter_weights):

            # estimate initial threshold
            thresh_init = self._estimate_threshold_source(self.Y_eff)
            thresh = thresh_init

            # initial hidden variables
            if j == 0 and self.algorithm == 'FISTA':
                fista_xi = np.copy(alpha_S)
                fista_t  = 1.

            ######### Loop over iterations at fixed weights ########
            for i in range(self._n_iter_source):

                # get the proximal operator with current weights, convention is that it takes 2 arguments
                prox_g = lambda x, y: self.proximal_sparsity_source_alt(x, threshold=thresh, weights=weights)

                if self.algorithm == 'FB':
                    S_next = algorithms.step_FB(S, grad_f, prox_g, mu)
                    alpha_S_next = self.Phi_T_s(S_next)

                elif self.algorithm == 'FISTA':
                    alpha_S_next, fista_xi_next, fista_t_next \
                        = algorithms.step_FISTA(alpha_S, fista_xi, fista_t, grad_f, prox_g, mu)
                    S_next = self.Phi_s(alpha_S_next)

                # save current step to track
                self._tracker.save(S=S, S_next=S_next, print_bool=(i % 10 == 0),
                                   iteration_text="=== iteration {:03}-{:03} ===".format(j, i))

                if self._show_steps and (i % ma.ceil(self._n_iter_source/2) == 0):
                    self._plotter.plot_step(S_next, iter_1=j, iter_2=i)

                # update current estimate of source light and local parameters
                S = S_next
                alpha_S = alpha_S_next
                if self.algorithm == 'FISTA':
                    fista_xi, fista_t = fista_xi_next, fista_t_next

                # update adaptive threshold
                thresh = self._update_threshold(thresh, thresh_init, self._n_iter_source)

            # update weights if necessary
            if self._n_iter_weights > 1:
                weights, _ = self._update_weights(alpha_S, threshold=self._k_min)

        # reset data to original data
        self.reset_partial_data()

        # store results
        self._tracker.finalize()
        self._source_model = S

        # all optimized coefficients (flattened)
        alpha_S_final = self.Phi_T_s(self.project_on_original_grid_source(S))
        coeffs_S_1d = util.cube2array(alpha_S_final)

        if self._show_steps:
            self._plotter.plot_final(self._source_model)

        model = self.image_model(unconvolved=False)
        return model, coeffs_S_1d, [], []

    def proximal_sparsity_source_alt(self, array_S, threshold, weights):
        from slitronomy.Optimization import proximals
        array_HFS = self.H(self.F(array_S))
        noise_levels_HFS = self.get_source_levels_in_image_plane(len(array_HFS), self.Phi_T_s)
        array_proxed_HFS =  proximals.full_prox_sparsity_positivity(array_HFS, self.Phi_T_s, self.Phi_s, 
                                                                weights, noise_levels_HFS, 
                                                                threshold, self._increm_high_freq,
                                                                self._n_scales_source, self._sparsity_prior_norm,
                                                                self._formulation, self._force_positivity)
        array_proxed = self.F_T(self.H_T(array_proxed_HFS))
        
        # then we set to 0 every pixel that is outside the 'support' in source plane
        array_proxed = self.apply_source_plane_mask(array_proxed)
        return array_proxed

    def get_source_levels_in_image_plane(self, num_pix_image, wavelet_transform):
        # starlet transform of a dirac impulse in image plane
        dirac = util.dirac_impulse(num_pix_image)
        dirac_coeffs2 = wavelet_transform(dirac)**2

        # TODO: if it happens that noise_map is a constant value, not need to initialise a full array
        noise_map = self.noise.effective_noise_map  #self.noise_map

        n_scale, n_pix1, npix2 = dirac_coeffs2.shape
        noise_levels = np.zeros((n_scale, n_pix1, npix2))
        for scale_idx in range(n_scale):
            scale_power2 = np.sum(dirac_coeffs2[scale_idx, :, :])
            noise_levels[scale_idx, :, :] = noise_map * np.sqrt(scale_power2)

        return noise_levels
