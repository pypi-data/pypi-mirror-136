// Copyright (c) «2015-2022» «Shibzukhov Zaur, szport at gmail dot com»

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software - recordclass library - and associated documentation files
// (the "Software"), to deal in the Software without restriction, including
// without limitation the rights to use, copy, modify, merge, publish, distribute,
// sublicense, and/or sell copies of the Software, and to permit persons to whom
// the Software is furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

#ifdef Py_LIMITED_API
#undef Py_LIMITED_API
#endif
// #define Py_LIMITED_API 1

#include "Python.h"
#include "_dataobject.h"

#define DEFERRED_ADDRESS(addr) 0

#define PyObject_GetDictPtr(o) (PyObject**)((char*)o + (py_type(o)->tp_dictoffset))

#define pyobject_size(tp) ( (tp)->tp_basicsize )

#define py_incref(o) ((PyObject*)(o))->ob_refcnt++
#define py_decref(o) \
        if (--(((PyObject*)(o))->ob_refcnt) == 0) \
              py_type((PyObject*)(o))->tp_dealloc((PyObject*)(o))

#define py_xincref(op)                                \
    do {                                              \
        PyObject *_py_xincref_tmp = (PyObject *)(op); \
        if (_py_xincref_tmp != NULL)                  \
            py_incref(_py_xincref_tmp);               \
    } while (0)

#define py_xdecref(op)                                \
    do {                                              \
        PyObject *_py_xdecref_tmp = (PyObject *)(op); \
        if (_py_xdecref_tmp != NULL)                  \
            py_decref(_py_xdecref_tmp);               \
    } while (0)

#define py_set_type(ob, type) (((PyObject*)(ob))->ob_type) = (type)
#define py_type(ob) ((PyObject*)(ob))->ob_type

#define py_refcnt(ob) (((PyObject*)(ob))->ob_refcnt)
#define py_set_size(ob, size) (((PyVarObject*)(ob))->ob_size = (size))

static PyTypeObject PyDataObject_Type;
static PyTypeObject *datatype;
static PyTypeObject PyDataObjectProperty_Type;

PyObject *__fields__name;
PyObject *__dict__name;
PyObject *__weakref__name;
PyObject *__defaults__name;

PyObject *fields_dict_name;

// Py_ssize_t fields_hash;
// Py_ssize_t fields_dict_hash;
// Py_ssize_t defaults_hash;

static inline PyObject *
type_error(const char *msg, PyObject *obj)
{
    PyErr_Format(PyExc_TypeError, msg, py_type(obj)->tp_name);
    return NULL;
}

static inline int
_PyIndex_Check(PyObject *obj)
{
    PyNumberMethods *tp_as_number = py_type(obj)->tp_as_number;
    return (tp_as_number != NULL && tp_as_number->nb_index != NULL);
}

static PyObject **
PyDataObject_GetDictPtr(PyObject *ob) {
    Py_ssize_t dictoffset = py_type(ob)->tp_dictoffset;

    if (dictoffset <= 0) {
        PyErr_Format(PyExc_TypeError,
                "Invalid tp_dictoffset=%i of the type %s",
                dictoffset, py_type(ob)->tp_name);
        return NULL;
    }
    return (PyObject**) ((char *)ob + dictoffset);
}

static PyObject *
PyDataObject_GetDict(PyObject *obj)
{
    PyObject **dictptr = PyDataObject_GetDictPtr(obj);

    if (!dictptr) {
        PyErr_SetString(PyExc_AttributeError, "This object has no __dict__");
        return NULL;
    }

    PyObject *dict = *dictptr;
    if (!dict) {
        *dictptr = dict = PyDict_New();
        if (!dict) {
            PyErr_SetString(PyExc_TypeError, "can't create dict");
            return NULL;
        }
    }
    py_incref(dict);
    return dict;
}

static PyObject *
_PyObject_GetObject(const char *modname_c, const char *attrname_c)
{
    PyObject *modname;
    PyObject *mod, *ob;

    modname = PyUnicode_FromString(modname_c);
    if (modname == NULL)
        return NULL;
    mod = PyImport_Import(modname);
    if (mod == NULL) {
        Py_DECREF(modname);
        return NULL;
    }
    ob = PyObject_GetAttrString(mod, attrname_c);
    if (ob == NULL) {
        Py_DECREF(mod);
        return NULL;
    }
    Py_DECREF(modname);
    Py_DECREF(mod);
    return ob;
}

static PyObject *
pyobject_get_builtin(const char *attrname_c)
{
    PyObject *modname;
    PyObject *mod, *ob;

    modname = PyUnicode_FromString("builtins");
    if (modname == NULL)
        return NULL;
    mod = PyImport_Import(modname);
    if (mod == NULL) {
        Py_DECREF(modname);
        return NULL;
    }
    ob = PyObject_GetAttrString(mod, attrname_c);
    if (ob == NULL) {
        Py_DECREF(mod);
        return NULL;
    }
    Py_DECREF(modname);
    Py_DECREF(mod);
    return ob;
}

// forward decaration
static Py_ssize_t dataobject_len(PyObject *op);
static PyObject* dataobject_sq_item(PyObject *op, Py_ssize_t i);
static PyObject* _astuple(PyObject *op);
static int _dataobject_update(PyObject *op, PyObject *kw);

static PyObject *
dataobject_alloc(PyTypeObject *type, Py_ssize_t unused)
{
    Py_ssize_t size = pyobject_size(type);
    PyObject *op = (PyObject*)PyObject_Malloc(size);

    if (!op)
        return PyErr_NoMemory();

    memset(op, '\0', size);

    py_set_type(op, type);
    if (type->tp_flags & Py_TPFLAGS_HEAPTYPE)
        py_incref(type);

    _Py_NewReference(op);

    return op;
}

static PyObject *
dataobject_alloc_gc(PyTypeObject *type, Py_ssize_t unused)
{
    Py_ssize_t size = _PyObject_SIZE(type);
    PyObject *op = _PyObject_GC_Malloc(size);

    if (!op)
        return PyErr_NoMemory();

    memset(op, '\0', size);

    py_type(op) = type;
    if (type->tp_flags & Py_TPFLAGS_HEAPTYPE)
        py_incref(type);

    _Py_NewReference(op);

    PyObject_GC_Track(op);

    return op;
}

static PyObject*
dataobject_new_vc(PyTypeObject *type, PyObject * const*args, const Py_ssize_t n_args, PyObject *kwds)
{
    const Py_ssize_t n_items = PyDataObject_NUMITEMS(type);

    if (n_args > n_items) {
        PyErr_SetString(PyExc_TypeError,
                        "number of the arguments greater than the number of the items");
        return NULL;
    }

    PyObject *op = type->tp_alloc(type, 0);

    const PyObject **items = (const PyObject**)PyDataObject_ITEMS(op);

    for(Py_ssize_t i=0; i<n_args; i++) {
        PyObject *v = args[i];
        py_incref(v);
        items[i] = v;
    }

    if (n_items > n_args) {
        PyObject *tp_dict = type->tp_dict;
        PyMappingMethods *mp = py_type(tp_dict)->tp_as_mapping;
        PyObject *defaults = mp->mp_subscript(tp_dict, __defaults__name);

        if (defaults == NULL) {
            if (PyErr_Occurred())
                PyErr_Clear();

            for (Py_ssize_t i=n_args; i < n_items; i++) {
                py_incref(Py_None);
                items[i] = Py_None;
            }
        } else {
            PyObject *fields = mp->mp_subscript(tp_dict, __fields__name);
            Py_ssize_t n_fields = Py_SIZE(fields);

            if (n_fields != n_items) {
                PyErr_SetString(PyExc_TypeError,
                                "number of fields != number of data items");
                Py_DECREF(defaults);
                return NULL;
            }

            for(Py_ssize_t i=n_args; i<n_items; i++) {
                PyObject *fname = PyTuple_GetItem(fields, i);
                PyObject *value = PyDict_GetItem(defaults, fname);

                if (!value)
                    value = Py_None;

                py_incref(value);
                items[i] = value;
            }
            py_decref(fields);
            py_decref(defaults);
        }
    }

    if (kwds != NULL) {
        int retval;

        retval = _dataobject_update(op, kwds);

        if (retval < 0)
            return NULL;
    }

    return op;
}

static PyObject*
dataobject_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (type == &PyDataObject_Type) {
        PyErr_SetString(PyExc_TypeError,
                        "dataobject base class can't be instantiated");
        return NULL;
    }

    PyTupleObject *tmp = (PyTupleObject*)args;

    return dataobject_new_vc(type, (PyObject * const*)tmp->ob_item, Py_SIZE(tmp), kwds);
}

static int
dataobject_init(PyObject *ob, PyObject *args, PyObject *kwds) {
    return 0;
}

static int
dataobject_clear(PyObject *op)
{
    PyTypeObject *type = py_type(op);

    if (type->tp_dictoffset) {
        PyObject **dictptr = PyDataObject_DICTPTR(type, op);
        if (*dictptr) {
            PyObject *dict = *dictptr;
            if (dict != NULL) {
                Py_CLEAR(dict);
                *dictptr = NULL;
            }
        }
    }

    PyObject **items = PyDataObject_ITEMS(op);
    Py_ssize_t n_items = PyDataObject_NUMITEMS(type);
    while (n_items-- > 0) {
        Py_CLEAR(*items);
        items++;
    }

    return 0;
}

static int
dataobject_xdecref(PyObject *op)
{
    PyTypeObject *type = py_type(op);

    if (type->tp_weaklistoffset)
        PyObject_ClearWeakRefs(op);

    if (type->tp_dictoffset) {
        PyObject **dictptr = PyDataObject_DICTPTR(type, op);
        if (*dictptr) {
            PyObject *dict = *dictptr;
            if (dict != NULL) {
                py_decref(dict);
                *dictptr = NULL;
            }
        }
    }

    PyObject **items = PyDataObject_ITEMS(op);
    Py_ssize_t n_items = PyDataObject_NUMITEMS(type);

    while (n_items--) {
        PyObject *ob = *(items++);
        if (ob)
            py_decref(ob);
    }
    return 0;
}

static void
dataobject_dealloc(PyObject *op)
{
    PyTypeObject *type = py_type(op);

    if (type->tp_finalize != NULL) {
        if(PyObject_CallFinalizerFromDealloc(op) < 0)
            return;
    }

    dataobject_xdecref(op);

    if (type->tp_flags & Py_TPFLAGS_HEAPTYPE)
        py_decref(type);

    type->tp_free((PyObject *)op);
}

static void
dataobject_dealloc_gc(PyObject *op)
{
    PyTypeObject *type = py_type(op);

    if (type->tp_finalize != NULL) {
        if(PyObject_CallFinalizerFromDealloc(op) < 0)
            return;
    }

    PyObject_GC_UnTrack(op);

// #if PY_VERSION_HEX < 0x03080000
//     Py_TRASHCAN_SAFE_BEGIN(op)
// #else
//     Py_TRASHCAN_BEGIN(op, dataobject_dealloc)
// #endif

    dataobject_xdecref(op);

    if (type->tp_flags & Py_TPFLAGS_HEAPTYPE)
        py_decref(type);

    type->tp_free((PyObject *)op);

// #if PY_VERSION_HEX < 0x03080000
//     Py_TRASHCAN_SAFE_END(op)
// #else
//     Py_TRASHCAN_END
// #endif
}

static void
dataobject_finalize_step(PyObject *op, PyObject *stack)
{
    Py_ssize_t n_items = PyDataObject_LEN(op);
    PyObject **items = PyDataObject_ITEMS(op);

    while (n_items--) {
        PyObject *o = *items;

        if (py_refcnt(o) == 1 && Py_METATYPE(o) == datatype) {
            PyList_Append(stack, o);
        } else
            py_decref(o);

        *(items++) = NULL;
    }
}

static PyObject* stack = NULL;

static void
dataobject_finalize(PyObject *ob) {

    if (!stack)
        stack = PyList_New(0);

    dataobject_finalize_step(ob, stack);

    Py_ssize_t n_stack = PyList_GET_SIZE(stack);
    while (n_stack) {
        PyObject *op = PyList_GET_ITEM(stack, 0);

        if (py_refcnt(op) == 1)
            dataobject_finalize_step(op, stack);

        py_decref(op);

        {   PyList_SET_ITEM(stack, 0, NULL);
            for(Py_ssize_t j=1; j<n_stack; j++) {
                PyList_SET_ITEM(stack, j-1, PyList_GET_ITEM(stack, j));
            }
            n_stack--;
            PyList_SET_ITEM(stack, n_stack, NULL);
            py_set_size(stack, n_stack);
        }
    }
}

#ifdef PYPY_VERSION
static PyObject*
dataobject_getattr(PyObject *op, PyObject *name)
{
    PyObject *ob = PyDict_GetItem(py_type(op)->tp_dict, name);

    if (ob != NULL) {
        PyTypeObject *ob_type = py_type(ob);
        if (ob_type == &PyDataObjectProperty_Type) {
            return ob_type->tp_descr_get(ob, op, NULL);
        }
    }
    int is__dict__ = PyObject_RichCompareBool(name, __dict__name, Py_EQ);
    if (py_type(op)->tp_dictoffset) {
        PyObject **dictptr = (PyObject**)((char*)op + py_type(op)->tp_dictoffset);
        if (*dictptr) {
            PyObject *dict = *dictptr;
            if (is__dict__) {
                Py_INCREF(dict);
                return dict;
            }
            if (PyMapping_HasKey(dict, name)) {
                PyObject *res = PyDict_GetItem(dict, name);
                if (res) {
                    Py_INCREF(res);
                    return res;
                }
            }
        } else {
            *dictptr = PyDict_New();
            Py_INCREF(*dictptr);
            return *dictptr;
        }
    } else {
        if (is__dict__) {
            PyErr_Format(PyExc_AttributeError, "do not get __dict__ for type %s\n", py_type(op)->tp_name);
            return NULL;
        }
    }
    return PyObject_GenericGetAttr(op, name);
}

static int
dataobject_setattr(PyObject *op, PyObject *name, PyObject* val)
{
    PyObject *ob = PyDict_GetItem(py_type(op)->tp_dict, name);

    if (ob != NULL) {
        PyTypeObject *ob_type = py_type(ob);
        if (ob_type == &PyDataObjectProperty_Type) {
            return ob_type->tp_descr_set(ob, op, val);
        }
    }
    if (py_type(op)->tp_dictoffset) {
        PyObject **dictptr = (PyObject**)((char*)op + py_type(op)->tp_dictoffset);
        PyObject *dict;
        if (*dictptr)
            dict = *dictptr;
        else
            dict = *dictptr = PyDict_New();
        PyDict_SetItem(dict, name, val);
        return 1;
    }
    PyErr_Format(PyExc_AttributeError, "do not set attribute for type %s\n", py_type(op)->tp_name);
    return -1;
}
#endif

PyDoc_STRVAR(dataobject_len_doc,
"T.__len__() -- len of T");

static Py_ssize_t
dataobject_len(PyObject *op)
{
    Py_ssize_t n = PyDataObject_LEN(op);
    if (py_type(op)->tp_dictoffset) {
        PyObject **dictptr = PyDataObject_GetDictPtr(op);
        if (dictptr != NULL) {
            PyObject *dict = *dictptr;
            if (dict != NULL)
                n += PyDict_Size(dict);
        }
    }
    return n;
}

static int
dataobject_traverse(PyObject *op, visitproc visit, void *arg)
{
    PyTypeObject *type = py_type(op);
    Py_ssize_t n_items = PyDataObject_NUMITEMS(type);

    if (n_items) {
        PyObject **items = PyDataObject_ITEMS(op);
        while (n_items--) {
            Py_VISIT(*items);
            items++;
        }
    }

    if (type->tp_dictoffset) {
        PyObject **dictptr = PyDataObject_GetDictPtr(op);
        if (dictptr && *dictptr)
            Py_VISIT(*dictptr);
    }

    return 0;
}

static PyObject *
dataobject_sq_item(PyObject *op, Py_ssize_t i)
{
    Py_ssize_t n = PyDataObject_LEN(op);

    if (i < 0)
        i += n;
    if (i < 0 || i >= n) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }

    PyObject *v = PyDataObject_GET_ITEM(op, i);
    if (v == NULL) {
        PyErr_SetString(PyExc_IndexError, "item has no value");
        return NULL;
    }

    py_incref(v);
    return v;
}

static int
dataobject_sq_ass_item(PyObject *op, Py_ssize_t i, PyObject *val)
{
    Py_ssize_t n = PyDataObject_LEN(op);

    if (i < 0)
        i += n;
    if (i < 0 || i >= n) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return -1;
    }

    PyObject **items = PyDataObject_ITEMS(op) + i;

    py_xdecref(*items);

    if (val)
        py_incref(val);
    *items = val;

    return 0;
}

static PyObject*
dataobject_mp_subscript_only(PyObject* op, PyObject* name)
{
    PyObject* tp_dict = py_type(op)->tp_dict;
    PyObject* fields_dict = py_type(tp_dict)->tp_as_mapping->mp_subscript(tp_dict, fields_dict_name);

    PyObject* tp_dict2 = py_type(fields_dict)->tp_dict;
    PyObject* index = py_type(tp_dict2)->tp_as_mapping->mp_subscript(fields_dict, name);

    if (index == NULL)
        return NULL;

#ifdef PYPY_VERSION
    Py_ssize_t i = PyLong_AsSsize_t(index);
#else
    Py_ssize_t i = ((PyLongObject*)index)->ob_digit[0];
#endif

    PyObject *v = PyDataObject_GET_ITEM(op, i);
    py_incref(v);
    return v;
}

static int
dataobject_mp_ass_subscript_only(PyObject* op, PyObject* name, PyObject *val)
{
    PyObject* tp_dict = py_type(op)->tp_dict;
    PyObject* fields_dict = py_type(tp_dict)->tp_as_mapping->mp_subscript(tp_dict, fields_dict_name);

    PyObject* tp_dict2 = py_type(fields_dict)->tp_dict;
    PyObject* index = py_type(tp_dict2)->tp_as_mapping->mp_subscript(fields_dict, name);

    if (index == NULL)
        return -1;

#ifdef PYPY_VERSION
    Py_ssize_t i = PyLong_AsSsize_t(index);
#else
    Py_ssize_t i = ((PyLongObject*)index)->ob_digit[0];
#endif

    PyObject **items = PyDataObject_ITEMS(op) + i;
    // PyObject *v = *items;

    py_xdecref(*items);

    py_incref(val);
    *items = val;

    return 0;
}

static PyObject*
dataobject_mp_subscript(PyObject* op, PyObject* item)
{
    PyObject *ret = py_type(op)->tp_getattro(op, item);
    if (ret == NULL) {
        if (_PyIndex_Check(item)) {
            type_error("object %s do not support access by index", op);
        }
        return NULL;
    }
    return ret;
}

static int
dataobject_mp_ass_subscript(PyObject* op, PyObject* item, PyObject *val)
{
    int retval = py_type(op)->tp_setattro(op, item, val);
    if (retval < 0) {
        if (_PyIndex_Check(item)) {
            type_error("object %s do not support assignment by index", op);
        }
        return -1;
    }
    return retval;
}

static int
dataobject_mp_ass_subscript2(PyObject* op, PyObject* item, PyObject *val)
{
    PyNumberMethods *tp_as_number = py_type(item)->tp_as_number;
    if (tp_as_number != NULL && tp_as_number->nb_index != NULL) {
        Py_ssize_t i = PyLong_AsSsize_t(item);
        if (i == -1 && PyErr_Occurred())
            return -1;
        return dataobject_sq_ass_item(op, i, val);
    } else
        return py_type(op)->tp_setattro(op, item, val);
}

static PyObject*
dataobject_mp_subscript2(PyObject* op, PyObject* item)
{
    PyNumberMethods *tp_as_number = py_type(item)->tp_as_number;
    if (tp_as_number != NULL && tp_as_number->nb_index != NULL) {
        Py_ssize_t i = PyLong_AsSsize_t(item);
        if (i == -1 && PyErr_Occurred())
            return NULL;
        return dataobject_sq_item(op, i);
    } else
        return py_type(op)->tp_getattro(op, item);
}

static int
dataobject_mp_ass_subscript_sq(PyObject* op, PyObject* item, PyObject *val)
{
    PyNumberMethods *tp_as_number = py_type(item)->tp_as_number;
    if (tp_as_number != NULL && tp_as_number->nb_index != NULL) {
        Py_ssize_t i = PyLong_AsSsize_t(item);
        if (i == -1 && PyErr_Occurred())
            return -1;
        return dataobject_sq_ass_item(op, i, val);
    } else {
        type_error("object %s support only assignment by index", op);
        return -1;
    }
}

static PyObject*
dataobject_mp_subscript_sq(PyObject* op, PyObject* item)
{
    PyNumberMethods *tp_as_number = py_type(item)->tp_as_number;
    if (tp_as_number != NULL && tp_as_number->nb_index != NULL) {
        Py_ssize_t i = PyLong_AsSsize_t(item);
        if (i == -1 && PyErr_Occurred())
            return NULL;
        return dataobject_sq_item(op, i);
    } else {
        type_error("object %s get item only by index", op);
        return NULL;
    }
}

static int
dataobject_mp_ass_subscript0(PyObject* op, PyObject* item, PyObject *val)
{
    type_error("object %s does not support set item", op);
    return -1;
}

static PyObject*
dataobject_mp_subscript0(PyObject* op, PyObject* item)
{
    type_error("object %s does not support assignment", op);
    return NULL;
}

static void copy_sequence_methods(PySequenceMethods *out, PySequenceMethods *in) {
    out->sq_length = in->sq_length;
    out->sq_concat = in->sq_concat;
    out->sq_repeat = in->sq_repeat;
    out->sq_item = in->sq_item;
    out->was_sq_slice = in->was_sq_slice;
    out->sq_ass_item = in->sq_ass_item;
    out->was_sq_ass_slice = in->was_sq_ass_slice;
    out->sq_contains = in->sq_contains;
}


static PySequenceMethods dataobject_as_sequence = {
    (lenfunc)dataobject_len,                /* sq_length */
    0,                                      /* sq_concat */
    0,                                      /* sq_repeat */
    (ssizeargfunc)dataobject_sq_item,          /* sq_item */
    0,                                      /* sq_slice */
    (ssizeobjargproc)dataobject_sq_ass_item,   /* sq_ass_item */
    0,                                      /* sq_ass_slice */
    0,                                      /* sq_contains */
};

static PySequenceMethods dataobject_as_sequence0 = {
    (lenfunc)dataobject_len,                /* sq_length */
    0,                                      /* sq_concat */
    0,                                      /* sq_repeat */
    0,          /* sq_item */
    0,                                      /* sq_slice */
    0,   /* sq_ass_item */
    0,                                      /* sq_ass_slice */
    0,                                      /* sq_contains */
};

static PySequenceMethods dataobject_as_sequence_ro = {
    (lenfunc)dataobject_len,         /* sq_length */
    0,                               /* sq_concat */
    0,                               /* sq_repeat */
    (ssizeargfunc)dataobject_sq_item,   /* sq_item */
    0,                               /* sq_slice */
    0,                               /* sq_ass_item */
    0,                               /* sq_ass_slice */
    0,                               /* sq_contains */
};

static void copy_mapping_methods(PyMappingMethods *out, PyMappingMethods *in) {
    out->mp_length = in->mp_length;
    out->mp_subscript = in->mp_subscript;
    out->mp_ass_subscript = in->mp_ass_subscript;
}

static PyMappingMethods dataobject_as_mapping = {
    (lenfunc)dataobject_len,                  /* mp_len */
    (binaryfunc)dataobject_mp_subscript,         /* mp_subscr */
    (objobjargproc)dataobject_mp_ass_subscript,  /* mp_ass_subscr */
};

static PyMappingMethods dataobject_as_mapping_only = {
    (lenfunc)dataobject_len,                  /* mp_len */
    (binaryfunc)dataobject_mp_subscript_only,         /* mp_subscr */
    (objobjargproc)dataobject_mp_ass_subscript_only,  /* mp_ass_subscr */
};

static PyMappingMethods dataobject_as_mapping_only_ro = {
    (lenfunc)dataobject_len,                  /* mp_len */
    (binaryfunc)dataobject_mp_subscript_only,         /* mp_subscr */
    0,  /* mp_ass_subscr */
};

static PyMappingMethods dataobject_as_mapping0 = {
    (lenfunc)dataobject_len,                  /* mp_len */
    (binaryfunc)dataobject_mp_subscript0,         /* mp_subscr */
    (objobjargproc)dataobject_mp_ass_subscript0,  /* mp_ass_subscr */
};

static PyMappingMethods dataobject_as_mapping_ro = {
    (lenfunc)dataobject_len,            /* mp_len */
    (binaryfunc)dataobject_mp_subscript,   /* mp_subscr */
    (objobjargproc)dataobject_mp_ass_subscript0,  /* mp_ass_subscr */
};

static PyMappingMethods dataobject_as_mapping2 = {
    (lenfunc)dataobject_len,                   /* mp_len */
    (binaryfunc)dataobject_mp_subscript2,         /* mp_subscr */
    (objobjargproc)dataobject_mp_ass_subscript2,  /* mp_ass_subscr */
};

static PyMappingMethods dataobject_as_mapping2_ro = {
    (lenfunc)dataobject_len,            /* mp_len */
    (binaryfunc)dataobject_mp_subscript2,  /* mp_subscr */
    (objobjargproc)dataobject_mp_ass_subscript0,   /* mp_ass_subscr */
};

static PyMappingMethods dataobject_as_mapping_sq = {
    (lenfunc)dataobject_len,                   /* mp_len */
    (binaryfunc)dataobject_mp_subscript_sq,         /* mp_subscr */
    (objobjargproc)dataobject_mp_ass_subscript_sq,  /* mp_ass_subscr */
};

static PyMappingMethods dataobject_as_mapping_sq_ro = {
    (lenfunc)dataobject_len,            /* mp_len */
    (binaryfunc)dataobject_mp_subscript_sq,  /* mp_subscr */
    (objobjargproc)dataobject_mp_ass_subscript0,      /* mp_ass_subscr */
};


#ifndef _PyHASH_MULTIPLIER
#define _PyHASH_MULTIPLIER 1000003UL
#endif

static Py_hash_t
dataobject_hash(PyObject *op)
{
    const Py_ssize_t len = PyDataObject_LEN(op);
    Py_hash_t mult = _PyHASH_MULTIPLIER;

    Py_uhash_t x = 0x345678L;
    for(Py_ssize_t i=0; i<len; i++) {
        PyObject *o = PyDataObject_GET_ITEM(op, i);
        Py_hash_t y = PyObject_Hash(o);
//         Py_DECREF(o);
        if (y == -1)
            return -1;
        x = (x ^ y) * mult;
        mult += (Py_hash_t)(82520L + len + len);
    }

    x += 97531L;
    if (x == (Py_uhash_t)-1)
        x = -2;
    return x;
}

static Py_hash_t
dataobject_hash_ni(PyObject *op)
{
        type_error("__hash__ is not implemented for %s", op);
        return -1;
}

// PyDoc_STRVAR(dataobject_hash_doc,
// "T.__hash__() -- __hash__ for T");

// static PyObject*
// dataobject_hash2(PyObject *op)
// {
//     return PyLong_FromSsize_t(dataobject_hash(op));
// }

// static PyObject*
// dataobject_hash2_ni(PyObject *op)
// {
//     dataobject_hash_ni(op);
//     return NULL;
// }

static PyObject *
dataobject_richcompare(PyObject *v, PyObject *w, int op)
{
    Py_ssize_t i, k;
    Py_ssize_t vlen = PyDataObject_LEN(v), wlen = PyDataObject_LEN(w);
    PyObject *vv;
    PyObject *ww;
    PyObject *ret;

    if (!(py_type(v) == py_type(w)) || (!PyObject_IsSubclass((PyObject*)py_type(w), (PyObject*)py_type(v))))
        Py_RETURN_NOTIMPLEMENTED;

    if ((vlen != wlen) && (op == Py_EQ || op == Py_NE)) {
        PyObject *res;
        if (op == Py_EQ)
            res = Py_False;
        else
            res = Py_True;
        Py_INCREF(res);
        return res;
    }

    for (i = 0; i < vlen && i < wlen; i++) {
        vv = PyDataObject_GET_ITEM(v, i);
        ww = PyDataObject_GET_ITEM(w, i);
        k = PyObject_RichCompareBool(vv, ww, Py_EQ);
//         Py_DECREF(vv);
//         Py_DECREF(ww);
        if (k < 0)
            return NULL;
        if (!k)
            break;
    }

    if (i >= vlen || i >= wlen) {
        /* No more items to compare -- compare sizes */
        int cmp;
        PyObject *res;
        switch (op) {
        case Py_LT: cmp = vlen <  wlen; break;
        case Py_LE: cmp = vlen <= wlen; break;
        case Py_EQ: cmp = vlen == wlen; break;
        case Py_NE: cmp = vlen != wlen; break;
        case Py_GT: cmp = vlen >  wlen; break;
        case Py_GE: cmp = vlen >= wlen; break;
        default: return NULL; /* cannot happen */
        }
        if (cmp)
            res = Py_True;
        else
            res = Py_False;
        Py_INCREF(res);
        return res;
    }

    /* We have an item that differs -- shortcuts for EQ/NE */
    if (op == Py_EQ) {
        Py_INCREF(Py_False);
        return Py_False;
    }
    if (op == Py_NE) {
        Py_INCREF(Py_True);
        return Py_True;
    }

    /* Compare the final item again using the proper operator */
    vv = PyDataObject_GET_ITEM(v, i);
    ww = PyDataObject_GET_ITEM(w, i);
    ret = PyObject_RichCompare(vv, ww, op);
//     Py_DECREF(vv);
//     Py_DECREF(ww);

    return ret;
}

PyDoc_STRVAR(dataobject_sizeof_doc,
"T.__sizeof__() -- size of T");

static PyObject *
dataobject_sizeof(PyObject *self)
{
    return PyLong_FromSsize_t(py_type(self)->tp_basicsize);
}

PyDoc_STRVAR(dataobject_copy_doc,
"T.__copy__() -- copy of T");

static PyObject *
dataobject_copy(PyObject* op)
{
    PyTypeObject *type = py_type(op);

    const Py_ssize_t n_items = PyDataObject_NUMITEMS(type);

    PyObject *new_op = type->tp_alloc(type, 0);

    PyObject **items = (PyObject**)PyDataObject_ITEMS(new_op);
    PyObject **args = (PyObject**)PyDataObject_ITEMS(op);

    for(Py_ssize_t i=0; i<n_items; i++) {
        PyObject *v = args[i];
        py_incref(v);
        items[i] = v;
    }

    if (type->tp_dictoffset) {
        PyObject **dictptr = PyDataObject_DICTPTR(type, op);
        PyObject* dict = NULL;

        if (*dictptr)
            dict = *dictptr;

        if (dict != NULL) {
            int retval;

            py_incref(dict);
            retval = _dataobject_update(new_op, dict);
            py_decref(dict);

            if (retval < 0)
                return NULL;
        }
    }

    return new_op;
}

// static PyObject *
// dataobject_repr(PyObject *self)
// {
//     Py_ssize_t i, n, n_fs = 0;
//     _PyUnicodeWriter writer;
//     PyObject *fs;
//     PyTypeObject *tp = py_type(self);
//     PyObject *tp_name = PyObject_GetAttrString((PyObject*)tp, "__name__");
//     PyObject *text;

//     fs = PyObject_GetAttrString(self, "__fields__");
//     if (fs) {
//         if (py_type(fs) == &PyTuple_Type) {
//             n_fs = PyObject_Length(fs);
//         } else {
//             n_fs = (Py_ssize_t)PyNumber_AsSsize_t(fs, PyExc_IndexError);
//             if (n_fs < 0) {
//                 Py_DECREF(fs);
//                 Py_DECREF(tp_name);
//                 return NULL;
//             }
//             n_fs = 0;
//         }
//     } else
//         PyErr_Clear();

//     n = dataobject_len(self);
//     if (n == 0) {
//         PyObject *s = PyUnicode_FromString("()");
//         text = PyUnicode_Concat(tp_name, s);
//         Py_DECREF(s);
//         Py_DECREF(tp_name);
//         return text;
//     }

//     i = Py_ReprEnter((PyObject *)self);
//     if (i != 0) {
//         Py_DECREF(tp_name);
//         return i > 0 ? PyUnicode_FromString("(...)") : NULL;
//     }

//     _PyUnicodeWriter_Init(&writer);
//     writer.overallocate = 1;
//     if (n > 1) {
//         /* "(" + "1" + ", 2" * (len - 1) + ")" */
//         writer.min_length = 1 + 1 + (2 + 1) * (n-1) + 1;
//     }
//     else {
//         /* "(1,)" */
//         writer.min_length = 4;
//     }

//     if (_PyUnicodeWriter_WriteStr(&writer, tp_name) < 0)
//         goto error;

//     Py_DECREF(tp_name);

//     if (_PyUnicodeWriter_WriteChar(&writer, '(') < 0)
//         goto error;

//     /* Do repr() on each element. */
//     for (i = 0; i < n; ++i) {
//         PyObject *s, *ob;
//         PyObject *fn;

//         if (n_fs > 0 && i < n_fs) {
//             fn = PyTuple_GET_ITEM(fs, i);
//             Py_INCREF(fn);
//             if (_PyUnicodeWriter_WriteStr(&writer, fn) < 0) {
//                 Py_DECREF(fn);
//                 goto error;
//             }
//             Py_DECREF(fn);
//             if (_PyUnicodeWriter_WriteChar(&writer, '=') < 0)
//                 goto error;
//         }

//         ob = dataobject_item(self, i);
//         if (ob == NULL)
//             goto error;

//         s = PyObject_Repr(ob);
//         if (s == NULL) {
//             Py_DECREF(ob);
//             goto error;
//         }

//         if (_PyUnicodeWriter_WriteStr(&writer, s) < 0) {
//             Py_DECREF(s);
//             Py_DECREF(ob);
//             goto error;
//         }
//         Py_DECREF(s);
//         Py_DECREF(ob);

//         if (i < n-1) {
//             if (_PyUnicodeWriter_WriteASCIIString(&writer, ", ", 2) < 0)
//                 goto error;
//         }
//     }

//     Py_XDECREF(fs);

//     if (tp->tp_dictoffset) {
//         PyObject *dict = PyObject_GetAttrString(self, "__dict__");
//         PyObject *s;

//         if (dict) {
//             if (PyObject_IsTrue(dict)) {
//                 if (_PyUnicodeWriter_WriteASCIIString(&writer, ", **", 4) < 0)
//                     goto error;
//                 s = PyObject_Repr(dict);
//                 if (_PyUnicodeWriter_WriteStr(&writer, s) < 0) {
//                     Py_DECREF(s);
//                     Py_DECREF(dict);
//                     goto error;
//                 }
//                 Py_DECREF(s);
//             }
//             Py_DECREF(dict);
//         }
//     }

//     writer.overallocate = 0;

//     if (_PyUnicodeWriter_WriteChar(&writer, ')') < 0)
//         goto error;

//     Py_ReprLeave((PyObject *)self);
//     return _PyUnicodeWriter_Finish(&writer);

// error:
//     Py_XDECREF(fs);

//     _PyUnicodeWriter_Dealloc(&writer);
//     Py_ReprLeave((PyObject *)self);
//     return NULL;
// }

PyDoc_STRVAR(dataobject_subscript_doc,
"T.__getitem__(ob, key)");

static PyObject *
dataobject_subscript(PyObject *ob, PyObject *key)
{
    PyMappingMethods *m = py_type(ob)->tp_as_mapping;

    if (m->mp_subscript) {
        return m->mp_subscript(ob, key);
    }

    return type_error("instances of %s are not subsciptable", (PyObject*)py_type(ob));
}

PyDoc_STRVAR(dataobject_ass_subscript_doc,
"T.__setitem__(ob, key, val)");

static PyObject*
dataobject_ass_subscript(PyObject *ob, PyObject *args)
{
    if (Py_SIZE(args) != 2) {
        type_error("__setitem__ need 2 args", ob);
        return NULL;
    }

    // PyObject *key = PyTuple_GET_ITEM(args, 0);
    // PyObject *val = PyTuple_GET_ITEM(args, 1);


    PyMappingMethods *m = py_type(ob)->tp_as_mapping;

    if (m->mp_ass_subscript) {
        if (m->mp_ass_subscript(ob,
                                PyTuple_GET_ITEM(args, 0),
                                PyTuple_GET_ITEM(args, 1)))
            return NULL;
        else
            Py_RETURN_NONE;
    }

    type_error("instances of %s does not support item assignment", (PyObject*)py_type(ob));
    return NULL;
}


PyDoc_STRVAR(dataobject_reduce_doc,
"T.__reduce__()");

static PyObject *
dataobject_reduce(PyObject *ob) //, PyObject *Py_UNUSED(ignore))
{
    PyObject *args;
    PyObject *result;
    PyTypeObject *tp = py_type(ob);
    PyObject *kw = NULL;
    PyObject **dictptr;

    args = _astuple(ob);
    if (args == NULL)
        return NULL;

    if (tp->tp_dictoffset) {
        dictptr = PyObject_GetDictPtr(ob);
        if (dictptr) {
            PyObject *d = *dictptr;
            if (d)
                kw = PyDict_Copy(d);
        }
    }
    if (kw)
        result = PyTuple_Pack(3, tp, args, kw);
    else
        result = PyTuple_Pack(2, tp, args);

    Py_DECREF(args);
    Py_XDECREF(kw);
    return result;
}

PyDoc_STRVAR(dataobject_getstate_doc,
"T.__getstate__()");

static PyObject *
dataobject_getstate(PyObject *ob) {
    PyTypeObject *tp = py_type(ob);
    PyObject **dictptr;

    if (tp->tp_dictoffset) {
        dictptr = PyObject_GetDictPtr(ob);
        if (dictptr && *dictptr) {
            return PyDict_Copy(*dictptr);
        }
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(dataobject_setstate_doc,
"T.__setstate__()");

static PyObject*
dataobject_setstate(PyObject *ob, PyObject *state) {
    PyTypeObject *tp = py_type(ob);
    PyObject *dict;

    if (!state || state == Py_None)
        return 0;

    if (tp->tp_dictoffset) {
        dict = PyDataObject_GetDict(ob);

        if (!dict) {
            // PyErr_SetString(PyExc_TypeError, "failed to create new dict");
            return NULL;
        }

        if (PyDict_Update(dict, state) < 0) {
            PyErr_SetString(PyExc_TypeError, "dict update failed");
            Py_DECREF(dict);
            return NULL;
        }
        Py_DECREF(dict);
    } else {
        PyErr_SetString(PyExc_TypeError, "object has no __dict__");
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyMethodDef dataobject_methods[] = {
    {"__getitem__",  (PyCFunction)(void(*)(void))dataobject_subscript, METH_O|METH_COEXIST, dataobject_subscript_doc},
    {"__setitem__",  (PyCFunction)dataobject_ass_subscript, METH_VARARGS|METH_COEXIST, dataobject_ass_subscript_doc},
    {"__copy__",     (PyCFunction)dataobject_copy, METH_NOARGS, dataobject_copy_doc},
    {"__len__",      (PyCFunction)dataobject_len, METH_NOARGS, dataobject_len_doc},
    {"__sizeof__",   (PyCFunction)dataobject_sizeof, METH_NOARGS, dataobject_sizeof_doc},
    {"__reduce__",   (PyCFunction)dataobject_reduce, METH_NOARGS, dataobject_reduce_doc},
    {"__getstate__", (PyCFunction)dataobject_getstate, METH_NOARGS, dataobject_getstate_doc},
    {"__setstate__", (PyCFunction)dataobject_setstate, METH_O, dataobject_setstate_doc},
    // {"__hash__",     (PyCFunction)dataobject_hash2_ni, METH_O, dataobject_hash_doc},
    {NULL}
};

static PyObject *dataobject_iter(PyObject *seq);

// static PyObject* __dict__get(PyObject *ob, void *unused) {
//     if (!py_type(ob)->tp_dictoffset) {
//             PyErr_SetString(PyExc_AttributeError, "the instance hasn't __dict__");
//             return NULL;
//     } else {
//         PyObject** dictptr = (PyObject**)((char*)ob + py_type(ob)->tp_dictoffset);
//         PyObject *dict;
//         if (*dictptr) {
//             dict = *dictptr;
//         } else {
//             *dictptr = dict = PyDict_New();
//         }
//         Py_INCREF(dict);
//         return dict;
//     }
// }

// static PyGetSetDef dataobject_getset[] = {
//     {"__dict__", __dict__get, NULL, "__dict__ property", NULL},
//     {NULL, NULL, NULL, NULL, NULL}
// };

PyDoc_STRVAR(dataobject_doc,
"dataobject(...) --> dataobject\n\n\
");

static PyTypeObject PyDataObject_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "recordclass._dataobject.dataobject",   /* tp_name */
    sizeof(PyObject),                       /* tp_basicsize */
    0,                                      /* tp_itemsize */
    /* methods */
    (destructor)dataobject_dealloc,         /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_reserved */
    0,                                      /* tp_repr */
    0,                                      /* tp_as_number */
    &dataobject_as_sequence0,               /* tp_as_sequence */
    &dataobject_as_mapping0,                /* tp_as_mapping */
    &dataobject_hash_ni,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
#ifdef PYPY_VERSION
    dataobject_getattr,                                      /* tp_setattro */
    dataobject_setattr,                                      /* tp_setattro */
#else
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
#endif
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
                                            /* tp_flags */
    dataobject_doc,                         /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    dataobject_richcompare,                 /* tp_richcompare */
    0,                                      /* tp_weaklistoffset*/
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    dataobject_methods,                     /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    dataobject_init,                                      /* tp_init */
    dataobject_alloc,                       /* tp_alloc */
    dataobject_new,                         /* tp_new */
    PyObject_Del,                        /* tp_free */
    0                                       /* tp_is_gc */
};



//////////////////////////////////////////////////////////////////////////

static PyObject* dataobject_iter(PyObject *seq);

//////////////////////////////////////////////////////////////////////////

// /*********************** DataObjectWRef **************************/

// typedef struct {
//     PyObject_HEAD
//     PyObject *value;
// } dataobject_weakref;

// static PyObject *
// dataobject_weakref_new(PyObject *value)
// {
//     dataobject_weakref *wref;

//     wref = PyObject_New(dataobject_weakref, &PyDataObjectWRef_Type);
//     if (wref == NULL)
//         return NULL;
//     if (value == NULL)
//         value = Py_None;
//     wref->value = value;
//     Py_INCREF(value);
//     return (PyObject *)wref;
// }

// static void
// dataobject_weakref_dealloc(dataobject_weakref *wref)
// {
//     Py_CLEAR(wref->value);
//     PyObject_Del(wref);
// }

// static PyObject*
// dataobject_weakref_get_value(PyObject *self)
// {
//     PyObject *value;
//     value = ((struct dataobject_weakref*)self)->value;
//     Py_INCREF(value);
//     return value;
// }

// static int
// dataobject_weakref_set_value(PyObject *self, PyObject *val)
// {
//     PyObject *value = ((struct dataobject_weakref*)self)->value;
//     Py_XDECREF(value);
//     Py_INCREF(val);
//     ((struct dataobject_weakref*)self)->value = val;
//     return 0;
// }

// static PyGetSetDef dataobject_weakref_getsets[] = {
//     {"value", (getter)dataobject_weakref_value, (setter)dataobject_weakref_set_value, NULL},
//     {0}
// };

// PyTypeObject PyDataObjectWRef_Type = {
//     PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
//     "recordclass._dataobject.dataobject_weakref",                           /* tp_name */
//     sizeof(dataobject_weakref),                    /* tp_basicsize */
//     0,                                          /* tp_itemsize */
//     /* methods */
//     (destructor)dataobject_weakref_dealloc,              /* tp_dealloc */
//     0,                                          /* tp_print */
//     0,                                          /* tp_getattr */
//     0,                                          /* tp_setattr */
//     0,                                          /* tp_reserved */
//     0,                                          /* tp_repr */
//     0,                                          /* tp_as_number */
//     0,                                          /* tp_as_sequence */
//     0,                                          /* tp_as_mapping */
//     0,                                          /* tp_hash */
//     0,                                          /* tp_call */
//     0,                                          /* tp_str */
//     PyObject_GenericGetAttr,                    /* tp_getattro */
//     0,                                          /* tp_setattro */
//     0,                                          /* tp_as_buffer */
//     Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,                         /* tp_flags */
//     0,                                          /* tp_doc */
//     0,     /* tp_traverse */
//     0,             /* tp_clear */
//     0,                                          /* tp_richcompare */
//     0,                                          /* tp_weaklistoffset */
//     PyObject_SelfIter,                          /* tp_iter */
//     (iternextfunc)dataobjectiter_next,         /* tp_iternext */
//     dataobjectiter_methods,                    /* tp_methods */
//     0,                                      /* tp_members */
//     dataobject_weakref_getsets,                                      /* tp_getset */
//     0,                                      /* tp_base */
//     0,                                      /* tp_memoryslots */
//     0,                                      /* tp_descr_get */
//     0,                                      /* tp_descr_set */
//     0,                                      /* tp_memoryslotsoffset */
//     0,                                      /* tp_init */
//     0,                         /* tp_alloc */
//     dataobject_weakref_new,                           /* tp_new */
//     PyObject_Del,                          /* tp_free */
//     0                                       /* tp_is_gc */
// };


/*********************** DataObject Iterator **************************/

static PyObject* dataobject_iter(PyObject *seq);

typedef struct {
    PyObject_HEAD
    Py_ssize_t it_index, it_len;
    PyObject *it_seq; /* Set to NULL when iterator is exhausted */
} dataobjectiterobject;

static void
dataobjectiter_dealloc(dataobjectiterobject *it)
{
    PyTypeObject *tp = py_type(it);

#if PY_VERSION_HEX < 0x03080000
    if (tp->tp_flags & Py_TPFLAGS_HEAPTYPE)
    Py_DECREF(tp);
#endif

    Py_XDECREF(it->it_seq);
    tp->tp_free((PyObject *)it);
}

// static int
// dataobjectiter_clear(PyObject *op)
// {
//     dataobjectiterobject *it = (dataobjectiterobject*)op;
//     Py_CLEAR(it->it_seq);
//     return 0;
// }

// static int
// dataobjectiter_traverse(PyObject *op, visitproc visit, void *arg)
// {
//     dataobjectiterobject *it = (dataobjectiterobject*)op;
//     Py_VISIT(it->it_seq);
//     return 0;
// }

static PyObject *
dataobjectiter_next(dataobjectiterobject *it)
{
    PyObject *item;
    PyObject *op = it->it_seq;

    if (it->it_index < it->it_len) {
        item = PyDataObject_GET_ITEM(op, it->it_index);
        Py_INCREF(item);
        it->it_index++;
        return item;
    }

//     Py_DECREF(it->it_seq);
//     it->it_seq = NULL;
    return NULL;
}

static PyObject *
dataobjectiter_len(dataobjectiterobject *it)
{
    Py_ssize_t len = 0;
    if (it->it_seq)
        len = it->it_len - it->it_index;
    return PyLong_FromSsize_t(len);
}

PyDoc_STRVAR(length_hint_doc, "Private method returning an estimate of len(list(it)).");

static PyObject *
dataobjectiter_reduce(dataobjectiterobject *it) //, PyObject *Py_UNUSED(ignore))
{
    if (it->it_seq)
        return Py_BuildValue("N(O)n", pyobject_get_builtin("iter"),
                             it->it_seq, it->it_index);
    else
        return Py_BuildValue("N(())", pyobject_get_builtin("iter"));
}

PyDoc_STRVAR(dataobjectiter_reduce_doc, "D.__reduce__()");

static PyObject *
dataobjectiter_setstate(dataobjectiterobject *it, PyObject *state)
{
    Py_ssize_t index;

    index = PyLong_AsSsize_t(state);
    if (index == -1 && PyErr_Occurred())
        return NULL;
    if (it->it_seq != NULL) {
        if (index < 0)
            index = 0;
        else if (index > it->it_len)
            index = it->it_len; /* exhausted iterator */
        it->it_index = index;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(setstate_doc, "Set state information for unpickling.");

static PyMethodDef dataobjectiter_methods[] = {
    {"__length_hint__", (PyCFunction)dataobjectiter_len, METH_NOARGS, length_hint_doc},
    {"__reduce__",      (PyCFunction)dataobjectiter_reduce, METH_NOARGS, dataobjectiter_reduce_doc},
    {"__setstate__",    (PyCFunction)dataobjectiter_setstate, METH_O, setstate_doc},
    {NULL,              NULL}           /* sentinel */
};

PyTypeObject PyDataObjectIter_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "recordclass._dataobject.dataobject_iterator",  /* tp_name */
    sizeof(dataobjectiterobject),               /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)dataobjectiter_dealloc,         /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_reserved */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,
                                                /* tp_flags */
    0,                                          /* tp_doc */
    0,                    /* tp_traverse */
    0,                        /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    (iternextfunc)dataobjectiter_next,          /* tp_iternext */
    dataobjectiter_methods,                     /* tp_methods */
    0,
};

static PyObject *
dataobject_iter(PyObject *seq)
{
    dataobjectiterobject *it;

    if (!seq)
        return NULL;

    if (py_type(seq)->tp_base != &PyDataObject_Type && !PyType_IsSubtype(py_type(seq), &PyDataObject_Type)) {
        PyErr_SetString(PyExc_TypeError, "the object is not instance of dataobject");
        return NULL;
    }

    it = PyObject_New(dataobjectiterobject, &PyDataObjectIter_Type);
    if (it == NULL)
        return NULL;

#if PY_VERSION_HEX < 0x03080000
    {
        PyTypeObject *t = py_type(it);
        if (t->tp_flags & Py_TPFLAGS_HEAPTYPE)
            Py_INCREF(t);
    }
#endif

    it->it_index = 0;
    it->it_seq = seq;
    Py_INCREF(seq);
    it->it_len = PyDataObject_LEN(seq);

    return (PyObject *)it;
}

////////////////////////////////////////////////////////////////////////

typedef struct {
    PyObject_HEAD
    Py_ssize_t index;
    int readonly;
} dataobjectproperty_object;

static PyMethodDef dataobjectproperty_methods[] = {
//   {"__set_name__", dataobjectproperty_setname, METH_VARARGS, dataobjectproperty_setname_doc},
  {0, 0, 0, 0}
};

static PyObject* dataobjectproperty_new(PyTypeObject *t, PyObject *args, PyObject *k) {
    dataobjectproperty_object *ob = NULL;
    PyObject *item;
    Py_ssize_t len, index;
    int readonly;

    len = Py_SIZE(args);
    if (len == 0 || len > 2) {
        PyErr_SetString(PyExc_TypeError, "number of args is 1 or 2");
        return NULL;
    }

    item = PyTuple_GET_ITEM(args, 0);
    index = PyNumber_AsSsize_t(item, PyExc_IndexError);
    if (index == -1 && PyErr_Occurred()) {
        return NULL;
    }

    item = PyTuple_GET_ITEM(args, 1);
    if (len == 2)
        readonly = PyObject_IsTrue(item);
    else
        readonly = 0;

    ob = PyObject_New(dataobjectproperty_object, t);
    if (ob == NULL)
        return NULL;

#if PY_VERSION_HEX < 0x03080000
        if (t->tp_flags & Py_TPFLAGS_HEAPTYPE)
            Py_INCREF(t);
#endif
    ob->readonly = readonly;
    ob->index = index;
    return (PyObject*)ob;
}

static void dataobjectproperty_dealloc(PyObject *o) {
    PyTypeObject *t = py_type(o);

    t->tp_free(o);

#if PY_VERSION_HEX >= 0x03080000
    if (t->tp_flags & Py_TPFLAGS_HEAPTYPE)
        Py_DECREF(t);
#endif
}

static PyObject* dataobjectproperty_get(PyObject *self, PyObject *obj, PyObject *type) {

    if (obj == NULL || obj == Py_None) {
        Py_INCREF(self);
        return self;
    }

    PyObject *v = PyDataObject_GET_ITEM(obj, ((dataobjectproperty_object *)self)->index);
    if (v == NULL) {
        PyErr_SetString(PyExc_AttributeError, "the attribute has no value");
        return NULL;
    }

    py_incref(v);
    return v;
}

static int dataobjectproperty_set(PyObject *self, PyObject *obj, PyObject *value) {

    if (value == NULL) {
        PyErr_SetString(PyExc_AttributeError, "The field and it's value can't be deleted");
        return -1;
    }

    if (obj == NULL || obj == Py_None)
        return 0;

    if (((dataobjectproperty_object *)self)->readonly) {
        PyErr_SetString(PyExc_TypeError, "item is readonly");
        return -1;
    }

    PyObject *v = PyDataObject_GET_ITEM(obj, ((dataobjectproperty_object *)self)->index);
    py_xdecref(v);

    py_incref(value);
    PyDataObject_SET_ITEM(obj, ((dataobjectproperty_object *)self)->index, value);

    return 0;
}

static PyObject*
dataobjectproperty_index(PyObject *self)
{
    return PyLong_FromSsize_t(((dataobjectproperty_object*)self)->index);
}

static PyObject*
dataobjectproperty_readonly(PyObject *self)
{
    return PyBool_FromLong((long)(((dataobjectproperty_object*)self)->readonly));
}

// static int
// dataobjectproperty_readonly_set(PyObject *self, PyObject *val)
// {
//     ((dataobjectproperty_object*)self)->readonly = PyObject_IsTrue(val);
//     return 0;
// }

static PyGetSetDef dataobjectproperty_getsets[] = {
    {"index", (getter)dataobjectproperty_index, NULL, NULL},
//     {"readonly", (getter)dataobjectproperty_readonly, (setter)dataobjectproperty_readonly_set, NULL},
    {"readonly", (getter)dataobjectproperty_readonly, NULL, NULL},
    {0}
};

static PyTypeObject PyDataObjectProperty_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "recordclass._dataobject.dataobjectproperty", /*tp_name*/
    sizeof(dataobjectproperty_object), /*tp_basicsize*/
    0, /*tp_itemsize*/
    dataobjectproperty_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*reserved*/
    0, /*tp_repr*/
    0, /*tp_as_number*/
    0, /*tp_as_sequence*/
    0, /*tp_as_mapping*/
    0, /*tp_hash*/
    0, /*tp_call*/
    0, /*tp_str*/
    0, /*tp_getattro*/
    0, /*tp_setattro*/
    0, /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /*tp_flags*/
    0, /*tp_doc*/
    0, /*tp_traverse*/
    0, /*tp_clear*/
    0, /*tp_richcompare*/
    0, /*tp_weaklistoffset*/
    0, /*tp_iter*/
    0, /*tp_iternext*/
    dataobjectproperty_methods, /*tp_methods*/
    0, /*tp_members*/
    dataobjectproperty_getsets, /*tp_getset*/
    0, /*tp_base*/
    0, /*tp_dict*/
    dataobjectproperty_get, /*tp_descr_get*/
    dataobjectproperty_set, /*tp_descr_set*/
    0, /*tp_dictoffset*/
    0, /*tp_init*/
    0, /*tp_alloc*/
    dataobjectproperty_new, /*tp_new*/
    0, /*tp_free*/
    0, /*tp_is_gc*/
};


//////////////////// datatype ////////////////////////////////////////////

// static int _get_bool_value(PyObject *options, const char *name) {
//         PyObject* b;

//         b = PyMapping_GetItemString(options, name);
//         if (b && PyObject_IsTrue(b))
//             return 1;
//         else
//             return 0;
// }



//////////////////// module level functions //////////////////////////////

static PyObject*
_collection_protocol(PyObject *cls, PyObject *sequence, PyObject *mapping, PyObject *readonly, PyObject *mapping_only) {
    PyTypeObject *tp;
    PyTypeObject *tp_base;
    int sq, mp, ro, mo;

    tp = (PyTypeObject*)cls;
    sq = PyObject_IsTrue(sequence);
    mp = PyObject_IsTrue(mapping);
    ro = PyObject_IsTrue(readonly);
    mo = PyObject_IsTrue(mapping_only);

    tp_base = tp->tp_base;

    if ((tp_base != &PyDataObject_Type) && !PyType_IsSubtype(tp_base, &PyDataObject_Type)) {
        PyErr_SetString(PyExc_TypeError, "the type should be dataobject or it's subtype");
        return NULL;
    }

    copy_mapping_methods(tp->tp_as_mapping, tp_base->tp_as_mapping);
    copy_sequence_methods(tp->tp_as_sequence, tp_base->tp_as_sequence);

    if (!mo && sq) {
        if (ro) {
            copy_sequence_methods(tp->tp_as_sequence, &dataobject_as_sequence_ro);
            copy_mapping_methods(tp->tp_as_mapping, &dataobject_as_mapping_sq_ro);
        } else {
            copy_sequence_methods(tp->tp_as_sequence, &dataobject_as_sequence);
            copy_mapping_methods(tp->tp_as_mapping, &dataobject_as_mapping_sq);
        }
    }

    if (!mo && mp) {
        if (ro) {
            copy_mapping_methods(tp->tp_as_mapping, &dataobject_as_mapping_ro);
        } else {
            copy_mapping_methods(tp->tp_as_mapping, &dataobject_as_mapping);
        }
    }

    if (!mo && mp && sq) {
        if (ro) {
            copy_mapping_methods(tp->tp_as_mapping, &dataobject_as_mapping2_ro);
        } else {
            copy_mapping_methods(tp->tp_as_mapping, &dataobject_as_mapping2);
        }
    }

    if (mo) {
        if (ro) {
            copy_mapping_methods(tp->tp_as_mapping, &dataobject_as_mapping_only_ro);
        } else {
            copy_mapping_methods(tp->tp_as_mapping, &dataobject_as_mapping_only);
        }
    }

    Py_RETURN_NONE;
}

#ifndef PYPY_VERSION
static PyObject*
_set_hashable(PyObject *cls, PyObject *hashable) {
    PyTypeObject *tp = (PyTypeObject*)cls;
    int state = PyObject_IsTrue(hashable);

    PyObject *bases = tp->tp_bases;
    Py_ssize_t i, n_bases = Py_SIZE(bases);
    for (i=0; i<n_bases; i++) {
        PyTypeObject *base = (PyTypeObject*)PyTuple_GetItem(bases, i);
        if (base->tp_hash) {
            if (base->tp_hash == dataobject_hash) {
                tp->tp_hash = base->tp_hash;
                break;
            }
        }
    }

    if (state) {
        tp->tp_hash = dataobject_hash;
    }
    // else
    //     tp->tp_hash = NULL;

    Py_RETURN_NONE;
}
#endif

static PyObject*
_set_iterable(PyObject *cls, PyObject *iterable) {
    PyTypeObject *tp;
    const int state = PyObject_IsTrue(iterable);

    if (!state)
        Py_RETURN_NONE;

    tp = (PyTypeObject*)cls;

    if (!tp->tp_iter && state)
        tp->tp_iter = dataobject_iter;

    PyObject *bases = tp->tp_bases;
    Py_ssize_t i, n_bases = Py_SIZE(bases);
    for (i=0; i<n_bases; i++) {
        PyTypeObject *base = (PyTypeObject*)PyTuple_GetItem(bases, i);
        if (base->tp_iter) {
            if (base->tp_iter == dataobject_iter) {
                tp->tp_iter = base->tp_iter;
                Py_RETURN_NONE;
            }
        }
    }

    // if (tp->tp_iter && !state)
    //     tp->tp_iter = NULL;

    Py_RETURN_NONE;
}

static PyObject*
_set_dictoffset(PyObject *cls, PyObject *add_dict) {
    PyTypeObject *tp;
    int state;

    tp = (PyTypeObject*)cls;
    state = PyObject_IsTrue(add_dict);

    if (!PyObject_IsInstance(cls, (PyObject*)&PyType_Type)) {
        PyErr_SetString(PyExc_TypeError, "argument is not a subtype of the type");
        return NULL;
    }

    if (!tp->tp_dictoffset && state) {
        if (!tp->tp_weaklistoffset) {
            tp->tp_dictoffset = tp->tp_basicsize;
            tp->tp_basicsize += sizeof(PyObject*);
        } else {
            tp->tp_dictoffset = tp->tp_basicsize - sizeof(PyObject*);
            tp->tp_weaklistoffset = tp->tp_basicsize;
            tp->tp_basicsize += sizeof(PyObject*);
        }
    }

    Py_RETURN_NONE;
}

static PyObject*
_set_weaklistoffset(PyObject *cls, PyObject* add_weakref) {
    PyTypeObject *tp;
    int state;

    tp = (PyTypeObject*)cls;
    if (!PyObject_IsInstance(cls, (PyObject*)&PyType_Type)) {
        PyErr_SetString(PyExc_TypeError, "argument is not a subtype of the type");
        return NULL;
    }

    state = PyObject_IsTrue(add_weakref);

    if (!tp->tp_weaklistoffset && state) {
        if (!tp->tp_dictoffset) {
            tp->tp_weaklistoffset = tp->tp_basicsize;
            tp->tp_basicsize += sizeof(PyObject*);
        } else {
            tp->tp_weaklistoffset = tp->tp_basicsize;
            tp->tp_basicsize += sizeof(PyObject*);
        }
    }
//     if (tp->tp_weaklistoffset && !state) {
// //         PyErr_SetString(PyExc_TypeError, "we can only enable __weakref__");
// //         return NULL;
//         tp->tp_weaklistoffset = 0;
//         tp->tp_basicsize -= sizeof(PyObject*);
//         if (tp->tp_dictoffset)
//             tp->tp_dictoffset = tp->tp_basicsize;
//     }

    Py_RETURN_NONE;
}

PyDoc_STRVAR(_dataobject_type_init_doc,
"Initialize dataobject subclass");

static PyObject*
_dataobject_type_init(PyObject *module, PyObject *args) {
    PyObject *cls;

    PyTypeObject *tp;
    PyTypeObject *tp_base;
    int __init__, __new__;
    PyObject *fields, *dict;
    Py_ssize_t n_fields;
    int has_fields;

    if (Py_SIZE(args) != 1) {
        PyErr_SetString(PyExc_TypeError, "number of arguments != 1");
        return NULL;
    }

    cls = PyTuple_GET_ITEM(args, 0);
    tp = (PyTypeObject*)cls;
    tp_base = tp->tp_base;

    if (!PyType_IsSubtype(tp_base, &PyDataObject_Type)) {
        PyErr_SetString(PyExc_TypeError,
                        "common base class should be subclass of dataobject");
        return NULL;
    }

    dict = tp->tp_dict;

    fields = PyMapping_GetItemString(dict, "__fields__");
    if (!fields){
        PyErr_SetString(PyExc_TypeError, "__fields__ is missing");
        return NULL;
    }

    if (PyTuple_Check(fields)) {
        n_fields = PyTuple_GET_SIZE(fields);
        if (n_fields > 0)
            has_fields = 1;
        else
            has_fields = 0;
    } else {
        n_fields = PyNumber_AsSsize_t(fields, PyExc_IndexError);
        if (n_fields == -1 && PyErr_Occurred()) {
            Py_DECREF(fields);
            return NULL;
        }
        if (n_fields < 0) {
            PyErr_SetString(PyExc_TypeError, "number of fields should not be negative");
            return NULL;
        }
        has_fields = 0;
    }

    Py_DECREF(fields);

    tp->tp_basicsize = sizeof(PyObject) + n_fields * sizeof(PyObject*);
    tp->tp_itemsize = n_fields;

    tp->tp_dictoffset = tp_base->tp_dictoffset;
    tp->tp_weaklistoffset = tp_base->tp_weaklistoffset;

    tp->tp_alloc = dataobject_alloc;

    __new__ = PyMapping_HasKeyString(dict, "__new__");

    if(!__new__ || !has_fields)
        tp->tp_new = dataobject_new;

    tp->tp_dealloc = dataobject_dealloc;
    tp->tp_free = PyObject_Del;

    __init__ = PyMapping_HasKeyString(dict, "__init__");
    if (!__init__)
        tp->tp_init = tp_base->tp_init;

    tp->tp_flags |= Py_TPFLAGS_HEAPTYPE;

    if (tp->tp_flags & Py_TPFLAGS_HAVE_GC)
        tp->tp_flags &= ~Py_TPFLAGS_HAVE_GC;

#ifndef PYPY_VERSION
    if (tp_base->tp_hash)
        tp->tp_hash = tp_base->tp_hash;
#endif

    if (tp_base->tp_iter)
        tp->tp_iter = tp_base->tp_iter;

    tp->tp_traverse = NULL;
    tp->tp_clear = NULL;
    tp->tp_is_gc = NULL;

#if PY_VERSION_HEX == 0x03080000
    tp->tp_vectorcall_offset = 0
#endif

// #if PY_VERSION_HEX >= 0x03080000
//     if (tp->tp_flags & Py_TPFLAGS_METHOD_DESCRIPTOR)
//         tp->tp_flags &= ~Py_TPFLAGS_METHOD_DESCRIPTOR;
// #endif

    Py_RETURN_NONE;
}

static PyObject *
_enable_gc(PyObject *cls)
{
    PyTypeObject *type;

    if (!PyObject_IsInstance(cls, (PyObject*)&PyType_Type)) {
        PyErr_SetString(PyExc_TypeError, "Argument have to be an instance of type");
        return NULL;
    }

    type = (PyTypeObject*)cls;
    type->tp_flags |= Py_TPFLAGS_HAVE_GC;
    type->tp_traverse = dataobject_traverse;
    type->tp_clear = dataobject_clear;

    type->tp_dealloc = dataobject_dealloc_gc;
    type->tp_alloc = dataobject_alloc_gc;
    type->tp_free = PyObject_GC_Del;

//     PyType_Modified(type);

    Py_RETURN_NONE;
}

static PyObject *
_set_deep_dealloc(PyObject *cls, PyObject *state)
{
    PyTypeObject *type;
    int have_gc;
    int  is_deep = PyObject_IsTrue(state);

    if (!PyObject_IsInstance(cls, (PyObject*)&PyType_Type)) {
        PyErr_SetString(PyExc_TypeError, "Argument have to be an instance of a type");
        return NULL;
    }

    type = (PyTypeObject*)cls;
    have_gc = type->tp_flags & Py_TPFLAGS_HAVE_GC;

    if (!have_gc && is_deep) {
        type->tp_finalize = dataobject_finalize;
    }

//     PyType_Modified(type);

    Py_RETURN_NONE;
}


static PyObject *
_astuple(PyObject *op)
{
    const Py_ssize_t n = PyDataObject_LEN(op);
    Py_ssize_t i;

    PyObject *tpl = PyTuple_New(n);
    for (i=0; i<n; i++) {
        PyObject *v = PyDataObject_GET_ITEM(op, i);
        Py_INCREF(v);
        PyTuple_SetItem(tpl, i, v);
    }
    return (PyObject*)tpl;
}

static PyObject *
_asdict(PyObject *op)
{
    Py_ssize_t i;
    PyObject *fn, *v;

    PyObject *fields = PyObject_GetAttrString((PyObject*)py_type(op), "__fields__");

    if (!fields)
        return NULL;

    if (!PyObject_IsInstance(fields, (PyObject*)&PyTuple_Type)) {
        PyErr_SetString(PyExc_TypeError, "__fields__ should be a tuple");
        return NULL;
    }

    const Py_ssize_t n = Py_SIZE(fields);
    PyObject *dict = PyDict_New();

    if (n == 0) {
        Py_DECREF(fields);
        return dict;
    }

    for (i=0; i<n; i++) {
        fn = PyTuple_GetItem(fields, i);
        Py_INCREF(fn);
        v = PyDataObject_GET_ITEM(op, i);
        Py_INCREF(v);
        PyDict_SetItem(dict, fn, v);
    }

    Py_DECREF(fields);
    return dict;
}

PyDoc_STRVAR(asdict_doc,
"Convert object to dict");

static PyObject *
asdict(PyObject *module, PyObject *args)
{
    PyObject *op;
    PyTypeObject *type;

    op = PyTuple_GET_ITEM(args, 0);
    type = py_type(op);

    if (type != &PyDataObject_Type &&
        !PyType_IsSubtype(type, &PyDataObject_Type)) {
            PyErr_SetString(PyExc_TypeError, "1st argument is not subclass of dataobject");
            return NULL;
    }

    return _asdict(op);
}

#ifdef PYPY_VERSION
PyDoc_STRVAR(hash_func_doc,
"Get hash value of the dataobject");

static PyObject *
_hash_func(PyObject *module, PyObject *args)
{
    PyObject *op;
    PyTypeObject *type;

    op = PyTuple_GetItem(args, 0);
    type = py_type(op);

    if (type != &PyDataObject_Type &&
        !PyType_IsSubtype(type, &PyDataObject_Type)) {
            PyErr_SetString(PyExc_TypeError, "1st argument is not subclass of dataobject");
            return NULL;
    }

    return PyLong_FromSsize_t(dataobject_hash(op));
}

PyDoc_STRVAR(iter_func_doc,
"Get hash value of the dataobject");

static PyObject *
_iter_func(PyObject *module, PyObject *args)
{
    PyObject *op;
    PyTypeObject *type;

    op = PyTuple_GetItem(args, 0);
    type = py_type(op);

    if (type != &PyDataObject_Type &&
        !PyType_IsSubtype(type, &PyDataObject_Type)) {
            PyErr_SetString(PyExc_TypeError, "1st argument is not subclass of dataobject");
            return NULL;
    }

    return dataobject_iter(op);
}
#endif

PyDoc_STRVAR(astuple_doc,
"Convert object to a tuple");

static PyObject *
astuple(PyObject *module, PyObject *args)
{
    PyObject *op;
    PyTypeObject *type;

    op = PyTuple_GET_ITEM(args, 0);
    type = py_type(op);

    PyTypeObject* tp_base = type->tp_base;

    if ((tp_base != &PyDataObject_Type) && !PyType_IsSubtype(tp_base, &PyDataObject_Type)) {
            PyErr_SetString(PyExc_TypeError, "1st argument is not subclass of dataobject");
            return NULL;
    }

    return _astuple(op);
}

PyDoc_STRVAR(dataobject_make_doc,
"Create a new dataobject-based object");

static PyObject *
dataobject_make(PyObject *module, PyObject *type_args, PyObject *kw)
{
    PyObject *args0, *args;

    const Py_ssize_t n = Py_SIZE(type_args);
    if (n >= 1) {
        args0 = PyTuple_GET_ITEM(type_args, 1);
        if (py_type(args0) == &PyTuple_Type) {
            args = args0;
            Py_INCREF(args);
        } else {
            args = PySequence_Tuple(args0);
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "nargs < 1");
        return NULL;
    }

    PyTypeObject *type = (PyTypeObject*)PyTuple_GET_ITEM(type_args, 0);
    Py_INCREF(type);

    PyObject *ret =  dataobject_new(type, args, kw);

    Py_DECREF(args);
    Py_DECREF(type);

    return ret;
}

PyDoc_STRVAR(dataobject_new_doc,
"Create a new dataobject-based object");

static PyObject *
dataobject_new_instance(PyObject *module, PyObject *type_args, PyObject *kw)
{
    PyTupleObject *tmp = (PyTupleObject *)type_args;

    const Py_ssize_t n = Py_SIZE(tmp);
    if (n < 1) {
        PyErr_SetString(PyExc_TypeError, "nargs < 1");
        return NULL;
    }

    PyObject *ret =  dataobject_new_vc((PyTypeObject*)tmp->ob_item[0], (PyObject * const*)&tmp->ob_item[1], n-1, kw);

    return ret;
}

PyDoc_STRVAR(dataobject_clone_doc,
"Clone dataobject-based object");

static PyObject *
dataobject_clone(PyObject *module, PyObject *args0, PyObject *kw)
{
    PyObject *args;

    PyObject *ob = PyTuple_GET_ITEM(args0, 0);
    PyTypeObject *type = py_type(ob);
    Py_INCREF(type);

    args = _astuple(ob);

    PyObject *ret =  dataobject_new(type, args, kw);

    Py_DECREF(args);
    Py_DECREF(type);

    return ret;
}

static int
_dataobject_update(PyObject *op, PyObject *kwds)
{
        PyObject *iter, *key, *val;

        iter = PyObject_GetIter(kwds);
        while ((key = PyIter_Next(iter))) {
            val = PyObject_GetItem(kwds, key);
            if (!val) {
                PyErr_SetString(PyExc_KeyError, "Invalid kwarg");
                Py_DECREF(key);
                Py_DECREF(iter);
                return -1;
            }
            if (PyObject_SetAttr(op, key, val) < 0) {
                PyErr_SetString(PyExc_AttributeError, "Set attribute failed");
                Py_DECREF(val);
                Py_DECREF(key);
                Py_DECREF(iter);
                return -1;
            }
            Py_DECREF(val);
            Py_DECREF(key);
        }
        Py_DECREF(iter);
    return 0;
}

PyDoc_STRVAR(dataobject_update_doc,
"Update dataobject-based object");

static PyObject*
dataobject_update(PyObject *module, PyObject *args, PyObject *kw)
{
    if (args && PySequence_Size(args) != 1) {
        PyErr_SetString(PyExc_TypeError, "Only one argument is allowed");
        return NULL;
    }

    PyObject *op = PyTuple_GET_ITEM(args, 0);

    if (_dataobject_update(op, kw) < 0)
        return NULL;

    Py_RETURN_NONE;
}

PyDoc_STRVAR(clsconfig_doc,
"Configure some class aspects");

static PyObject *
clsconfig(PyObject *module, PyObject *args, PyObject *kw) {
    PyObject *cls = PyTuple_GET_ITEM(args, 0);
    PyObject *sequence = PyMapping_GetItemString(kw, "sequence");
    PyObject *mapping = PyMapping_GetItemString(kw, "mapping");
    PyObject *readonly = PyMapping_GetItemString(kw, "readonly");
    PyObject *use_dict = PyMapping_GetItemString(kw, "use_dict");
    PyObject *use_weakref = PyMapping_GetItemString(kw, "use_weakref");
    PyObject *iterable = PyMapping_GetItemString(kw, "iterable");
    PyObject *gc = PyMapping_GetItemString(kw, "gc");
    PyObject *set_dd = PyMapping_GetItemString(kw, "deep_dealloc");
    PyObject *mapping_only = PyMapping_GetItemString(kw, "mapping_only");

    _set_dictoffset(cls, use_dict);
    _set_weaklistoffset(cls, use_weakref);

    _collection_protocol(cls, sequence, mapping, readonly, mapping_only);
    _set_iterable(cls, iterable);

#ifndef PYPY_VERSION
    PyObject *hashable = PyMapping_GetItemString(kw, "hashable");
    _set_hashable(cls, hashable);
    Py_XDECREF(hashable);
#endif

    if (PyObject_IsTrue(gc))
        _enable_gc(cls);

    _set_deep_dealloc(cls, set_dd);

    PyTypeObject *tp = (PyTypeObject*)cls;
    PyType_Modified(tp);
    tp->tp_flags &= ~Py_TPFLAGS_READYING;
    if(PyType_Ready(tp) < 0)
        printf("Ready failed\n");

    Py_XDECREF(sequence);
    Py_XDECREF(mapping);
    Py_XDECREF(readonly);
    Py_XDECREF(use_dict);
    Py_XDECREF(use_weakref);
    Py_XDECREF(iterable);
    Py_XDECREF(gc);
    Py_XDECREF(set_dd);
    Py_XDECREF(mapping_only);

    Py_RETURN_NONE;
}

static void
__fix_type(PyObject *tp, PyTypeObject *meta) {
    PyObject *val;

    if (py_type(tp) != meta) {
        val = (PyObject*)py_type(tp);
        if (val)
            Py_DECREF(val);
        py_type(tp) = meta;
        Py_INCREF(meta);
        // PyType_Modified((PyTypeObject*)tp);
    }
}

//////////////////////////////////////////////////

PyDoc_STRVAR(dataobjectmodule_doc,
"dataobject module provide `dataobject` class.");

static PyMethodDef dataobjectmodule_methods[] = {
    {"asdict", asdict, METH_VARARGS, asdict_doc},
    {"astuple", astuple, METH_VARARGS, astuple_doc},
    {"new", (PyCFunction)dataobject_new_instance, METH_VARARGS | METH_KEYWORDS, dataobject_new_doc},
    {"make", (PyCFunction)dataobject_make, METH_VARARGS | METH_KEYWORDS, dataobject_make_doc},
#ifdef PYPY_VERSION
    {"_hash_func", (PyCFunction)_hash_func, METH_VARARGS, hash_func_doc},
    {"_iter_func", (PyCFunction)_iter_func, METH_VARARGS, iter_func_doc},
#endif
    {"clone", (PyCFunction)dataobject_clone, METH_VARARGS | METH_KEYWORDS, dataobject_clone_doc},
    {"update", (PyCFunction)dataobject_update, METH_VARARGS | METH_KEYWORDS, dataobject_update_doc},
    {"_dataobject_type_init", _dataobject_type_init, METH_VARARGS, _dataobject_type_init_doc},
    {"_clsconfig", (PyCFunction)clsconfig, METH_VARARGS | METH_KEYWORDS, clsconfig_doc},
    {0, 0, 0, 0}
};


// #if PY_MAJOR_VERSION >= 3
static struct PyModuleDef dataobjectmodule = {
    PyModuleDef_HEAD_INIT,
    "recordclass._dataobject",
    dataobjectmodule_doc,
    -1,
    dataobjectmodule_methods,
    NULL,
    NULL,
    NULL,
    NULL
};
// #endif

PyMODINIT_FUNC
PyInit__dataobject(void)
{
    PyObject *m;

#ifndef PYPY_VERSION
    m = PyState_FindModule(&dataobjectmodule);
    if (m) {
        Py_INCREF(m);
        return m;
    }
#endif

    m = PyModule_Create(&dataobjectmodule);
    if (m == NULL)
        return NULL;

    datatype = (PyTypeObject*)_PyObject_GetObject("recordclass", "datatype");
    __fix_type((PyObject*)&PyDataObject_Type, datatype);
    Py_DECREF(datatype);

    // PyDataObject_Type.tp_base = &PyBaseObject_Type;
    // Py_INCREF(&PyBaseObject_Type);
// #if PY_VERSION_HEX == 0x03080000
//     PyDataObject_Type.tp_vectorcall_offset = 0
// #endif
    if (PyType_Ready(&PyDataObject_Type) < 0)
        Py_FatalError("Can't initialize dataobject type");

    if (PyType_Ready(&PyDataObjectIter_Type) < 0)
        Py_FatalError("Can't initialize dataobjectiter type");

    if (PyType_Ready(&PyDataObjectProperty_Type) < 0)
        Py_FatalError("Can't initialize dataobjectproperty type");

    Py_INCREF(&PyDataObject_Type);
    PyModule_AddObject(m, "dataobject", (PyObject *)&PyDataObject_Type);

    Py_INCREF(&PyDataObjectIter_Type);
    PyModule_AddObject(m, "dataobjectiter", (PyObject *)&PyDataObjectIter_Type);

    Py_INCREF(&PyDataObjectProperty_Type);
    PyModule_AddObject(m, "dataobjectproperty", (PyObject *)&PyDataObjectProperty_Type);

    fields_dict_name = PyUnicode_FromString("__fields_dict__");
    if (fields_dict_name == NULL)
        return NULL;
    // Py_INCREF(fields_dict_name);
    // fields_dict_hash = PyObject_Hash(fields_dict_name);

    __fields__name = PyUnicode_FromString("__fields__");
    if (__fields__name == NULL)
        return NULL;

    __dict__name = PyUnicode_FromString("__dict__");
    if (__dict__name == NULL)
        return NULL;

    __weakref__name = PyUnicode_FromString("__weakref__");
    if (__weakref__name == NULL)
        return NULL;

    __defaults__name = PyUnicode_FromString("__defaults__");
    if (__defaults__name == NULL)
        return NULL;

//     dataobject_as_mapping.mp_subscript = PyDataObject_Type.tp_getattro;
//     dataobject_as_mapping.mp_ass_subscript = PyDataObject_Type.tp_setattro;

//     dataobject_as_mapping_ro.mp_subscript = PyDataObject_Type.tp_getattro;

    return m;
}
