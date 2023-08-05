/*
    WinAPY - Windows API wrapper in C developed for Python.
    Copyright (c) 2022 Itzsten
*/

#include "Python.h"
#include <Windows.h>
#include <stdio.h>
#include <mmeapi.h>

#pragma comment(lib, "Winmm.lib")

#define MIDIHDR_TUPLE_TO_STRUCT_FAILED(hdr) (hdr.reserved == -69420)

#if PY_MAJOR_VERSION >= 3
#define PyString_ToCharArr PyUnicode_AsUTF8
#else
#define PyString_ToCharArr PyString_AsString
#endif

BOOL WINAPI RaiseExceptionCheck(BOOL bSuccess) {
    if (GetLastError() && (!bSuccess)) {
        PyErr_SetFromWindowsErr(GetLastError());
        return TRUE;
    }
    return FALSE;
}

BOOL WINAPI ErrorCheckMME(MMRESULT ret) {
    if (!ret) {
        return FALSE;
    }
    CHAR err[512];
    CHAR res[520];
    if (!waveOutGetErrorTextA(ret, err, 512)) {
        sprintf_s(res, 520, "[MMSYSERR %u] %s", ret, err);
        PyErr_SetString(PyExc_SystemError, res);
    }
    return TRUE;
}

MIDIHDR MidiTupleToStruct(PyObject* ob) {
    MIDIHDR res;
    res.reserved = -69420;

    if (!PyTuple_Check(ob)) {
        PyErr_SetString(PyExc_TypeError, "excepted tuple object");
        return res;
    }
    if (PyTuple_Size(ob) != 7) {
        PyErr_SetString(PyExc_ValueError, "excepted tuple returned from midiOutPrepareHeader of length 7");
        return res;
    }
    PyObject* bArr = PyTuple_GET_ITEM(ob, 0);
    if (!PyByteArray_Check(bArr)) {
        PyErr_SetString(PyExc_TypeError, "first element in midi header tuple must be a bytearray object");
        return res;
    }

    res.lpData = bArr;
    res.dwBufferLength = PyLong_AsUnsignedLong( PyTuple_GET_ITEM(ob, 1) );
    res.dwBytesRecorded =PyLong_AsUnsignedLong( PyTuple_GET_ITEM(ob, 2) );
    res.dwUser =     PyLong_AsUnsignedLongLong( PyTuple_GET_ITEM(ob, 3) );
    res.dwFlags =        PyLong_AsUnsignedLong( PyTuple_GET_ITEM(ob, 4) );
    res.dwOffset =       PyLong_AsUnsignedLong( PyTuple_GET_ITEM(ob, 6) );
    res.reserved =   PyLong_AsUnsignedLongLong( PyTuple_GET_ITEM(ob, 5) );

    return res;
}

static PyObject* PywaveOutOpen(PyObject* self, PyObject* args) {
    //@description@ Opens the given waveform-audio output device for playback. The return value specifies a handle identifying the open waveform-audio output device.@@HWAVEOUT
    //@args@ deviceID|int|Identifier of the waveform-audio output device to open. It can be either a device identifier or a handle of an open waveform-audio input device. You can also use the following flag instead of a device identifier;<br><b>WAVE_MAPPER</b> - The function selects a waveform-audio output device capable of playing the given format.@@wfx|tuple|A tuple of 6 integers representing the values below;<br><ul><li><b>wFormatTag</b><br>Waveform-audio format type. Format tags are registered with Microsoft Corporation for many compression algorithms. For one- or two-channel PCM data, this value should be WAVE_FORMAT_PCM.<br></li><li><b>nChannels</b><br>Number of channels in the waveform-audio data. Monaural data uses one channel and stereo data uses two channels.<br></li><li><b>nSamplesPerSec</b><br>Sample rate, in samples per second (hertz). If wFormatTag is WAVE_FORMAT_PCM, then common values for nSamplesPerSec are 8.0 kHz, 11.025 kHz, 22.05 kHz, and 44.1 kHz. For non-PCM formats, this member must be computed according to the manufacturer's specification of the format tag.<br></li><li><b>nAvgBytesPerSec</b><br>Required average data-transfer rate, in bytes per second, for the format tag. If wFormatTag is WAVE_FORMAT_PCM, nAvgBytesPerSec should be equal to the product of nSamplesPerSec and nBlockAlign. For non-PCM formats, this member must be computed according to the manufacturer's specification of the format tag.<br></li><li><b>nBlockAlign</b><br>Block alignment, in bytes. The block alignment is the minimum atomic unit of data for the wFormatTag format type. If wFormatTag is WAVE_FORMAT_PCM or WAVE_FORMAT_EXTENSIBLE, nBlockAlign must be equal to the product of nChannels and wBitsPerSample divided by 8 (bits per byte). For non-PCM formats, this member must be computed according to the manufacturer's specification of the format tag.<br><br>Software must process a multiple of nBlockAlign bytes of data at a time. Data written to and read from a device must always start at the beginning of a block. For example, it is illegal to start playback of PCM data in the middle of a sample (that is, on a non-block-aligned boundary).<br></li><li><b>wBitsPerSample</b><br>Bits per sample for the wFormatTag format type. If wFormatTag is WAVE_FORMAT_PCM, then wBitsPerSample should be equal to 8 or 16. For non-PCM formats, this member must be set according to the manufacturer's specification of the format tag. If wFormatTag is WAVE_FORMAT_EXTENSIBLE, this value can be any integer multiple of 8 and represents the container size, not necessarily the sample size; for example, a 20-bit sample size is in a 24-bit container. Some compression schemes cannot define a value for wBitsPerSample, so this member can be 0.<br></li></ul>@@callback|int|Specifies the callback mechanism, or None.@@instance|int|User-instance data passed to the callback mechanism. This parameter is not used with the window callback mechanism.@@fOpen|int|<ul><li><b>CALLBACK_EVENT</b><br>The dwCallback parameter is an event handle.<br></li><li><b>CALLBACK_NULL</b><br> No callback mechanism. This is the default setting.<br></li><li><b>CALLBACK_THREAD</b><br> The dwCallback parameter is a thread identifier.<br></li><li><b>CALLBACK_WINDOW</b><br> The dwCallback parameter is a window handle.<br></li><li><b>WAVE_ALLOWSYNC</b><br> If this flag is specified, a synchronous waveform-audio device can be opened. If this flag is not specified while opening a synchronous driver, the device will fail to open.<br></li><li><b>WAVE_MAPPED_DEFAULT_COMMUNICATION_DEVICE</b><br> If this flag is specified and the uDeviceID parameter is WAVE_MAPPER, the function opens the default communication device. This flag applies only when uDeviceID equals WAVE_MAPPER. (Requires Windows 7)<br></li><li><b>WAVE_FORMAT_DIRECT</b><br> If this flag is specified, the ACM driver does not perform conversions on the audio data.<br></li><li><b>WAVE_FORMAT_QUERY</b><br> If this flag is specified, waveOutOpen queries the device to determine if it supports the given format, but the device is not actually opened.<br></li><li><b>WAVE_MAPPED</b><br> If this flag is specified, the uDeviceID parameter specifies a waveform-audio device to be mapped to by the wave mapper.<br></li></ul>
    PyObject* obOut;
    UINT deviceId;
    WAVEFORMATEX wFormat;
    DWORD_PTR dwCallback = 0, dwInstance = 0;
    DWORD fdwOpen = CALLBACK_NULL;
    HWAVEOUT hOut = 0;
    PyObject* pyPe = Py_None;
    
    if (!PyArg_ParseTuple(args, "k(HHkkHH)|OKk",
        &deviceId,
        &wFormat.wFormatTag, &wFormat.nChannels, &wFormat.nSamplesPerSec,
        &wFormat.nAvgBytesPerSec, &wFormat.nBlockAlign, &wFormat.wBitsPerSample,
        &pyPe,
        &dwInstance,
        &fdwOpen
    )) return NULL;

    if (pyPe != Py_None) {
        dwCallback = PyLong_AsUnsignedLongLong(pyPe);
    }
    
    MMRESULT res = waveOutOpen(&hOut, deviceId, &wFormat, dwCallback, dwInstance, fdwOpen);
    
    if (ErrorCheckMME(res)) return NULL;
    return Py_BuildValue("L", hOut);
}

static PyObject* PywaveOutPrepareHeader(PyObject* self, PyObject* args) {
    //@description@ The waveOutPrepareHeader function prepares a waveform-audio data block for playback. The return value should be used as the new wave header, as it is prepared for playback.@@tuple
    //@args@ hwo|HWAVEOUT|Handle to the waveform-audio output device.@@hdr|tuple|Tuple that identifies the data block to be prepared. Must contain the followings values;<br><ul><li>The data block to be prepared, as a <b>bytearray</b> object.</li><li>When the header is used in input, specifies how much data is in the buffer. If it is not used in input, set this value to 0.</li><li>User data, or 0.</li><li>A bitwise OR of zero of more flags.</li><li>Number of times to play the loop. This member is used only with output buffers. Zero if unused</li></ul>
    HWAVEOUT hwo;
    WAVEHDR hdr;
    UINT cbwh = sizeof(WAVEHDR);
    PyObject* obData;

    if (!PyArg_ParseTuple(args, "L(OkKkk)",
        &hwo,
        &obData,
        &hdr.dwBytesRecorded,
        &hdr.dwUser,
        &hdr.dwFlags,
        &hdr.dwLoops
    )) return NULL;

    if (!PyByteArray_Check(obData)) {
        PyErr_SetString(PyExc_TypeError, "argument 2: index 1: Excepted bytes type object");
        return NULL;
    }
    
    LONGLONG length = PyByteArray_Size(obData);

    hdr.dwBufferLength = length;
    hdr.lpData = PyByteArray_AsString(obData);
    hdr.lpNext = 0;
    hdr.reserved = 0;

    if (hdr.lpData == NULL) {
        PyErr_SetString(PyExc_TypeError, "Could not convert bytearray to char pointer.");
        return NULL;
    }

    MMRESULT res = waveOutPrepareHeader(hwo, &hdr, cbwh);

    if (ErrorCheckMME(res)) return NULL;
    return Py_BuildValue("(OkKkk)", 
        PyByteArray_FromStringAndSize(hdr.lpData, length),
        hdr.dwBytesRecorded,
        hdr.dwUser,
        hdr.dwFlags,
        hdr.dwLoops);
}

static PyObject* PywaveOutClose(PyObject* self, PyObject* args) {
    //@description@ Closes and frees memory from the specified waveform-audio output device.@@bool
    //@args@ hwo|HWAVEOUT|Handle to the waveform-audio output device.
    HWAVEOUT hwo;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutClose(hwo)))   return NULL;
    return Py_True;
}

static PyObject* PywaveOutUnprepareHeader(PyObject* self, PyObject* args) {
    //@description@ Frees memory from the specified header and waveform-audio output device.@@bool
    //@args@ hwo|HWAVEOUT|Handle to the waveform-audio output device.@@hdr|tuple|The header to be freen
    HWAVEOUT hwo;
    WAVEHDR hdr;
    UINT cbwh = sizeof(WAVEHDR);
    PyObject* obData;

    if (!PyArg_ParseTuple(args, "L(OkKkk)",
        &hwo,
        &obData,
        &hdr.dwBytesRecorded,
        &hdr.dwUser,
        &hdr.dwFlags,
        &hdr.dwLoops
    )) return NULL;

    if (!PyByteArray_Check(obData)) {
        PyErr_SetString(PyExc_TypeError, "argument 2: index 1: Excepted bytes type object");
        return NULL;
    }

    LONGLONG length = PyByteArray_Size(obData);

    hdr.dwBufferLength = length;
    hdr.lpData = PyByteArray_AsString(obData);
    hdr.lpNext = 0;
    hdr.reserved = 0;

    if (hdr.lpData == NULL) {
        PyErr_SetString(PyExc_TypeError, "Could not convert bytearray to char pointer.");
        return NULL;
    }
    MMRESULT res = waveOutUnprepareHeader(hwo, &hdr, cbwh);

    if (ErrorCheckMME(res)) return NULL;
    return Py_True;
}

static PyObject* PywaveOutWrite(PyObject* self, PyObject* args) {
    //@description@ Sends a data block to the given waveform-audio output device.@@bool
    //@args@ hwo|HWAVEOUT|Handle to the waveform-audio output device.@@hdr|tuple|The header containing the data block to be sent. For more information, please look under the waveOutPrepareHeader function.
    HWAVEOUT hwo;
    WAVEHDR hdr;
    UINT cbwh = sizeof(WAVEHDR);
    PyObject* obData;

    if (!PyArg_ParseTuple(args, "L(OkKkk)",
        &hwo,
        &obData,
        &hdr.dwBytesRecorded,
        &hdr.dwUser,
        &hdr.dwFlags,
        &hdr.dwLoops
    )) return NULL;

    if (!PyByteArray_Check(obData)) {
        PyErr_SetString(PyExc_TypeError, "argument 2: index 1: Excepted bytes type object");
        return NULL;
    }

    LONGLONG length = PyByteArray_Size(obData);

    hdr.dwBufferLength = length;
    hdr.lpData = PyByteArray_AsString(obData);
    hdr.lpNext = 0;
    hdr.reserved = 0;

    if (hdr.lpData == NULL) {
        PyErr_SetString(PyExc_TypeError, "Could not convert bytearray to char pointer.");
        return NULL;
    }

    MMRESULT res = waveOutWrite(hwo, &hdr, cbwh);

    if (ErrorCheckMME(res)) return NULL;
    return Py_True;
}

static PyObject* PywaveOutRestart(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutRestart(hwo)))   return NULL;
    return Py_True;
}

static PyObject* PywaveOutPause(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutPause(hwo)))   return NULL;
    return Py_True;
}

static PyObject* PywaveOutGetPitch(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    DWORD res;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutGetPitch(hwo, &res)))   return NULL;
    return Py_BuildValue("k", res);
}

static PyObject* PywaveOutGetPlaybackRate(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    DWORD res;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutGetPitch(hwo, &res)))   return NULL;
    return Py_BuildValue("k", res);
}

static PyObject* PywaveOutGetVolume(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    DWORD res;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutGetVolume(hwo, &res)))   return NULL;
    return Py_BuildValue("HH", LOWORD(res), HIWORD(res));
}

static PyObject* PywaveOutSetPitch(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    DWORD pitch;
    if (!PyArg_ParseTuple(args, "Lk", &hwo, &pitch)) return NULL;
    if (ErrorCheckMME(waveOutSetPitch(hwo, pitch)))   return NULL;
    return Py_True;
}

static PyObject* PywaveOutSetVolume(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    WORD left, right;
    if (!PyArg_ParseTuple(args, "LHH", &hwo, &left, &right)) return NULL;
    if (ErrorCheckMME(waveOutSetVolume(hwo, MAKELONG(left, right)))) return NULL;
    return Py_True;
}

static PyObject* PywaveOutGetID(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    UINT res = 0;
    if (ErrorCheckMME(waveOutGetID(hwo, &res))) return NULL;
    return Py_BuildValue("I", res);
}

static PyObject* PywaveOutGetNumDevs(PyObject* self, PyObject* args) {
    return Py_BuildValue("I", waveOutGetNumDevs());
}

static PyObject* PywaveOutGetDevCaps(PyObject* self, PyObject* args) {
    UINT deviceID;
    if (!PyArg_ParseTuple(args, "I", &deviceID)) return NULL;
    WAVEOUTCAPS res;
    if (ErrorCheckMME(waveOutGetDevCaps(deviceID, &res, sizeof(WAVEOUTCAPS)))) return NULL;

    return Py_BuildValue("(HHOukkk)", res.wMid, res.wPid, Py_BuildValue("(ll)", LOWORD(res.vDriverVersion), HIWORD(res.vDriverVersion)),
                               res.szPname, res.dwFormats, res.wChannels, res.dwSupport
    );
}

static PyObject* PymidiOutOpen(PyObject* self, PyObject* args) {
    HMIDIOUT hwo = 0;
    UINT deviceId;
    DWORD dopen = CALLBACK_NULL;
    DWORD_PTR dwInstance = 0, dwCallback = 0;
    if (!PyArg_ParseTuple(args, "k|KKk", &deviceId, &dwCallback, &dwInstance, &dopen)) return NULL;
    if (ErrorCheckMME(midiOutOpen(&hwo, deviceId, dwCallback, dwInstance, dopen))) return NULL;
    return Py_BuildValue("L", hwo);
}

static PyObject* PymidiOutClose(PyObject* self, PyObject* args) {
    HMIDIOUT hwo;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(midiOutClose(hwo))) return NULL;
    return Py_True;
}

static PyObject* PymidiOutShortMsg(PyObject* self, PyObject* args) {
    HMIDIOUT hwo;
    DWORD dwLo;
    if (!PyArg_ParseTuple(args, "Lk", &hwo, &dwLo)) return NULL;
    if (ErrorCheckMME(midiOutShortMsg(hwo, dwLo)))  return NULL;
    return Py_True;
}

static PyObject* PymidiOutShortMsgFromBytes(PyObject* self, PyObject* args) {
    union {
        DWORD	dwData;
        UCHAR	bData[4];
    } u;

    HMIDIOUT hmo;
    LONG a, b = 0, c = 0, d = 0;

    if (!PyArg_ParseTuple(args, "Ll|lll", &hmo, &a, &b, &c, &d)) return NULL;

    u.bData[0] = (unsigned char)a;
    u.bData[1] = (unsigned char)b;
    u.bData[2] = (unsigned char)c;
    u.bData[3] = (unsigned char)d;

    MMRESULT res = midiOutShortMsg(hmo, u.dwData);
    if (ErrorCheckMME(res)) return NULL;
    return Py_True;
}

static PyObject* PymidiOutSetVolume(PyObject* self, PyObject* args) {
    HMIDIOUT hwo;
    DWORD dwLo, dwHi;
    if (!PyArg_ParseTuple(args, "Lkk", &hwo, &dwLo, &dwHi)) return NULL;
    if (ErrorCheckMME(midiOutSetVolume(hwo, MAKELONG(dwLo, dwHi)))) return NULL;
    return Py_True;
}

static PyObject* PymidiOutPrepareHeader(PyObject* self, PyObject* args) {
    MIDIHDR hdr;
    PyObject* bArr;
    HMIDIOUT hOut;
    DWORD_PTR user;
    DWORD flags;
    if (!PyArg_ParseTuple(args, "L(OKk)", &hOut, &bArr, &user, &flags)) return NULL;

    MIDIHDR h;

    if (!PyByteArray_Check(bArr)) {
        PyErr_SetString(PyExc_TypeError, "argument 2: element 1: excepted bytearray object");
        return NULL;
    }

    LONGLONG length = PyByteArray_Size(bArr);
    LPCSTR data = PyByteArray_AsString(bArr);

    h.dwBufferLength = length;
    h.lpData = data;
    h.dwUser = user;
    h.dwFlags = flags;

    MMRESULT res = midiOutPrepareHeader(hOut, &h, sizeof(MIDIHDR));

    if (ErrorCheckMME(res)) return NULL;
    return Py_BuildValue(
        "OkkKkKk",
        PyByteArray_FromStringAndSize(h.lpData, length),
        h.dwBufferLength,
        h.dwBytesRecorded,
        h.dwUser,
        h.dwFlags,
        h.reserved,
        h.dwOffset
    );
}

static PyObject* PymidiOutUnprepareHeader(PyObject* self, PyObject* args) {
    HMIDIOUT hmo;
    PyObject* pytup;
    if (!PyArg_ParseTuple(args, "LO", &hmo, &pytup)) return NULL;

    MIDIHDR hdr = MidiTupleToStruct(pytup);
    if (MIDIHDR_TUPLE_TO_STRUCT_FAILED(hdr)) return NULL;

    MMRESULT res = midiOutUnprepareHeader(hmo, &hdr, sizeof(MIDIHDR));
    
    if (ErrorCheckMME(res)) return NULL;
    return Py_True;
}

static PyObject* PymidiOutLongMsg(PyObject* self, PyObject* args) {
    HMIDIOUT hmo;
    PyObject* pytup;
    if (!PyArg_ParseTuple(args, "LO", &hmo, &pytup)) return NULL;

    MIDIHDR hdr = MidiTupleToStruct(pytup);
    if (MIDIHDR_TUPLE_TO_STRUCT_FAILED(hdr)) return NULL;

    MMRESULT res = midiOutLongMsg(hmo, &hdr, sizeof(MIDIHDR));

    if (ErrorCheckMME(res)) return NULL;
    return Py_True;
}

static PyMethodDef module_methods[] = {
    { "waveOutOpen", PywaveOutOpen, METH_VARARGS },
    { "waveOutPrepareHeader", PywaveOutPrepareHeader, METH_VARARGS },
    { "waveOutClose", PywaveOutClose, METH_VARARGS },
    { "waveOutUnprepareHeader", PywaveOutUnprepareHeader, METH_VARARGS },
    { "waveOutWrite", PywaveOutWrite, METH_VARARGS },
    { "waveOutRestart", PywaveOutRestart, METH_VARARGS },
    { "waveOutPause", PywaveOutPause, METH_VARARGS },
    { "waveOutGetPitch", PywaveOutGetPitch, METH_VARARGS },
    { "waveOutGetPlaybackRate", PywaveOutGetPlaybackRate, METH_VARARGS },
    { "waveOutGetVolume", PywaveOutGetVolume, METH_VARARGS },
    { "waveOutSetPitch", PywaveOutSetPitch, METH_VARARGS },
    { "waveOutSetVolume", PywaveOutSetVolume, METH_VARARGS },
    { "waveOutGetID", PywaveOutGetID, METH_VARARGS },
    { "waveOutGetNumDevs", PywaveOutGetNumDevs, METH_NOARGS },
    { "waveOutGetDevCaps", PywaveOutGetDevCaps, METH_VARARGS },
    { "midiOutOpen", PymidiOutOpen, METH_VARARGS },
    { "midiOutClose", PymidiOutClose, METH_VARARGS },
    { "midiOutShortMsg", PymidiOutShortMsg, METH_VARARGS },
    { "midiOutSetVolume", PymidiOutSetVolume, METH_VARARGS },
    { "midiOutPrepareHeader", PymidiOutPrepareHeader, METH_VARARGS },
    { "midiOutUnprepareHeader", PymidiOutUnprepareHeader, METH_VARARGS },
    { "midiOutLongMsg", PymidiOutLongMsg, METH_VARARGS },
    { "midiOutShortMsgFromBytes", PymidiOutShortMsgFromBytes, METH_VARARGS },

    /* sentinel */
    { 0 }
};

static struct PyModuleDef ModuleCombinations =
{
    PyModuleDef_HEAD_INIT,
    "WinAPY_mme", /* name of module */
    NULL,
    -1,   /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    module_methods
};


void PyInit_winapy_mme(void) {
    PyModule_Create(&ModuleCombinations);
}