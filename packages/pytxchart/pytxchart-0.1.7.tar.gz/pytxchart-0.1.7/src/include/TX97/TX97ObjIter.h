#pragma once

#include "TX97Extractor.h"

namespace tx97
{

template<class ObjStruct>
class ObjIter
{
public:
   ObjIter ( const DESCRIPTION* pDesc, const byte* pBuffer, unsigned szBuffer )
      : _pDesc ( pDesc ), _pBuffer ( pBuffer ), _szBuffer ( szBuffer )
      , _curIdx ( -1 ), _objsNum ( 0 )
      , _pObjStruct (nullptr )
   {
      _ASSERTE( szBuffer >= sizeof(short) );
      _objsNum = *reinterpret_cast<const short*>( _pBuffer );
      _pBuffer  += sizeof(short);
      _szBuffer -= sizeof(short);
   }

   bool Next ( )
   {
      if ( _curIdx + 1 < _objsNum )
      {
         const long objStructSize = _extractor.Get( _pDesc, _pBuffer, _szBuffer, _pObjStruct );
         if ( objStructSize > 0 )
         {
            ++_curIdx;

            _pBuffer  += objStructSize;
            _szBuffer -= objStructSize;

            return true;
         }
      }

      _ASSERTE( _curIdx + 1 == _objsNum );
      _pObjStruct = nullptr;
      return false;
   }

   const ObjStruct* Get ( )
   {
      _ASSERTE( _pObjStruct != nullptr );
      return _pObjStruct;
   }

private:
   const DESCRIPTION* _pDesc;

   const byte* _pBuffer;
   unsigned    _szBuffer;

   short _curIdx, _objsNum;

   const ObjStruct*     _pObjStruct;
   Extractor<ObjStruct> _extractor;
};

}