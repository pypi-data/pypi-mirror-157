#define PY_SSIZE_T_CLEAN
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <Python.h>
#include <stdbool.h>
#define MIN(a,b) (((a)<=(b))?(a):(b))

static long acp_type(long b, long N, long sign){
    /* Categorize the logical relationship of an inequality given by b, N and sign as
    sign * x_1 + sign * x_2 + ... + sign * x_N >= b */
    if (sign > 0) // Require atleast b
        if (b > N) // Always false, not possible to satisfy the inequality
            return -1;
        else if (b==0) // Always true
            return 0;
        else if (b==1) // Atleast 1 <=> Any
            return 1;
        else if (N-b==0) // Atleast N <=> All
            return 4;
        else
            return 5; // Atleast n
    else // require atmost b
        if (b > 0)
            return -1; // Always false, not possible to satisfy the inequality
        else if (b <= -N)
            return 0; // Always true
        else if (b==0)
            return 3; // Atmost 0 <=> None
        else if (labs(b) == N-1)
            return 2; // Atmost all but one
        else
            return 6; // Atmost n

}

static long mcc_type(PyObject* constraint){ //constraint = ((indices),(constants),support, parent_index)
    PyObject* constants = PyTuple_GetItem(constraint, 2);
    long N = (long)PyTuple_Size(constants);
    long const1;
    if (N==-1){
        N = 1;
        const1 = PyLong_AsLong(constants);
    }
    else
        const1 = PyLong_AsLong(PyTuple_GetItem(constants, 0));
    if (const1 == 1 || const1 == -1){
        for (long i = 1; i < N; i++){
            if (const1 != PyLong_AsLong(PyTuple_GetItem(constants, i)))
            {
                return 7;
            }
        }
        return acp_type(PyLong_AsLong(PyTuple_GetItem(constraint, 3)), N, const1);
    }
    else {
        return 7;
    }
}

static PyObject* build_PyConstraintTuple(PyObject* var_type1, PyObject* indices1, long constant1, PyObject* var_type2, PyObject* indices2, long constant2, long b, PyObject* id){
    PyObject* constraint_tuple = PyTuple_New(5);
    long n1 = (long)PyTuple_Size(indices1);
    long n2 = (long)PyTuple_Size(indices2);
    PyObject* var_types = PyTuple_New(n1+n2);
    PyObject* indices = PyTuple_New(n1+n2);
    PyObject* values = PyTuple_New(n1+n2);
    for (long i = 0; i < n1; i++){
        PyTuple_SetItem(var_types, i, PyTuple_GetItem(var_type1, i));
        PyTuple_SetItem(indices, i, PyTuple_GetItem(indices1, i));
        PyTuple_SetItem(values, i, PyLong_FromLong(constant1));
    }
    for (long i=0; i < n2; i++){
        PyTuple_SetItem(var_types, n1+i, PyTuple_GetItem(var_type2, i));
        PyTuple_SetItem(indices, n1+i, PyTuple_GetItem(indices2, i));
        PyTuple_SetItem(values, n1+i, PyLong_FromLong(constant2));
    }
    PyTuple_SetItem(constraint_tuple, 0, var_types);
    PyTuple_SetItem(constraint_tuple, 1, indices);
    PyTuple_SetItem(constraint_tuple, 2, values);
    PyTuple_SetItem(constraint_tuple, 3, PyLong_FromLong(b));
    PyTuple_SetItem(constraint_tuple, 4, id);
    return constraint_tuple;
};

static PyObject* build_PyCompoundConstraints(long b, long sign, PyObject* constraint_list, PyObject* id){
    PyObject* result = PyTuple_New(4);
    PyTuple_SetItem(result, 0, PyLong_FromLong(b));
    PyTuple_SetItem(result, 1, PyLong_FromLong(sign));
    PyTuple_SetItem(result, 2, constraint_list);
    PyTuple_SetItem(result, 3, id);
    return result;
}

long lower_bound(PyObject* constraint){
    PyObject* constants = PyTuple_GetItem(constraint, 2);
    long b = PyLong_AsLong(PyTuple_GetItem(constraint, 3));
    long N = (long) PyTuple_Size(constants);
    long res = -b;
    for (int i = 0; i < N; i++){
        if (PyLong_AsLong(PyTuple_GetItem(constants, i)) < 0)
            res--;
    }
    return res;
}

static PyObject* compress_two_disjunctions(PyObject* constraint1, PyObject* constraint2, PyObject* id){
    /* Returns a Python Compound Constraint */
    PyObject* constraint1_const = PyTuple_GetItem(constraint1, 2);
    PyObject* constraint2_const = PyTuple_GetItem(constraint2, 2);
    long ctype1 = mcc_type(constraint1);
    long ctype2 = mcc_type(constraint2);
    long n1 = (long)PyTuple_Size(constraint1_const);
    long n2 = (long)PyTuple_Size(constraint2_const);

    if (ctype1 == -1 && ctype2 == -1){
            PyErr_SetString(PyExc_ValueError, "ERROR: Found contradicition");
            Py_RETURN_NONE;
    } else if (ctype1 == -1){
        PyObject* constraint_list = PyList_New(1);
        PyList_SetItem(constraint_list, 0, constraint2);
        return build_PyCompoundConstraints(1, 1, constraint_list, id);
    } else if (ctype2 == -1){
        PyObject* constraint_list = PyList_New(1);
        PyList_SetItem(constraint_list, 0, constraint1);
        return build_PyCompoundConstraints(1, 1, constraint_list, id);
    } else if (ctype1 == 0 || ctype2 == 0){
        /* Both constraints are redundant */
        PyObject* constraint_list = PyList_New(1);
        PyList_SetItem(constraint_list, 0, Py_None);
        return build_PyCompoundConstraints(0, 1, constraint_list, id);
    } else if (ctype1 > ctype2){
        return compress_two_disjunctions(constraint2, constraint1, id);
    } else if (ctype1 == 1){
        if (ctype2 == 1){
            PyObject* constraint_list = PyList_New(1);
            PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), 1, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, 1, id));
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        } else if (ctype2 == 2 ){
            PyObject* constraint_list = PyList_New(1);
            PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, 0, id));
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        } else if (ctype2 == 3 || ctype2 == 6){
            PyObject* constraint_list = PyList_New(1);
            PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0),PyTuple_GetItem(constraint1, 1),  n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        } else if (ctype2 == 4 || ctype2 == 5){
            PyObject* constraint_list = PyList_New(1);
            PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        } else {
            PyObject* constraint_list = PyList_New(2);
            PyList_SetItem(constraint_list, 0, constraint1);
            PyList_SetItem(constraint_list, 1, constraint2);
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        }
    } else if (ctype1 == 2){
        if (ctype2 == 2){
            PyObject* constraint_list = PyList_New(1);
            PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, -n2*(labs(PyLong_AsLong(PyTuple_GetItem(constraint1, 3)))+1)-labs(PyLong_AsLong(PyTuple_GetItem(constraint2, 3))), id));
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        } else if (ctype2 == 3){
                PyObject* constraint_list = PyList_New(1);
                PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -1, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -n1, -n1*n2, id));
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
        } else if (ctype2 == 4 || ctype2 == 5){
                PyObject* constraint_list = PyList_New(1);
                PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, -n2*(labs(PyLong_AsLong(PyTuple_GetItem(constraint1, 3)))+1)+PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
        } else if (ctype2 == 6){
            PyObject* constraint_list = PyList_New(1);
            PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, -n2*(labs(PyLong_AsLong(PyTuple_GetItem(constraint1, 3)))+1)+PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        } else {
            PyObject* constraint_list = PyList_New(2);
            PyList_SetItem(constraint_list, 0, constraint1);
            PyList_SetItem(constraint_list, 1, constraint2);
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        }
    } else if (ctype1 == 3 || ctype1 == 4){
        if (n1 == 1){
            if (ctype2 == 3){
                PyObject* constraint_list = PyList_New(1);
                PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, -n2, id));
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
            } else if (ctype2 == 4){
                PyObject* constraint_list = PyList_New(1);
                PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, 0, id));
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
            } else if (ctype2 == 5){
                PyObject* constraint_list = PyList_New(1);
                PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, -n2*PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
            } else if (ctype2 == 6){
                PyObject* constraint_list = PyList_New(1);
                PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, -n2+PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
            } else {
                PyObject* constraint_list = PyList_New(2);
                PyList_SetItem(constraint_list, 0, constraint1);
                PyList_SetItem(constraint_list, 1, constraint2);
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
            }
        } else if (n2 == 1 && (ctype2 == 3 || ctype2 == 4)){
            if (ctype1 == 3){
                PyObject* constraint_list = PyList_New(1);
                PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -1, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -n1, -n1, id));
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
            } else {
                // ctype1 == 4
                PyObject* constraint_list = PyList_New(1);
                PyList_SetItem(constraint_list, 0, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), 1, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -n1, 0, id));
                return build_PyCompoundConstraints(1, 1, constraint_list, id);
            }
        } else{
            PyObject* constraint_list = PyList_New(2);
            PyList_SetItem(constraint_list, 0, constraint1);
            PyList_SetItem(constraint_list, 1, constraint2);
            return build_PyCompoundConstraints(1, 1, constraint_list, id);
        }
    } else {
        PyObject* constraint_list = PyList_New(2);
        PyList_SetItem(constraint_list, 0, constraint1);
        PyList_SetItem(constraint_list, 1, constraint2);
        return build_PyCompoundConstraints(1, 1, constraint_list, id);
    }
}

static PyObject* compress_disjunctions(PyObject* constraints, PyObject* id){
    long N = (long) PyList_Size(constraints);
    PyObject * tmp;
    PyObject* res[N];
    long j = 0;
    PyObject* constraint1 = PyList_GetItem(constraints, 0);
    for (long i=1; i < N; i++){
        tmp = compress_two_disjunctions(constraint1, PyList_GetItem(constraints, i), id);
        if (PyList_Size(PyTuple_GetItem(tmp, 2)) < 2){
            constraint1 = PyList_GetItem(PyTuple_GetItem(tmp, 2), 0);
        } else{
            res[j] = constraint1;
            constraint1 = PyList_GetItem(constraints, i);
            j++;
        }
    }
    res[j] = constraint1;
    PyObject* result = PyList_New(j+1);
    for(int i=0; i <= j; i++){
        PyList_SetItem(result, i, res[i]);
    }
    return build_PyCompoundConstraints(1, 1, result, id);
}


PyObject* create_new_variable(long b, long sign, PyObject* constraints, PyObject* id){
    long N = (long) PyList_Size(constraints);
    long N_i;
    PyObject* constraint_list = PyList_New(N+1);
    PyObject* constraint_i;
    PyObject* main_constraint_var_types = PyTuple_New(N);
    PyObject* main_constraint_indices = PyTuple_New(N);
    PyObject* main_constraint_values = PyTuple_New(N);
    long m;
    for (long i=0; i < N; i++){
        constraint_i = PyList_GetItem(constraints, i);
        N_i = (long) PyTuple_Size(PyTuple_GetItem(constraint_i, 0));
        PyTuple_SetItem(main_constraint_var_types, i, PyLong_FromLong(0));
        PyTuple_SetItem(main_constraint_indices, i, PyTuple_GetItem(constraint_i, 4));
        PyTuple_SetItem(main_constraint_values, i, PyLong_FromLong(sign));
        m = lower_bound(constraint_i);
        PyObject* var_type_support_constraint = PyTuple_New(1+N_i);
        PyObject* ind_support_constraint = PyTuple_New(1+N_i);
        PyObject* val_support_constraint = PyTuple_New(1+N_i);
        for (int j=0; j < N_i; j++){
            PyTuple_SetItem(var_type_support_constraint, j, PyTuple_GetItem(PyTuple_GetItem(constraint_i, 0), j));
            PyTuple_SetItem(ind_support_constraint, j, PyTuple_GetItem(PyTuple_GetItem(constraint_i, 1), j));
            PyTuple_SetItem(val_support_constraint, j, PyTuple_GetItem(PyTuple_GetItem(constraint_i, 2), j));
        }
        PyTuple_SetItem(var_type_support_constraint, N_i, PyLong_FromLong(0));
        PyTuple_SetItem(ind_support_constraint, N_i, PyTuple_GetItem(constraint_i, 4));
        PyTuple_SetItem(val_support_constraint, N_i, PyLong_FromLong(m));
        PyObject* support_constraint_i = PyTuple_New(5);
        PyTuple_SetItem(support_constraint_i, 0, var_type_support_constraint);
        PyTuple_SetItem(support_constraint_i, 1, ind_support_constraint);
        PyTuple_SetItem(support_constraint_i, 2, val_support_constraint);
        PyTuple_SetItem(support_constraint_i, 3, PyLong_FromLong(m + PyLong_AsLong(PyTuple_GetItem(constraint_i, 3))));
        PyTuple_SetItem(support_constraint_i, 4, PyTuple_GetItem(constraint_i, 4));
        PyList_SetItem(constraint_list, i+1, support_constraint_i);
    }
    PyObject* main_constraint = PyTuple_New(5);
    PyTuple_SetItem(main_constraint, 0, main_constraint_var_types);
    PyTuple_SetItem(main_constraint, 1, main_constraint_indices);
    PyTuple_SetItem(main_constraint, 2, main_constraint_values);
    PyTuple_SetItem(main_constraint, 3, PyLong_FromLong(b));
    PyTuple_SetItem(main_constraint, 4, id);
    PyList_SetItem(constraint_list, 0, main_constraint);
    return build_PyCompoundConstraints(N+1, 1, constraint_list, id);
}

PyObject * transform_two_disjunctions(PyObject* constraint1, PyObject* constraint2, PyObject* id, bool allow_mc){
    PyObject* constraint1_const = PyTuple_GetItem(constraint1, 2);
    PyObject* constraint2_const = PyTuple_GetItem(constraint2, 2);
    int ctype1 = mcc_type(constraint1);
    int ctype2 = mcc_type(constraint2);
    int n1 = (int)PyTuple_Size(constraint1_const);
    int n2 = (int)PyTuple_Size(constraint2_const);

    if (ctype1 > ctype2)
        return transform_two_disjunctions(constraint2, constraint1, id, allow_mc);
    else if (ctype1 <= 2 || ctype2 <= 2)
        return compress_two_disjunctions(constraint1, constraint2, id);
    else if (ctype1 == 3 || ctype1 == 4){
        if (n1 == 1)
            return compress_two_disjunctions(constraint1, constraint2, id);
        else if (n2 == 1 && (ctype2 == 3 || ctype2 == 4))
            return compress_two_disjunctions(constraint1, constraint2, id);
        else if (allow_mc && ctype2 <= 4){
            PyObject* _var_type = PyTuple_New(1);
            PyObject* _index = PyTuple_New(1);
            if (n2 < n1){
                PyObject* constraint_list = PyList_New(n2);
                if (ctype2 == 3)
                    if(ctype1 == 3){
                        for (int i=0; i < n2; i++){
                            PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint2, 0), i));
                            PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint2, 1), i));
                            PyList_SetItem(constraint_list, i, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -1, _var_type, _index, -n1, -n1, id));
                        }
                    } else { //ctype1 == 4
                        for (int i=0; i < n2; i++){
                            PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint2, 0), i));
                            PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint2, 1), i));
                            PyList_SetItem(constraint_list, i, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), 1, _var_type, _index, -n1, 0, id));
                        }
                    }
                else // ctype2 == 4
                    if (ctype1 == 3){
                        for (int i=0; i < n2; i++){
                            PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint2, 0), i));
                            PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint2, 1), i));
                            PyList_SetItem(constraint_list, i, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), -1, _var_type, _index, n1, 0, id));
                        }
                    } else { // ctype1 == 4
                        for (int i=0; i < n2; i++){
                            PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint2, 0), i));
                            PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint2, 1), i));
                            PyList_SetItem(constraint_list, i, build_PyConstraintTuple(PyTuple_GetItem(constraint1, 0), PyTuple_GetItem(constraint1, 1), 1, _var_type, _index, n1, n1, id));
                        }
                    }

                return build_PyCompoundConstraints(n2, 1, constraint_list, id);
            } else {
                PyObject* constraint_list = PyList_New(n1);
                if (ctype1 == 3)
                    if (ctype2 == 3){
                        for (int i=0; i < n1; i++){
                            PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 0), i));
                            PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 1), i));
                            PyList_SetItem(constraint_list, i, build_PyConstraintTuple(_var_type, _index, -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, -n2, id));
                        }
                    } else { // ctype2 == 4
                        for (int i=0; i < n1; i++){
                            PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 0), i));
                            PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 1), i));
                            PyList_SetItem(constraint_list, i, build_PyConstraintTuple(_var_type, _index, -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, 0, id));
                        }
                    }
                else { // ctype1 == 4 and ctype2 == 4
                    for (int i=0; i < n1; i++){
                        PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 0), i));
                        PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 1), i));
                        PyList_SetItem(constraint_list, i, build_PyConstraintTuple(_var_type, _index, n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, n2, id));
                    }
                }
                return build_PyCompoundConstraints(n1, 1, constraint_list, id);
            }
        } else if (allow_mc){
            PyObject* constraint_list = PyList_New(n1);
            PyObject* _var_type = PyTuple_New(1);
            PyObject* _index = PyTuple_New(1);
            if (ctype1 == 3)
                if (ctype2 == 5){
                    for (int i=0; i < n1; i++){
                        PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 0), i));
                        PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 1), i));
                        PyList_SetItem(constraint_list, i, build_PyConstraintTuple(_var_type, _index, -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, -n2 + PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
                    }
                } else {
                    for (int i=0; i < n1; i++){
                        PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 0), i));
                        PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 1), i));
                        PyList_SetItem(constraint_list, i, build_PyConstraintTuple(_var_type, _index, -n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, -n2 + PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
                    }
                }
            else //ctype1 == 4
                if (ctype2 == 5){
                    for (int i=0; i < n1; i++){
                        PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 0), i));
                        PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 1), i));
                        PyList_SetItem(constraint_list, i, build_PyConstraintTuple(_var_type, _index, n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), 1, PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
                    }
                } else {
                    for (int i=0; i < n1; i++){
                        PyTuple_SetItem(_var_type, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 0), i));
                        PyTuple_SetItem(_index, 0, PyTuple_GetItem(PyTuple_GetItem(constraint1, 1), i));
                        PyList_SetItem(constraint_list, i, build_PyConstraintTuple(_var_type, _index, n2, PyTuple_GetItem(constraint2, 0), PyTuple_GetItem(constraint2, 1), -1, PyLong_AsLong(PyTuple_GetItem(constraint2, 3)), id));
                    }
                }
            return build_PyCompoundConstraints(n1, 1, constraint_list, id);
        } else {
            PyObject* constraints = PyList_New(2);
            PyList_SetItem(constraints, 0, constraint1);
            PyList_SetItem(constraints, 1, constraint2);
            return create_new_variable(1, 1, constraints, id);
        }
    } else {
        PyObject* constraints = PyList_New(2);
        PyList_SetItem(constraints, 0, constraint1);
        PyList_SetItem(constraints, 1, constraint2);
        return create_new_variable(1, 1, constraints, id);
    }

}

PyObject* transform_disjunctions(PyObject* constraints, PyObject* id, bool allow_mc)
{
    PyObject* compressed_compound_constraints = compress_disjunctions(constraints, id);
    PyObject* compressed_constraints = PyTuple_GetItem(compressed_compound_constraints, 2);
    long N = (long) PyList_Size(compressed_constraints);
    if (N < 2){
        return compressed_compound_constraints;
    } else if (allow_mc && N < 3) {
        return transform_two_disjunctions(PyList_GetItem(compressed_constraints, 0), PyList_GetItem(compressed_constraints, 1), id, allow_mc);
    } else {
        return create_new_variable(PyLong_AsLong(PyTuple_GetItem(compressed_compound_constraints, 0)), PyLong_AsLong(PyTuple_GetItem(compressed_compound_constraints, 1)), compressed_constraints, id);
    }

}

static PyObject* ctransform(PyObject* compound_constraint, bool allow_mc){
    long b = PyLong_AsLong(PyTuple_GetItem(compound_constraint, 0));
    long sign = PyLong_AsLong(PyTuple_GetItem(compound_constraint, 1));
    PyObject* constraints = PyTuple_GetItem(compound_constraint, 2);
    PyObject* id = PyTuple_GetItem(compound_constraint, 3);
    long N = (long)PyList_Size(constraints);
    long ctype = acp_type(b, N, sign);

    if (ctype==-1){
        PyErr_SetString(PyExc_ValueError, "ERROR: Found contradicition");
        return NULL;
    } else if (ctype==0){
        // No constraint needed
        PyObject* constraint_list = PyList_New(1);
        PyList_SetItem(constraint_list, 0, Py_None);
        return build_PyCompoundConstraints(0, 1, constraint_list, id);
    } else if (ctype==1)
        return transform_disjunctions(constraints, id, allow_mc);
    else if (ctype==4)
        return Py_None;
        //return CTransformConjunction(PyList_GetItem(constraints, 0), PyList_GetItem(constraints, 1), allow_mc);
    else if (ctype==5)
        printf("Create new variable");
    else if (ctype==2 || ctype==3 || ctype==6)
        printf("Create new variable");
}


static PyObject* merge(PyObject* self, PyObject* args)
{
    PyObject* compound_constraint;
    bool allow_mc;
    if (!PyArg_ParseTuple(args, "Op", &compound_constraint, &allow_mc))
        return NULL;

    return Py_BuildValue("O", ctransform(compound_constraint, allow_mc));
}


static PyMethodDef LogicMethods[] = {
        {"merge", merge, METH_VARARGS, "Merge constraints."},
        {NULL, NULL, 0, NULL}
};


static struct PyModuleDef logicfunc = {
    PyModuleDef_HEAD_INIT,
    "logicfunc",
    NULL,
    -1,
    LogicMethods
};

PyMODINIT_FUNC PyInit_logicfunc(void)
{
    return PyModule_Create(&logicfunc);
}



