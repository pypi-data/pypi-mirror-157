"""Particle movement integrators, for particle simulations.

These do not have `astropy.units` support, choosing instead to
limit overhead and increase performance.

They act in-place on position and velocity arrays to reduce
memory allocation.
"""
import numpy as np


def boris_push(x, v, B, E, q, m, dt):
    r"""
    The explicit Boris pusher.

    Parameters
    ----------
    x : `~numpy.ndarray`
        Particle position at full timestep, in SI (meter) units.

    v : `~numpy.ndarray`
        Particle velocity at half timestep, in SI (meter/second) units.

    B : `~numpy.ndarray`
        Magnetic field at full timestep, in SI (tesla) units.

    E : `float`
        Electric field at full timestep, in SI (V/m) units.

    q : `float`
        Particle charge, in SI (coulomb) units.

    m : `float`
        Particle mass, in SI (kg) units.

    dt : `float`
        Timestep, in SI (second) units.

    Notes
    ----------
    The Boris algorithm :cite:p:`boris:1970` is the standard energy
    conserving algorithm for particle movement in plasma physics. See
    :cite:t:`birdsall:2004` for more details, and this `page on the
    Boris method <https://www.particleincell.com/2011/vxb-rotation>`__
    for a nice overview.

    Conceptually, the algorithm has three phases:

    1. Add half the impulse from electric field.
    2. Rotate the particle velocity about the direction of the magnetic
       field.
    3. Add the second half of the impulse from the electric field.

    This ends up causing the magnetic field action to be properly "centered" in
    time, and the algorithm, being a symplectic integrator, conserves energy.
    """
    hqmdt = 0.5 * dt * q / m
    vminus = v + hqmdt * E

    # rotate to add magnetic field
    t = B * hqmdt
    s = 2 * t / (1 + (t * t).sum(axis=1, keepdims=True))
    vprime = vminus + np.cross(vminus, t)
    vplus = vminus + np.cross(vprime, s)

    # add second half of electric impulse
    v[...] = vplus + hqmdt * E

    x += v * dt
