from dist_sim.sparsmat cimport SparseVectorD
from python cimport *

cdef extern from "lbfgs.h":
    # return codes
    int LBFGS_SUCCESS
    int LBFGS_CONVERGENCE
    int LBFGS_STOP
    # line search algorithms
    int LBFGS_LINESEARCH_MORETHUENTE
    int LBFGS_LINESEARCH_BACKTRACKING_ARMIJO
    int LBFGS_LINESEARCH_BACKTRACKING
    int LBFGS_LINESEARCH_BACKTRACKING_WOLFE
    int LBFGS_LINESEARCH_BACKTRACKING_STRONG_WOLFE
    ctypedef double lbfgsfloatval_t
    ctypedef double const_lbfgsfloatval_t "const lbfgsfloatval_t"
    struct _lbfgs_parameter_t:
        int m
        lbfgsfloatval_t epsilon
        lbfgsfloatval_t delta
        int max_iterations
        int linesearch
        int max_linesearch
        lbfgsfloatval_t min_step
        lbfgsfloatval_t max_step
        lbfgsfloatval_t ftol
        lbfgsfloatval_t wolfe
        lbfgsfloatval_t gtol
        lbfgsfloatval_t xtol
        lbfgsfloatval_t orthantwise_c
        int orthantwise_start
        int orthantwise_end
    ctypedef _lbfgs_parameter_t lbfgs_parameter_t
    ctypedef lbfgsfloatval_t (*lbfgs_evaluate_t)(
        void *instance,
        const_lbfgsfloatval_t *x,
        lbfgsfloatval_t *g,
        int n,
        const_lbfgsfloatval_t step) except 0.0
    ctypedef int (*lbfgs_progress_t)(
        void *instance,
        const_lbfgsfloatval_t *x,
        const_lbfgsfloatval_t *g,
        const_lbfgsfloatval_t fx,
        const_lbfgsfloatval_t xnorm,
        const_lbfgsfloatval_t gnorm,
        const_lbfgsfloatval_t step,
        int n,
        int k,
        int ls)
    int lbfgs(int n,
              lbfgsfloatval_t *x,
              lbfgsfloatval_t *ptr_fx,
              lbfgs_evaluate_t proc_evaluate,
              lbfgs_progress_t proc_progress,
              void *instance,
              lbfgs_parameter_t *param)
    void lbfgs_parameter_init(lbfgs_parameter_t *param)
    lbfgsfloatval_t* lbfgs_malloc(int n)
    void lbfgs_free(lbfgsfloatval_t *x)
    ctypedef double const_double "const double"

cdef extern from "math.h":
    double log(double)
    double log1p(double)
    double exp(double)
    double fabs(double)

cdef extern from "Python.h":
    PyObject *PyErr_Occurred()
    ctypedef int size_t
    void *PyMem_Malloc(size_t)
    void *PyMem_Realloc(void *,size_t)
    void PyMem_Free(void *)

cdef class Document:
    cdef object vecs
    cdef double *weights
    cdef int *offsets
    cdef int n_alloc
    cdef int n_filled
    cpdef bint clear(self)
    cpdef bint addVector(self, SparseVectorD vec, double weight=*, int offset=*)
    cdef void _axpy(self, double *w, double weight=*, int offset_size=*)

ctypedef double gradient_func(object, const_double *, double, Document)
