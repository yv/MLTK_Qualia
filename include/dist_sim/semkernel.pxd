from dist_sim.sparsmat cimport CSRMatrixD, SparseVectorD
cimport alphabet
import alphabet
from python_list cimport PyList_Append, PyList_GET_SIZE
from python_mem cimport PyMem_Malloc, PyMem_Free

cdef extern from "math.h":
    double sqrt(double x)

cdef class Kernel:
    cpdef double kernel(self, int i, int j)

cdef class PolynomialKernel(Kernel):
    cdef CSRMatrixD matrix
    cdef double c
    cdef int d
    cdef object norm_vals
    cdef int last_i, last_j
    cdef double last_val

cdef class JSDKernel(Kernel):
    cdef CSRMatrixD matrix
    cdef object norm_vals
    cdef int last_i, last_j
    cdef double last_val

cdef class MinKernel(Kernel):
    cdef CSRMatrixD matrix
    cdef object norm_vals
    cdef int last_i, last_j
    cdef double last_val

cdef class KPolynomial(Kernel):
    cdef public object kernels
    cdef object poly
    cpdef double kernel(self, int i, int j)
