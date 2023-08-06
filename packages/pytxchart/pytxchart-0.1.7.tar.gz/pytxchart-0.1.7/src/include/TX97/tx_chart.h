#pragma once
#include "TX97Reader.h"
#include "TX97PointConvert.h"
#include "TX97StructsConvert.h"
#include "TX97PointConvert.h"

namespace TX97ImportExport
{
   struct tx_chart
   {
      TX97Convert::trs_point_convert CreatePointConverter() const
      {
         const TX97Convert::lat_lon lb{ desc.Latb, desc.Lonb };
         const TX97Convert::lat_lon rt{ desc.Late, desc.Lone };
         return TX97Convert::trs_point_convert(lb, rt);
      }
      DESCRIPTION_Attrs desc;
      TAIL_Attrs        tail;
      TRSLayerContent   layers[tx97::LayersCount];
   };

   template<class TxObjHolder>
   inline void read_chart_layer(const tx97::TX97Reader& reader, tx_chart& crt)
   {
      //auto coorsConverter = crt.CreatePointConverter();

      auto iter = reader.GetObjIter<TxObjHolder::TxStruct>(TxObjHolder::TxLayer);
      while (iter.Next())
      {
         crt.layers[TxObjHolder::TxLayer].push_back(
            std::unique_ptr<Base_Attrs_Struct>(new TxObjHolder(iter.Get())));
      }
   }

   inline tx_chart read_tx_chart(const char* chartPath)
   {
      auto buf = read_file_to_buffer(chartPath);
      if (buf.empty())
         return tx_chart();
      tx97::TX97Reader reader;
      reader.Load(buf.data(), buf.size());

      auto desc = reader.GetHead();

      tx_chart crt;
      crt.desc = DESCRIPTION_Attrs(desc);
      crt.tail = TAIL_Attrs(reader.GetTail());

      read_chart_layer<Point_Holder<RACON_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<DEPTHS_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<COVERED_HEIGHTS_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<ISOLATED_DANGER_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<CIRCLE_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<STREAM_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<TEXT_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<INFORMATION_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<OTHER_OBJECT_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<SEABED_NATURE_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<HEIGHT_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<LIGHTHOUSE_DESC_Attrs>>(reader, crt);
      read_chart_layer<Point_Holder<BUOY_DESC_Attrs>>(reader, crt);

      read_chart_layer<Linear_Holder<CHARTLET_Attrs>>(reader, crt);
      read_chart_layer<Linear_Holder<COAST_LINE_Attrs>>(reader, crt);
      read_chart_layer<Linear_Holder<COVERS_AREA_Attrs>>(reader, crt);
      read_chart_layer<Linear_Holder<ISOBATHS_Attrs>>(reader, crt);
      read_chart_layer<Linear_Holder<LINE_Attrs>>(reader, crt);
      read_chart_layer<Linear_Holder<RECOMMENDED_ROUTE_Attrs>>(reader, crt);
      read_chart_layer<Linear_Holder<HORISONTAL_LANDMARKS_Attrs>>(reader, crt);
      read_chart_layer<Linear_Holder<COASTAL_FEATURE_Attrs>>(reader, crt);

      return crt;
   }

}



