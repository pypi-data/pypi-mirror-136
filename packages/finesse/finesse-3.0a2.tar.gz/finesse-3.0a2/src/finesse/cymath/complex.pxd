cimport numpy as np

cdef extern from "complex.h" nogil:
    double cabs(double complex z)
    double carg(double complex z)
    double complex cexp(double complex z)
    double cimag(double complex z)
    double creal(double complex z)
    double complex csqrt(double complex z)
    double complex conj(double complex z)

cdef extern from "math.h" nogil:
    double cos(double arg)
    double sin(double arg)

ctypedef np.complex128_t complex_t


"""Dense complex matrix, contiguous in memory"""
cdef struct DenseZMatrix:
    complex_t *ptr
    Py_ssize_t stride1 # in units of 16 bytes
    Py_ssize_t stride2 # in units of 16 bytes
    Py_ssize_t size1
    Py_ssize_t size2


"""Dense complex vector, contiguous in memory"""
cdef struct DenseZVector:
    complex_t *ptr
    Py_ssize_t stride # in units of 16 bytes
    Py_ssize_t size


cpdef inline double cnorm(complex_t z) nogil:
    return creal(z) * creal(z) + cimag(z) * cimag(z)


cpdef bint ceq(complex_t z1, complex_t z2) nogil


cpdef inline complex_t inverse_unsafe(complex_t z) nogil:
    cdef double inv_abs_sqd_z = 1.0 / cnorm(z)
    return creal(z) * inv_abs_sqd_z - 1.0j * cimag(z) * inv_abs_sqd_z


cpdef complex_t cpow_re(complex_t z, double n) nogil


cpdef inline complex_t crotate(complex_t z, double ph) nogil:
    cdef:
        double cph = cos(ph)
        double sph = sin(ph)

    return crotate2(z, cph, sph)

cpdef inline complex_t crotate2(complex_t z, double cph, double sph) nogil:
    cdef:
        double zre = creal(z)
        double zim = cimag(z)

    return zre * cph - zim * sph + 1j * (zre * sph + zim * cph)


# TODO (sjr) Move to new finesse.cymath.linalg file and use
#            fused types to make it like a template function
cpdef void couter(complex_t[::1] x, complex_t[::1] y, complex_t[:, ::1] out) nogil
