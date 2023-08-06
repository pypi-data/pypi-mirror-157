#include "MCSStruct.h"

typedef struct
{
    char *ptr;
    size_t len;
} STRPTR;

static const STRPTR FindEventId(
    const EventStruct const event,
    const BEEventStruct *const beevent_struct,
    const CCFEventStruct *const ccfevent_struct,
    const MODEventStruct *const modevent_struct)
{

    STRPTR str;

    switch (event.EventType)
    {
    case BASIC_EVENT:
        str.ptr = (char*)beevent_struct[event.Index].Name;
        break;
    case CCF_EVENT:
        str.ptr = (char*)ccfevent_struct[event.Index].Name;
        break;
    case MOD_EVENT:
        str.ptr = (char*)modevent_struct[event.Index].Name;
        break;
    default:
        str.ptr = NULL;
        return str;
    }

    str.len = trim(str.ptr, MAX_ID_LEN);
    return str;
}

static PyObject *expand_module(
    PyObject *set,
    const EventStruct const module,
    const EventStruct *const event_struct,
    const MODEventStruct *const modevent_struct,
    const int32_t *const modulevents,
    const BEEventStruct *const beevent_struct,
    const CCFEventStruct *const ccfevent_struct,
    const char *encoding)
{
    const int32_t index = module.Index;
    int32_t num = modevent_struct[index - 1].LastChild + 1;
    int32_t iLastChild = modevent_struct[index].LastChild;
    PyObject *row_obj = PyTuple_New(iLastChild - num + 1);
    for (uint32_t i = num; i <= iLastChild; i++)
    {
        int32_t num2 = modulevents[i];
        EventStruct event = event_struct[abs(num2)];
        if (event.EventType == MOD_EVENT)
        {
            expand_module(
                    set,
                    event,
                    event_struct,
                    modevent_struct,
                    modulevents,
                    beevent_struct,
                    ccfevent_struct,
                    encoding);
        }
        else
        {
            STRPTR name = FindEventId(event,
                                      beevent_struct, ccfevent_struct, modevent_struct);
            if (name.ptr == NULL)
            {
                PyErr_Format(PyExc_RuntimeError,
                             "Can't read event, undefine event type '%u' in mod. event (%u)",
                             event.EventType, i);
                Py_DECREF(row_obj);
                return NULL;
            }
            PyObject *name_obj;

            // Test on non negative event
            if (abs(num2) + num2 > 0)
            {
                name_obj = PyUnicode_Decode(name.ptr, name.len, encoding, NULL);
            }
            else
            {
                char neg_name[MAX_ID_LEN + 1];
                neg_name[0] = '-';
                strncpy(&neg_name[1], name.ptr, name.len);
                name_obj = PyUnicode_Decode(neg_name, name.len + 1, encoding, NULL);
            }
            PySet_Add(set, name_obj);
        }
    }
    return set;
}

PyObject *create_mcs(
    const MCSStruct *const mcs_struct,
    const int32_t *const mcsevent_struct,
    const EventStruct *const event_struct,
    const BEEventStruct *const beevent_struct,
    const CCFEventStruct *const ccfevent_struct,
    const MODEventStruct *const modevent_struct,
    const int32_t *const modulevents,
    const char *encoding,
    const uint_fast32_t start,
    const uint_fast32_t end,
    const int with_header,
    const int mod_expand)
{
    PyObject *col_obj = PyTuple_New(end - start + with_header);
    uint_fast8_t max_mcs_len = 1;
    for (uint_fast32_t row = start; row < end; row++)
    {
        MCSStruct mcs = mcs_struct[row];
        const uint_fast32_t column_count = mcs.LastEvent - mcs.FirstEvent + 1;
        max_mcs_len = MAX(max_mcs_len, column_count);
        PyObject *row_obj = PyTuple_New(column_count + 1);

        PyTuple_SET_ITEM(row_obj, 0, Py_BuildValue("d", mcs.Mean));

        for (uint_fast32_t column = 0; column < column_count; column++)
        {
            // Address to event struct. If negative then not event
            const int32_t e9 = mcsevent_struct[mcs.FirstEvent + column];
            EventStruct event = event_struct[abs(e9)];

            const STRPTR name = FindEventId(event,
                                            beevent_struct, ccfevent_struct, modevent_struct);
            if (name.ptr == NULL)
            {
                PyErr_Format(PyExc_RuntimeError,
                             "Can't read event, undefine event type '%u' in (%u, %u)",
                             event.EventType, row, column + 1);
                Py_DECREF(row_obj);
                Py_DECREF(col_obj);
                return NULL;
            }

            PyObject *name_obj;
            if ((mod_expand == 1) && (event.EventType == MOD_EVENT))
            {
                name_obj = expand_module(
                    PySet_New(NULL),
                    event,
                    event_struct,
                    modevent_struct,
                    modulevents,
                    beevent_struct,
                    ccfevent_struct,
                    encoding);
            }
            else
            {
                // Test on non negative event
                if (abs(e9) + e9 > 0)
                {
                    name_obj = PyUnicode_Decode(name.ptr, name.len, encoding, NULL);
                }
                else
                {
                    char neg_name[MAX_ID_LEN + 1];
                    neg_name[0] = '-';
                    strncpy(&neg_name[1], name.ptr, name.len);
                    name_obj = PyUnicode_Decode(neg_name, name.len + 1, encoding, NULL);
                }
            }

            PyTuple_SET_ITEM(row_obj, column + 1, name_obj);
        }

        PyTuple_SET_ITEM(col_obj, row + with_header - start, row_obj);
    }
    if (with_header)
    {
        PyObject *header_obj = PyTuple_New(max_mcs_len + 1);
        PyTuple_SET_ITEM(header_obj, 0, Py_BuildValue("s", "Mean"));
        for (uint_fast8_t i = 1; i < max_mcs_len + 1; i++)
        {
            char s[10];
            snprintf(s, sizeof(s), "Event %u", i);
            PyTuple_SET_ITEM(header_obj, i, Py_BuildValue("s", s));
        }
        PyTuple_SET_ITEM(col_obj, 0, header_obj);
    }

    return col_obj;
}