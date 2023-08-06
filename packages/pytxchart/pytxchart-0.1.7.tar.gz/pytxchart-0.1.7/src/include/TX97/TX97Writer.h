#pragma once
#include "..\Common\common.h"
#include "TX97StructsConvert.h"
#include "tx_chart.h"

namespace tx97
{
   class TX97Writer
   {
   public:
      
      TX97Writer(const TX97ImportExport::tx_chart& crt) : _crt(crt) {};
      raw_pipeline_ostream WriteToBuffer()
      {
         for (size_t layer = 0; layer < (size_t)tx97::LayersCount; ++layer)
         {
            if (_obj_layouts[layer].size() == std::numeric_limits<short>::max())
               break;

            for (const auto& o : _crt.layers[layer])
            {
               auto& buf = _layersBuffers[layer];
               const size_t offset = _layersBuffers[layer].getPos();
               o->write_tx(buf);
               const size_t size = buf.getPos() - offset;
               _obj_layouts[layer].push_back(obj_layout(/*objID, */offset, size));

            }
         }

         long offsets[tx97::LayersCount + 1];
         memset(offsets, 0, sizeof(offsets));
         long curOffset = static_cast<long>(sizeof(_crt.desc) + sizeof(offsets));
         for (unsigned txLayer = 0; txLayer < tx97::LayersCount; ++txLayer)
         {
            offsets[txLayer] = curOffset;
            curOffset += sizeof(short) + _layersBuffers[txLayer].getSize();
         }
         offsets[tx97::LayersCount] = curOffset;  // offset of tail

         raw_pipeline_ostream tailStream;
         _crt.tail.write_tx(tailStream);

         //////////////////////////////////////////////////////////////////////////

         raw_pipeline_ostream ost;
         props_on_map props;
         // TODO: write directly without props
         PropsIO::Write(_crt.desc, props);
         TX97ImportExport::DESCRIPTION_Attrs descAttrs;
         PropsIO::Read(descAttrs, props);
         auto desc = descAttrs.GetTxDesc();
         ost.write(&desc, sizeof(desc));
         ost.write(offsets, sizeof(offsets));

         for (size_t layer = 0; layer < (size_t)tx97::LayersCount; ++layer)
         {
            const short objsCount = static_cast<short>(_obj_layouts[layer].size());
            ost.write(&objsCount, sizeof(short));
            ost.write(_layersBuffers[layer].getData(), _layersBuffers[layer].getSize());
            //TODO: здесь была сортировка по ObjectId. Она должна быть отдельно от записи
         }

         ost.write(tailStream.getData(), tailStream.getSize());

         // write check-sum
         const long crc = tx97::calc_check_sum(ost.getData(), ost.getSize());
         ost.write(&crc, sizeof(crc));

         return ost;
      }

   private:
      struct obj_layout
      {
         obj_layout(/*ObjectID _objID = -1, */size_t _offset = 0, size_t _size = 0)
            : /*objID(_objID), */offset(_offset), size(_size)
         { }

         /*ObjectID objID;*/
         size_t   offset, size;

         //bool operator < (const obj_layout& rhs) const { return objID < rhs.objID; }
      };
   private:
      const TX97ImportExport::tx_chart& _crt;
      raw_pipeline_ostream _layersBuffers[tx97::LayersCount];
      std::vector<obj_layout> _obj_layouts[tx97::LayersCount];
   };
};
