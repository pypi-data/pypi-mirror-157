#!/bin/python
# -*- coding: utf-8 -*-

import os
import jax
import time
import jax.numpy as jnp
import scipy.sparse as ssp
from grgrlib.jaxed import newton_jax, jacfwd_and_val, jacrev_and_val
from .shooting import find_path_linear
from .parser.build_functions import *


def find_stack(
    model,
    x0=None,
    shock=None,
    init_path=None,
    horizon=250,
    tol=None,
    maxit=None,
    use_linear_guess=True,
    use_linear_endpoint=None,
    use_jacrev=True,
    verbose=True,
    **solver_kwargs,
):
    """Find the expected trajectory given an initial state.

    Parameters
    ----------
    model : dict
        model dict or PizzaModel instance
    x0 : array
        initial state
    shock : tuple, optional
        shock in period 0 as in `(shock_name_as_str, shock_size)`
    init_path : array, optional
        a first guess on the trajectory. Should not be necessary
    horizon : int, optional
        number of periods until the system is assumed to be back in the steady state. A good idea to set this corresponding to the respective problem. A too large value may be computationally expensive. A too small value may generate inaccurate results
    tol : float, optional
        convergence criterion. Defaults to 1e-8
    maxit : int, optional
        number of iterations. Default is 30.
    use_linear_guess : bool, optional
        whether to use the linear impulse responses as an initial guess. Defaults to True if the linear LOM is known
    use_linear_endpoint : bool, optional
        whether to use the linear impulse responses as the final state. Defaults to True if the linear LOM is known
    use_jacrev : bool, optional
        whether to use reverse mode or forward mode automatic differentiation. By construction, reverse AD is faster, but does not work for all types of functions. Defaults to True
    verbose : bool, optional
        degree of verbosity. 0/`False` is silent
    solver_kwargs : optional
        any additional keyword arguments will be passed on to the solver

    Returns
    -------
    x : array
        array of the trajectory
    x_lin : array or None
        array of the trajectory based on the linear model. Will return None if the linear model is unknown
    flag : bool
        returns True if the solver was successful, else False
    """

    st = time.time()

    stst = jnp.array(list(model["stst"].values()))
    nvars = len(model["variables"])
    pars = jnp.array(list(model["parameters"].values()))
    shocks = model.get("shocks") or ()
    # load functions
    func_eqns = model['context']["func_eqns"]
    func_backw = model['context'].get('func_backw')
    func_dist = model['context'].get('func_dist')

    tol = 1e-8 if tol is None else tol
    maxit = 30 if maxit is None else maxit

    x0 = jnp.array(list(x0)) if x0 is not None else stst
    x = jnp.ones((horizon + 1, nvars)) * stst
    x = x.at[0].set(x0)

    x_init, x_lin = find_path_linear(
        model, shock, horizon, x, use_linear_guess)

    if use_linear_endpoint is None:
        use_linear_endpoint = False if x_lin is None else True
    elif use_linear_endpoint and x_lin is None:
        print("(find_path_stacked:) Linear solution for the endpoint not available")
        use_linear_endpoint = False

    if init_path is not None:
        x_init[1: len(init_path)] = init_path[1:]

    zshock = jnp.zeros(len(shocks))
    tshock = jnp.copy(zshock)
    if shock is not None:
        tshock = tshock.at[shocks.index(shock[0])].set(shock[1])
        if model.get('distributions'):
            print("(find_path_stacked:) Warning: shocks for heterogenous agent models are not yet fully supported. Use adjusted steady state values as x0 instead.")

    endpoint = x_lin[-1] if use_linear_endpoint else stst

    if model.get('distributions'):
        vfSS = model['steady_state']['decisions']
        distSS = jnp.array(model['steady_state']['distributions'])
        decisions_output_init = model['init_run'].get('decisions_output')

        # get values of func_eqns that are independent of the distribution
        stst_in_t = stst[:, jnp.newaxis]

        def func_eqns_from_dist(dist, decisions_output): return func_eqns(
            stst_in_t, stst_in_t, stst_in_t, stst, zshock, pars, dist[..., jnp.newaxis], decisions_output[..., jnp.newaxis])

        _, mask_out_jvp = jax.jvp(func_eqns_from_dist, (distSS, decisions_output_init), (
            jnp.ones_like(distSS), jnp.ones_like(decisions_output_init)))
        mask_out = jnp.repeat(mask_out_jvp.astype(bool), horizon-1)

        # compile dist-specific functions
        stacked_func_dist_raw = get_stacked_func_dist(pars, func_backw, func_dist, func_eqns, x0, stst,
                                                      vfSS, distSS, zshock, tshock, horizon, nvars, endpoint, model.get('distributions'), shock)
        stacked_func_dist = jax.jit(
            stacked_func_dist_raw, static_argnames='full_output')
        model['context']['stacked_func_dist'] = stacked_func_dist
        dist_dummy = distSS[..., jnp.newaxis]
        decisions_output_dummy = decisions_output_init[..., jnp.newaxis]
    else:
        dist_dummy = decisions_output_dummy = []

    stacked_func = get_stacked_func(pars, func_eqns, stst, x0, horizon, nvars,
                                    endpoint, zshock, tshock, shock, dist_dummy, decisions_output_dummy)

    if verbose:
        print("(find_path_stacked:) Solving stack (size: %s)..." %
              (horizon*nvars))

    if model.get('distributions'):
        stacked_func = combine_stacked_funcs(
            stacked_func_dist, stacked_func, mask_out, use_jacrev)
    res = newton_jax(stacked_func, x_init[1:-1].flatten(), None, maxit, tol,
                     sparse=True, func_returns_jac=True, verbose=verbose, **solver_kwargs)

    # calculate error
    err = jnp.abs(res['fun']).max()
    x = x.at[1:-1].set(res['x'].reshape((horizon - 1, nvars)))

    mess = res['message']

    if err > tol or not res['success']:
        mess += f" Max. error is {err:1.2e}."
        verbose = True

    if verbose:
        duration = time.time() - st
        sucess = 'done' if res['success'] else 'FAILED'
        print(
            f"(find_path_stacked:) Stacking {sucess} after {duration:1.3f} seconds. " + mess)

    return x, x_lin, not res['success']
