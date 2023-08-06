#include "stdafx.h"
#include "PyTxChart.h"

PYBIND11_MODULE(pytxchart, m) {
   pybind11::class_<PyTxChart>(m, "PyTxChart")
      .def(pybind11::init())
      .def("read", &PyTxChart::Read)
      .def("write", &PyTxChart::Write)
      .def("get_data", &PyTxChart::GetData)
      .def("set_data", &PyTxChart::SetData);

//    m.def(
// 		"read_chart",
// 		&ReadChart,
// 		"",
// 		pybind11::arg("file_path")
// 		);
};

