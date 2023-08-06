#include "stdafx.h"
#include "PyTxChart.h"
#include "TX97/tx_chart.h"
#include "TX97/TX97Writer.h"
#include "Common/string_convert.h"


struct props_on_dict
{
   using container_type = pybind11::dict;
   using container_ptr = std::shared_ptr<container_type>;
   container_ptr container = std::make_shared<container_type>();
   bool is_valid() const
   {
      return (bool)container;
   }
};

// implementation
namespace PropSerialTraits
{
   bool is_valid(const props_on_dict& props)
   {
      return props.is_valid();
   }

   template<class T>
   bool get_item(const wchar_t* itemName, T& itemValue, const props_on_dict& props)
   {
      if (!props.container->contains(itemName))
         return false;
      const auto& cnt = *(props.container); 
      itemValue = cnt[itemName];
      return true;
   }

   template<class T>
   void put_item(const wchar_t* itemName, T itemValue, props_on_dict& props)
   {
      const auto& cnt = *(props.container); 
      cnt[itemName] = itemValue;
   }

   template<class ElementIter>
   inline void put_array(const wchar_t* itemName, ElementIter begin, ElementIter end, props_on_dict& props)
   {
      //std::vector<std::any> v;
      //for (auto it = begin; it != end; ++it )
      //{
      //   props_on_map elemProps;
      //   props.container->insert(std::make_pair(name, result.container));

      //}
      assert(!"put_array not implemented yet");
   }

   inline props_on_map create_branch(props_on_dict& props, const wchar_t* name)
   {
      props_on_map result;
//      props.container->insert(std::make_pair(name, result.container));
      return result;
   }

//    inline props_on_map get_branch(props_on_dict& props, const wchar_t* name)
//    {
//       auto it = props.container->find(name);
//       return props_on_map{ it != props.container->end()
//          ? std::any_cast<props_on_map::container_ptr>(it->second)
//          : nullptr };
//    }
}

namespace py = pybind11;

namespace PropSerialTraits
{
   bool is_valid(const py::dict& props)
   {
      return !props.empty();
//      return !props.is_none();
   }

   template<class T>
   bool get_item(const wchar_t* itemName, T& itemValue, const py::dict& props)
   {
      std::string sname = wstring_to_string(itemName);

      if (!props.contains(sname.c_str()))
         return false;

      itemValue = props[sname.c_str()].cast<T>();
      return true;
   }

   template<class T>
   void put_item(const wchar_t* itemName, T itemValue, py::dict& props)
   {
      std::string sname = wstring_to_string(itemName);
      props[sname.c_str()] = itemValue;
   }

   template<class ElementIter>
   inline void put_array(const wchar_t* itemName, ElementIter begin, ElementIter end, py::dict& props)
   {
      //std::vector<std::any> v;
      //for (auto it = begin; it != end; ++it )
      //{
      //   props_on_map elemProps;
      //   props.container->insert(std::make_pair(name, result.container));

      //}
      assert(!"put_array not implemented yet");
   }

   inline py::dict create_branch(py::dict& props, const wchar_t* name)
   {
      py::dict result;
      std::string sname = wstring_to_string(name);
      props[sname.c_str()] = result;
      //      props.container->insert(std::make_pair(name, result.container));
      return result;
   }

   inline py::dict get_branch(py::dict& props, const wchar_t* name)
   {
      std::string sname = wstring_to_string(name);

      if (!props.contains(sname.c_str()))
          // Правильней было бы возвращать none, но происходит исключение при неявном приведении none в dict.
          // не стал разбираться в чём дело и вернул пустой dict.
          // Так же исправлен метод is_valid в котором проверялся is_none на проверку на empty.
          return py::dict();//py::none();
          
      return props[sname.c_str()];
   }
}

const char* LayerNames[] =
{
 "DZ", "CL", "DL", "IB", "LH", "BO", "RA", "DP", "DD", "DG", "LN", "RT", "CR", "FL", "TX", "IN", "OT", "SB", "HL", "HG", "HO"
};

size_t layer_name_2_layer_index(const char* name)
{
   static std::map<std::string, size_t> remap;
   if (remap.empty())
      for (size_t i = 0; i < sizeof(LayerNames) / sizeof(char*); ++ i)
         remap[LayerNames[i]] = i;

   return remap[name];
}

template<class TProps>
TProps get_tx_object_props(const TX97ImportExport::Base_Attrs_Struct* pBase, tx97::Layer layer)
{
   using namespace TX97ImportExport;
   TProps res;
   switch(layer)
   {
      case CHARTLET_Attrs::TxLayer:              PropsIO::Write(*(dynamic_cast<const CHARTLET_Attrs*>(pBase)), res); break;
      case COAST_LINE_Attrs::TxLayer:            PropsIO::Write(*(dynamic_cast<const COAST_LINE_Attrs*>(pBase)), res); break;
      case COVERS_AREA_Attrs::TxLayer:           PropsIO::Write(*(dynamic_cast<const COVERS_AREA_Attrs*>(pBase)), res); break;
      case ISOBATHS_Attrs::TxLayer:              PropsIO::Write(*(dynamic_cast<const ISOBATHS_Attrs*>(pBase)), res); break;
      case LIGHTHOUSE_DESC_Attrs::TxLayer:       PropsIO::Write(*(dynamic_cast<const LIGHTHOUSE_DESC_Attrs*>(pBase)), res); break;
      case BUOY_DESC_Attrs::TxLayer:             PropsIO::Write(*(dynamic_cast<const BUOY_DESC_Attrs*>(pBase)), res); break;
      case RACON_Attrs::TxLayer:                 PropsIO::Write(*(dynamic_cast<const RACON_Attrs*>(pBase)), res); break;
      case DEPTHS_Attrs::TxLayer:                PropsIO::Write(*(dynamic_cast<const DEPTHS_Attrs*>(pBase)), res); break;
      case COVERED_HEIGHTS_Attrs::TxLayer:       PropsIO::Write(*(dynamic_cast<const COVERED_HEIGHTS_Attrs*>(pBase)), res); break;
      case ISOLATED_DANGER_Attrs::TxLayer:       PropsIO::Write(*(dynamic_cast<const ISOLATED_DANGER_Attrs*>(pBase)), res); break;
      case LINE_Attrs::TxLayer:                  PropsIO::Write(*(dynamic_cast<const LINE_Attrs*>(pBase)), res); break;
      case RECOMMENDED_ROUTE_Attrs::TxLayer:     PropsIO::Write(*(dynamic_cast<const RECOMMENDED_ROUTE_Attrs*>(pBase)), res); break;
      case CIRCLE_Attrs::TxLayer:                PropsIO::Write(*(dynamic_cast<const CIRCLE_Attrs*>(pBase)), res); break;
      case STREAM_Attrs::TxLayer:                PropsIO::Write(*(dynamic_cast<const STREAM_Attrs*>(pBase)), res); break;
      case TEXT_Attrs::TxLayer:                  PropsIO::Write(*(dynamic_cast<const TEXT_Attrs*>(pBase)), res); break;
      case INFORMATION_Attrs::TxLayer:           PropsIO::Write(*(dynamic_cast<const INFORMATION_Attrs*>(pBase)), res); break;
      case OTHER_OBJECT_Attrs::TxLayer:          PropsIO::Write(*(dynamic_cast<const OTHER_OBJECT_Attrs*>(pBase)), res); break;
      case SEABED_NATURE_Attrs::TxLayer:         PropsIO::Write(*(dynamic_cast<const SEABED_NATURE_Attrs*>(pBase)), res); break;
      case HORISONTAL_LANDMARKS_Attrs::TxLayer:  PropsIO::Write(*(dynamic_cast<const HORISONTAL_LANDMARKS_Attrs*>(pBase)), res); break;
      case HEIGHT_Attrs::TxLayer:                PropsIO::Write(*(dynamic_cast<const HEIGHT_Attrs*>(pBase)), res); break;
      case COASTAL_FEATURE_Attrs::TxLayer:       PropsIO::Write(*(dynamic_cast<const COASTAL_FEATURE_Attrs*>(pBase)), res); break;
      default:
      {
         assert(!"unknown tx layer");
         break;
      }
   }
   return res;
}

py::dict get_chart_props(TX97ImportExport::tx_chart& crt)
{
   py::list features;
   for (size_t i = 0; i < tx97::LayersCount; ++i)
   {
      for (const auto& osrc : crt.layers[i])
      {
         py::dict ft;
         ft["properties"] = get_tx_object_props<py::dict>(osrc.get(), (tx97::Layer)i); 
         ft["layer"] = LayerNames[i];
         
         py::list coordinates;
         for (const tx97::TRS_GEO_POINT& p : osrc->get_points())
         {
            py::list coordsPair;
            coordsPair.append(p.lon);
            coordsPair.append(p.lat);
            coordinates.append(coordsPair);
         }
         ft["coordinates"] = coordinates;
         features.append(ft);

      }
   }
   py::dict desc, tail;
   PropsIO::Write(crt.desc, desc);
   PropsIO::Write(crt.tail, tail);

   py::dict res;
   res["desc"] = desc;
   res["tail"] = tail;
   res["features"] = features;
   return res;
}

bool PyTxChart::Read(std::string& file_path)
{
   _crt = TX97ImportExport::read_tx_chart(file_path.c_str());
   return !_crt.desc.is_empty();
}

bool PyTxChart::Write(std::string& file_path)
{
    auto buf = tx97::TX97Writer(_crt).WriteToBuffer();
    return write_buffer_to_file(reinterpret_cast<const char*>(buf.getData()), (size_t)buf.getSize(), file_path.c_str());
}

pybind11::dict PyTxChart::GetData()
{
   return get_chart_props(_crt);
}

tx97::TRS_GEO_POINT get_point(const py::handle& coordinate)
{
    tx97::TRS_GEO_POINT p;

    pybind11::iterator it = coordinate.begin();
    p.lon = py::cast<short>(*it);
    ++it;
    p.lat = py::cast<short>(*it);

    return p;
}

std::vector<tx97::TRS_GEO_POINT> get_vector_points(const py::list& coordinates)
{
    std::vector<tx97::TRS_GEO_POINT> points;
    for (auto coordsPair : coordinates)
        points.push_back(get_point(coordsPair));
    return points;
}

template<class T>
void set_tx_object_props(TX97ImportExport::tx_chart& crt, py::dict ftDict)
{
    using namespace TX97ImportExport;

    T object;

    auto props = ftDict["properties"].cast<py::dict>();
    PropsIO::Read(object, props);

    auto coordinates = ftDict["coordinates"].cast<py::list>();
    auto points = get_vector_points(coordinates);
    object.put_points(points);

    crt.layers[T::object_type::TxLayer].push_back(std::unique_ptr<Base_Attrs_Struct>(new T(object)));
}

bool PyTxChart::SetData(const py::dict& data)
{
   using namespace TX97ImportExport;

   _crt = tx_chart();
   PropsIO::Read(_crt.desc, data["desc"].cast<py::dict>());
   PropsIO::Read(_crt.tail, data["tail"].cast<py::dict>());
   auto features = data["features"].cast<py::list>();
   for (auto ft : features)
   {
      auto ftDict = ft.cast<py::dict>();
      std::string layer = ftDict["layer"].cast<std::string>();
      switch (layer_name_2_layer_index(ftDict["layer"].cast<std::string>().c_str()))
      {
         case CHARTLET_Attrs::TxLayer:             set_tx_object_props<CHARTLET_Holder>(_crt, ftDict); break;
         case COAST_LINE_Attrs::TxLayer:           set_tx_object_props<COAST_LINE_Holder>(_crt, ftDict); break;
         case COVERS_AREA_Attrs::TxLayer:          set_tx_object_props<COVERS_AREA_Holder>(_crt, ftDict); break;
         case ISOBATHS_Attrs::TxLayer:             set_tx_object_props<ISOBATHS_Holder>(_crt, ftDict); break;
         case LIGHTHOUSE_DESC_Attrs::TxLayer:      set_tx_object_props<LIGHTHOUSE_DESC_Holder>(_crt, ftDict); break;
         case BUOY_DESC_Attrs::TxLayer:            set_tx_object_props<BUOY_DESC_Holder>(_crt, ftDict); break;
         case RACON_Attrs::TxLayer:                set_tx_object_props<RACON_Holder>(_crt, ftDict); break;
         case DEPTHS_Attrs::TxLayer:               set_tx_object_props<DEPTHS_Holder>(_crt, ftDict); break;
         case COVERED_HEIGHTS_Attrs::TxLayer:      set_tx_object_props<COVERED_HEIGHTS_Holder>(_crt, ftDict); break;
         case ISOLATED_DANGER_Attrs::TxLayer:      set_tx_object_props<ISOLATED_DANGER_Holder>(_crt, ftDict); break;
         case LINE_Attrs::TxLayer:                 set_tx_object_props<LINE_Holder>(_crt, ftDict); break;
         case RECOMMENDED_ROUTE_Attrs::TxLayer:    set_tx_object_props<RECOMMENDED_ROUTE_Holder>(_crt, ftDict); break;
         case CIRCLE_Attrs::TxLayer:               set_tx_object_props<CIRCLE_Holder>(_crt, ftDict); break;
         case STREAM_Attrs::TxLayer:               set_tx_object_props<STREAM_Holder>(_crt, ftDict); break;
         case TEXT_Attrs::TxLayer:                 set_tx_object_props<TEXT_Holder>(_crt, ftDict); break;
         case INFORMATION_Attrs::TxLayer:          set_tx_object_props<INFORMATION_Holder>(_crt, ftDict); break;
         case OTHER_OBJECT_Attrs::TxLayer:         set_tx_object_props<OTHER_OBJECT_Holder>(_crt, ftDict); break;
         case SEABED_NATURE_Attrs::TxLayer:        set_tx_object_props<SEABED_NATURE_Holder>(_crt, ftDict); break;
         case HORISONTAL_LANDMARKS_Attrs::TxLayer: set_tx_object_props<HORISONTAL_LANDMARKS_Holder>(_crt, ftDict); break;
         case HEIGHT_Attrs::TxLayer:               set_tx_object_props<HEIGHT_Holder>(_crt, ftDict); break;
         case COASTAL_FEATURE_Attrs::TxLayer:      set_tx_object_props<COASTAL_FEATURE_Holder>(_crt, ftDict); break;
         default:
         {
             assert(!"unknown layer name");
             break;
         }
      }
   }

   return true;
}
