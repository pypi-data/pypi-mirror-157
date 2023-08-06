#pragma once
#include "TX97ObjIter.h"

namespace tx97
{

class TX97Reader
{
public:
   TX97Reader ( )
   {
      clear();
   }

   bool Load ( const void* pBuffer, size_t szBuffer, bool possessData = true )
   {
      clear();

      const byte* pBytes = static_cast<const byte*>(pBuffer);
      if (possessData)
      {
         _dataHolder.assign(pBytes, pBytes + szBuffer);
         _data = _dataHolder.data();
         _szData = _dataHolder.size();
      }
      else
      {
         _data = pBytes;
         _szData = szBuffer;
      }

      return load();
   }

   const DESCRIPTION* GetHead ( ) const { return _pHead; }
   const TAIL*        GetTail ( ) const { return _pTail; }

   ObjIter<CHARTLET>             GetDZ ( ) const { return getObjIter<CHARTLET>               ( TX_DZ ); }
   ObjIter<COAST_LINE>           GetCL ( ) const { return getObjIter<COAST_LINE>             ( TX_CL ); }
   ObjIter<COVERS_AREA>          GetDL ( ) const { return getObjIter<COVERS_AREA>            ( TX_DL ); }
   ObjIter<ISOBATHS>             GetIB ( ) const { return getObjIter<ISOBATHS>               ( TX_IB ); }
   ObjIter<LIGHTHOUSE_DESC>      GetLH ( ) const { return getObjIter<LIGHTHOUSE_DESC>        ( TX_LH ); }
   ObjIter<BUOY_DESC>            GetBO ( ) const { return getObjIter<BUOY_DESC>              ( TX_BO ); }
   ObjIter<RACON>                GetRA ( ) const { return getObjIter<RACON>                  ( TX_RA ); }
   ObjIter<DEPTHS>               GetDP ( ) const { return getObjIter<DEPTHS>                 ( TX_DP ); }
   ObjIter<COVERED_HEIGHTS>      GetDD ( ) const { return getObjIter<COVERED_HEIGHTS>        ( TX_DD ); }
   ObjIter<ISOLATED_DANGER>      GetDG ( ) const { return getObjIter<ISOLATED_DANGER>        ( TX_DG ); }
   ObjIter<LINE>                 GetLN ( ) const { return getObjIter<LINE>                   ( TX_LN ); }
   ObjIter<RECOMMENDED_ROUTE>    GetRT ( ) const { return getObjIter<RECOMMENDED_ROUTE>      ( TX_RT ); }
   ObjIter<CIRCLE>               GetCR ( ) const { return getObjIter<CIRCLE>                 ( TX_CR ); }
   ObjIter<STREAM>               GetFL ( ) const { return getObjIter<STREAM>                 ( TX_FL ); }
   ObjIter<TEXT>                 GetTX ( ) const { return getObjIter<TEXT>                   ( TX_TX ); }
   ObjIter<INFORMATION>          GetIN ( ) const { return getObjIter<INFORMATION>            ( TX_IN ); }
   ObjIter<OTHER_OBJECT>         GetOT ( ) const { return getObjIter<OTHER_OBJECT>           ( TX_OT ); }
   ObjIter<SEABED_NATURE>        GetSB ( ) const { return getObjIter<SEABED_NATURE>          ( TX_SB ); }
   ObjIter<HORISONTAL_LANDMARKS> GetHL ( ) const { return getObjIter<HORISONTAL_LANDMARKS>   ( TX_HL ); }
   ObjIter<HEIGHT>               GetHG ( ) const { return getObjIter<HEIGHT>                 ( TX_HG ); }
   ObjIter<COASTAL_FEATURE>      GetHO ( ) const { return getObjIter<COASTAL_FEATURE>        ( TX_HO ); }

   template<class ObjStruct>
   ObjIter<ObjStruct> GetObjIter(unsigned layerIdx) const { return getObjIter<ObjStruct>(layerIdx); };
  

private:
   void clear()
   {
      _dataHolder.clear();
      _data = nullptr;
      _szData = 0;

      _pHead = nullptr;
      _pTail = nullptr;
   }

   template<class ObjStruct>
   ObjIter<ObjStruct> getObjIter ( unsigned layerIdx ) const
   {
      return ObjIter<ObjStruct>( _pHead, &_data[_pHead->Offsets[layerIdx]],
         _pHead->Offsets[layerIdx + 1] - _pHead->Offsets[layerIdx] );
   }

   bool load ()
   {
      // parse description
      {
         if ( _szData < sizeof(DESCRIPTION_EX) )
            return false;
         _pHead = reinterpret_cast<const DESCRIPTION_EX*>( &_data[0] );
      }
      // parse tail
      {
         const long tailOffset = _pHead->Offsets[_countof(_pHead->Offsets) - 1];
         if ( _szData < tailOffset + sizeof(TAIL) - sizeof(char) )  // -1, так как в структуре массив из одного символа
            return false;
         _pTail = reinterpret_cast<const TAIL*>( &_data[tailOffset] );
         const long tailSize = (_pTail->name.N - 1) * sizeof(char) + sizeof(TAIL);
         if ( static_cast<long>(_szData) < tailOffset + tailSize )
            return false;

         const long crcOffset = tailOffset + tailSize;
         if ( _szData >= crcOffset + sizeof(long) )
         {
            // checksum present
            const long* pSavedCrc = reinterpret_cast<const long*>( &_data[crcOffset] );

            // calc check sum (без поля Crc)
            const long crc = calc_check_sum( &_data[0], static_cast<unsigned>(_szData - sizeof(long)) );
            if ( crc != *pSavedCrc )
               return false;
         }
      }

      return true;
   }

private:
   ByteVec _dataHolder;

   const byte* _data = nullptr;
   size_t _szData = 0;

   const DESCRIPTION_EX* _pHead = nullptr;
   const TAIL* _pTail = nullptr;
};

}
