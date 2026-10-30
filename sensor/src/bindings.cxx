// sensor/src/bindings.cxx

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>

#include "capture/capture.hxx"

namespace py = pybind11;

PYBIND11_MODULE(_wirewatch, m) {
    m.doc() = "WireWatch native capture extension";

    m.def("list_devices", &wirewatch::listDevices);

    m.def("capture_packets", py::overload_cast<const std::string, int, int>
        (&wirewatch::capturePackets));
}