#pragma once
#include "TX97Structs.h"

namespace TX97Convert
{
   struct lat_lon
   {
      double lat, lon;
   };

   struct xy
   {
      double x, y;
   };

#define BAST_NUM 31999.

#ifndef M_PI
#define M_PI    3.14159265358979323846
#endif

#ifndef DEG_RAD
#define DEG_RAD ( M_PI / 180. )
#endif

#ifndef RAD_DEG
#define RAD_DEG  ( 180. / M_PI )
#endif

   class trs_point_convert
   {
   public:
      trs_point_convert(const lat_lon& lb, const lat_lon& rt)
         : _mlatb(melat(lb.lat)), _mlate(melat(rt.lat))
         , _lonb(lb.lon), _lone(rt.lon)
      { }

      lat_lon operator () (const tx97::TRS_GEO_POINT& trsGeoPt) const
      {
         // в TX97 хранятся "лапти" в меркаторе
         return lat_lon
         {
            /*.lat = */ latit(_mlate + (trsGeoPt.lat * (_mlatb - _mlate)) / BAST_NUM),
            /*.lon = */_lonb + (trsGeoPt.lon * (_lone - _lonb)) / BAST_NUM
         };
      }

      tx97::TRS_GEO_POINT operator () (const lat_lon& geoPt) const
      {
         double trsLon = round((geoPt.lon - _lonb) / (_lone - _lonb) * BAST_NUM);
         double trsLat = round((melat(geoPt.lat) - _mlate) / (_mlatb - _mlate) * BAST_NUM);

         // TODO: is_between
         //ATLASSERT(cg::is_between(0, 31999, trsPt.x) && cg::is_between(0, 31999, trsPt.y));

         return tx97::TRS_GEO_POINT
         {
            /*.lat = */ static_cast<short>(trsLat), 
            /*.lon = */static_cast<short>(trsLon)
         };
      }
   private:
      static double melat(const double lat) { return log(tan((lat / 2 + 45) * DEG_RAD)) * RAD_DEG; }
      static double latit(const double mlt) { return (atan(exp(mlt * DEG_RAD)) * RAD_DEG - 45) * 2; }
   private:
      const double _mlatb, _mlate;
      const double _lonb, _lone;
   };

}
