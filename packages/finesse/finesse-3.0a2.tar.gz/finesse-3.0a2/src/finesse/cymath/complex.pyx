#cython: boundscheck=False, wraparound=False, initializedcheck=False

"""Functions operating on complex numbers of type ``double complex``.

This module provides complex number functions as well as the fundamental
complex data type to be used by developers.

.. note::

    For any developer writing a Cython extension which involves complex
    mathematics, you should ``cimport`` the complex data type, which is used
    consistently across the code-base, via::

        from finesse.cymath cimport complex_t

    or::

        from finesse.cymath.complex cimport complex_t

    Both statements are equivalent. This ``complex_t`` typedef corresponds
    exactly to NumPy's ``np.complex128_t`` --- i.e. ``double complex``.

Most of the standard functions of the C ``"complex.h"`` header are exposed
at a C level via this module. Refer to the `Complex Number Arithmetic C reference
<https://en.cppreference.com/w/c/numeric/complex>`_ for the names, arguments
and further details on these functions. One can ``cimport`` such functions
in the same way as cimporting any other C exposed Cython function. For example::

    from finesse.cymath.complex cimport cexp

will ``cimport`` the `cexp <https://en.cppreference.com/w/c/numeric/complex/cexp>`_
function for use on ``complex_t`` data types in another Cython extension.
"""

cdef extern from "complex.h" nogil:
    double complex cexp(double complex z)
    double complex clog(double complex z)
    double cimag(double complex z)
    double creal(double complex z)

cdef extern from "math.h" nogil:
    double fabs(double arg)
    double fmax(double x, double y)

cdef extern from "constants.h":
    double complex COMPLEX_0 # 0 + 0i
    double complex COMPLEX_1 # 1 + 0i

cpdef bint ceq(complex_t z1, complex_t z2) nogil:
    cdef:
        double maximum
        int re = 0
        int im = 0

    maximum = fmax(
        fmax(fabs(creal(z1)), fabs(creal(z2))),
        fmax(fabs(cimag(z1)), fabs(cimag(z2)))
    )

    if maximum < 1e-13: return True

    # Clip denominator at 1 to avoid amplification of
    # difference for small complex number equality checks
    # NOTE (sjr) Leaving a note here just in case this causes issues in
    #            the future, see Issue #252 for reason for this change
    maximum = fmax(maximum, 1.0)

    if creal(z1) == 0.0 and creal(z2) == 0.0:
        re = 1
    else:
        re = fabs(creal(z1) - creal(z2)) / maximum < 1e-13

    if cimag(z1) == 0.0 and cimag(z2) == 0.0:
        im = 1
    else:
        im = fabs(cimag(z1) - cimag(z2)) / maximum < 1e-13

    return re & im


cpdef complex_t cpow_re(complex_t z, double n) nogil:
    if n == 0.0:
        return COMPLEX_1

    if z == COMPLEX_0:
        return COMPLEX_0

    if n == 1.0:
        return z

    return cexp(n * clog(z))


cpdef void couter(complex_t[::1] x, complex_t[::1] y, complex_t[:, ::1] out) nogil:
    cdef:
        Py_ssize_t i, j
        Py_ssize_t N = x.shape[0]
        Py_ssize_t M = y.shape[0]

    for i in range(N):
        for j in range(M):
            out[i][j] = x[i] * y[j]
