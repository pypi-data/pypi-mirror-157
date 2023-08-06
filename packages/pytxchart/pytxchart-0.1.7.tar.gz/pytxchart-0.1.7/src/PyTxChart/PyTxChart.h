#include <string>
#include <pybind11/pybind11.h>
#include "TX97\tx_chart.h"

class PyTxChart 
{
   public:
      bool Read(std::string& file_path);
      bool Write(std::string& file_path);
      pybind11::dict GetData();
      bool SetData(const pybind11::dict& data);
      pybind11::tuple ConvertPointFromTxUnitsToLonLat(pybind11::tuple&) 
      {
         // TODO: use trs_point_convert
         return pybind11::make_tuple(0, 0);
      }
      pybind11::tuple ConvertPointFromLonLatToTxUnits(pybind11::tuple&)
      {
         // TODO: use trs_point_convert
         return pybind11::make_tuple(0, 0);
      }
private:
      TX97ImportExport::tx_chart _crt;
};
