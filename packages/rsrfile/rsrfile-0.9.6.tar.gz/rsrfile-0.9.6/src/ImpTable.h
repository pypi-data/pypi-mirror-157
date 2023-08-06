#ifndef IMPTABLE
#define IMPTABLE

#define PY_SSIZE_T_CLEAN
#include <Python.h>
//#include <string.h>
#include "structures.h"
#include "common.h"

PyObject *create_BEImportanceTable(
    const ImpStruct *const imp_struct,
    const EventStruct *const event_struct,
    const BEEventStruct *const beevent_struct,
    const CCFEventStruct *const ccfevent_struct,
    const MODEventStruct *const modevent_struct,
    const uint_fast32_t count,
    const char *encoding);

PyObject *create_ParamImportanceTable(
    const ImpStruct *const imp_struct,
    const ParStruct *const param_struct,
    const uint_fast32_t count,
    const char *encoding);

PyObject* ccfg_importance_table(
    const ImpStruct *const imp_struct,
    const CCFGroupStruct *const ccfg_struct,
    const uint_fast32_t count,
    const char *encoding);

PyObject* attr_importance_table(
    const ImpStruct *const imp_struct,
    const AttributeStruct *const attr_struct,
    const uint_fast32_t count,
    const char *encoding);

#endif /* IMPTABLE */
