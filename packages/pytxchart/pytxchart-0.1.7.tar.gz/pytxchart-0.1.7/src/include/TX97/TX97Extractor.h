#pragma once

#include "TX97Structs.h"
#include "TX97StructsDesc.h"

namespace tx97
{

typedef unsigned char byte;
typedef std::vector<byte> ByteVec;

// поддержка "замапливания" памяти на структуры tx97

template<class ObjStruct>
class Extractor
{
public:
   long Get ( const DESCRIPTION* pDesc, const byte* pBuffer, unsigned szBuffer, const ObjStruct*& pObjStruct )
   {
      const long objStructSize = sizeof(ObjStruct);
      if ( szBuffer >= objStructSize )
      {
         pObjStruct = reinterpret_cast<const ObjStruct*>( pBuffer );
         return objStructSize;
      }
      return 0;
   }
};

//////////////////////////////////////////////////////////////////////////

/// Алгоритм чтения всех структур, содержащих множество точек в упакованном виде
/// @param destBuf Буфер, в который будет записана распакованная структура
/// @param pBuffer Буфер, из которого читаются исходные данные
/// @return Размер исходного буфера, который занимает упакованная структура
template<typename ObjStruct>
long CreatePolyLineStCompress ( const byte* pBuffer, size_t szBuffer, ByteVec& destBuf )
{
   const byte STOP_PACKED_BYTE = 0x80; // Константа, которой завершается массив упакованных координат

   if ( szBuffer < sizeof(ObjStruct) )
      return 0;

   // Размер стуктуры, которая должна быть заполнена
   ObjStruct const * p = reinterpret_cast< ObjStruct const * >( pBuffer );
   const long full_dest_struct_size = sizeof( ObjStruct ) +( p->N - 1 ) * sizeof(TRS_GEO_POINT);

   // Чтения количества байт под координаты
   const long fixed_size = sizeof( ObjStruct ) - sizeof( TRS_GEO_POINT );
   unsigned short const * bytes = reinterpret_cast< unsigned short const * > ( 
      pBuffer + fixed_size );

   const long full_source_struct_size = fixed_size + sizeof( unsigned short ) + *bytes;
   if ( full_source_struct_size > static_cast< long > ( szBuffer ) )
      return 0;

   if ( full_dest_struct_size < 0 || full_source_struct_size < 0 )
      return 0;

   // Выделение памяти и заполнение 0
   destBuf.assign( full_dest_struct_size, 0 );
   // Записать фиксированную часть структуры
   ::memcpy( &destBuf.at(0), pBuffer, fixed_size );

   ObjStruct * dest_st = reinterpret_cast< ObjStruct * >( &destBuf.at(0) );
   // Пропустить поля bytes (short) и LHEAD (long) из буфера
   const byte * source_buffer_offset = nullptr;
   size_t counter = 0;

   long index = fixed_size + sizeof( unsigned short ) + sizeof( long );

   if (  static_cast< long >( szBuffer ) >= index )
   {
      source_buffer_offset = pBuffer + index;
      counter = index;
   }
   else
      return 0;

   bool packed = false;

   for( int i = 0; i < dest_st->N; ++i )
   {
      if( packed && ( *source_buffer_offset == STOP_PACKED_BYTE ) )
      { // Упаковка точек закончилась
         ++source_buffer_offset;
         ++counter;
         packed = false;
      }
      if( !packed )
      { 
         // Проверяем, не вышел ли указатель за границы вектора
         if ( counter > szBuffer )
            return 0;

         // Читаются не упакованные точки.
         ::memcpy( &destBuf.at( fixed_size + i * sizeof( TRS_GEO_POINT ) ),
            source_buffer_offset, 
            sizeof( TRS_GEO_POINT) );
         if( dest_st->points[ i ].lon < 0 )
         {
            dest_st->points[ i ].lon = -dest_st->points[ i ].lon - 1;
            packed = true;
         }
         source_buffer_offset += sizeof( TRS_GEO_POINT );
         counter += sizeof( TRS_GEO_POINT );
      }
      else
      { // Читаются упакованные точки.
         if ( counter > szBuffer )
            return 0;

         char packed_point[ 2 ];
         ::memcpy( &packed_point, source_buffer_offset, sizeof( packed_point) );

         dest_st->points[ i ].lat = dest_st->points[ i - 1 ].lat + packed_point[ 0 ];
         dest_st->points[ i ].lon = dest_st->points[ i - 1 ].lon + packed_point[ 1 ];
         source_buffer_offset += sizeof( packed_point );
         counter += sizeof( packed_point );
      }
   }
   return full_source_struct_size;
}

/// Алгоритм вычисления размера всех структур, содержащих множество точек в неупакованном виде
/// @param source_buffer Буфер, из которого читаются исходные данные, необходимые для вычисления
/// @return Размер буфера, который занимает структура
template< typename ObjStruct >
long CalcPolyLineSize( const byte * buffer, size_t size )
{
   if( size < sizeof( ObjStruct ) )
      return 0;

   // Размер стуктуры, которая должна быть заполнена.
   ObjStruct const * p = reinterpret_cast< ObjStruct const * >( buffer );
   const long full_dest_struct_size = sizeof( ObjStruct ) +( p->N - 1 ) * sizeof( TRS_GEO_POINT );
   if( full_dest_struct_size > static_cast< long > ( size ) )
      return 0;

   return full_dest_struct_size;
}

template<class ObjStruct>
class LineExtractor
{
public:
   long Get ( const DESCRIPTION* pDesc, const byte* pBuffer, unsigned szBuffer, const ObjStruct*& pObjStruct )
   {
      long srcStructSize = 0;
      if ( pDesc->compress )
      {
         // распаковка в _unpackedBuf
         srcStructSize = CreatePolyLineStCompress<ObjStruct>( pBuffer, szBuffer, _unpackedBuf );
         if ( srcStructSize == 0 )
            return 0;

         _ASSERTE( !_unpackedBuf.empty() );
         pObjStruct = reinterpret_cast<const ObjStruct*>( &_unpackedBuf[0] );
      }
      else
      {
         srcStructSize = CalcPolyLineSize<ObjStruct>( pBuffer, szBuffer );
         if ( srcStructSize == 0 )
            return 0;

         pObjStruct = reinterpret_cast<const ObjStruct*>( pBuffer );
      }
      return srcStructSize;
   }

private:
   const DESCRIPTION* _pDesc;
   ByteVec _unpackedBuf;
};

template<> class Extractor<CHARTLET>             : public LineExtractor<CHARTLET>              { };
template<> class Extractor<COAST_LINE>           : public LineExtractor<COAST_LINE>            { };
template<> class Extractor<COVERS_AREA>          : public LineExtractor<COVERS_AREA>           { };
template<> class Extractor<ISOBATHS>             : public LineExtractor<ISOBATHS>              { };
template<> class Extractor<LINE>                 : public LineExtractor<LINE>                  { };
template<> class Extractor<RECOMMENDED_ROUTE>    : public LineExtractor<RECOMMENDED_ROUTE>     { };
template<> class Extractor<HORISONTAL_LANDMARKS> : public LineExtractor<HORISONTAL_LANDMARKS>  { };
template<> class Extractor<COASTAL_FEATURE>      : public LineExtractor<COASTAL_FEATURE>       { };

//////////////////////////////////////////////////////////////////////////

template<class ObjStruct>
class StringExtractor
{
public:
   long Get ( const DESCRIPTION* pDesc, const byte* pBuffer, unsigned szBuffer, const ObjStruct*& pObjStruct )
   {
      const long trsStrConstSize = sizeof(TRS_STRING) - sizeof(char);  // отнимаем символ, так как может быть пустая строка
      const long constSize = sizeof(ObjStruct) - sizeof(TRS_STRING) + trsStrConstSize;
      if ( szBuffer >= constSize )
      {
         pObjStruct = reinterpret_cast<const ObjStruct*>( pBuffer );
         const long fullSize = constSize + pObjStruct->s.N * sizeof(char);
         if ( szBuffer >= static_cast<unsigned>(fullSize) )
            return fullSize;
      }
      return 0;
   }
};

template<> class Extractor<TEXT>           : public StringExtractor<TEXT>          { };
template<> class Extractor<SEABED_NATURE>  : public StringExtractor<SEABED_NATURE> { };

//////////////////////////////////////////////////////////////////////////

inline long extractTrsString ( const byte* pBuffer, unsigned szBuffer, const TRS_STRING*& pTrsStr )
{
   const long trsStrConstSize = sizeof(TRS_STRING) - sizeof(char);  // отнимаем символ, так как может быть пустая строка
   if ( szBuffer >= static_cast<unsigned>(trsStrConstSize) )
   {
      pTrsStr = reinterpret_cast<const TRS_STRING*>( pBuffer );
      const long fullSize = trsStrConstSize + pTrsStr->N * sizeof(char);
      if ( szBuffer >= static_cast<unsigned>(fullSize) )
         return fullSize;
   }
   return 0;
}

template<>
class Extractor<INFORMATION>
{
public:
   long Get ( const DESCRIPTION* pDesc, const byte* pBuffer, unsigned szBuffer, const INFORMATION*& pObjStruct )
   {
      const long constSize = sizeof(INFORMATION) - sizeof(TRS_STRING);
      if ( szBuffer < constSize )
         return 0;
      pObjStruct = reinterpret_cast<const INFORMATION*>( pBuffer );

      // calc object full size
      long fullSize = constSize;
      for ( short i = 0; i < pObjStruct->num; ++i )
      {
         const TRS_STRING* pStrLine;
         const long trsStrSize = extractTrsString( pBuffer + fullSize, szBuffer - fullSize, pStrLine );
         if ( trsStrSize == 0 )
            return 0;
         fullSize += trsStrSize;
      }
      return fullSize;
   }
};

//////////////////////////////////////////////////////////////////////////

inline short calc_nf_info_size ( const LIGHTHOUSE* pLightHouse )
{
   if ( pLightHouse->nf > 0 )
   {
      if ( pLightHouse->ft == lighthouse_ft::MorseCode )
         return pLightHouse->nf;  // в nfInfo закодирован код морзе

      if ( is_nf_info_type(pLightHouse->ft) )
         return 2 * pLightHouse->nf;  // для всех остальных, кроме NoNfInfoTypes и lighthouse_ft::MorseCode
   }
   return 0;
}

template<>
class Extractor<LIGHTHOUSE_DESC>
{
public:
   long Get ( const DESCRIPTION* pDesc, const byte* pBuffer, unsigned szBuffer, const LIGHTHOUSE_DESC*& pObjStruct )
   {
      long curOffset = 0;

      const long constSize = sizeof(LIGHTHOUSE);
      if ( szBuffer < constSize )
         return 0;
      _lhDesc.pLighthouse = reinterpret_cast<const LIGHTHOUSE*>( pBuffer );
      curOffset += constSize;

      _lhDesc.nfInfoSize = calc_nf_info_size( _lhDesc.pLighthouse );
      if ( szBuffer < static_cast<unsigned>(curOffset + _lhDesc.nfInfoSize) )
         return 0;
      _lhDesc.pNfInfo = nullptr;
      if ( _lhDesc.nfInfoSize != 0 )
      {
         _lhDesc.pNfInfo = reinterpret_cast<const char*>( pBuffer + curOffset );
         curOffset += _lhDesc.nfInfoSize;
      }

      // Если в поле ra установлен признак наличия створа (0x80) - в массив
      // добавляется еще один элемент, поле ang у которого содержит значение
      // направления створа.
      _lhDesc.lhInfoNum = _lhDesc.pLighthouse->ns + (_lhDesc.pLighthouse->ra & lighthouse_ra::RangeIsAvailable ? 1 : 0);
      const long lhInfoBlockSize = (long)(_lhDesc.lhInfoNum * sizeof(LIGHTHOUSE_INFO));
      if ( szBuffer < static_cast<unsigned>(curOffset + lhInfoBlockSize) )
         return 0;
      _lhDesc.pLhInfo = nullptr;
      if ( _lhDesc.lhInfoNum != 0 )
      {
         _lhDesc.pLhInfo = reinterpret_cast<const LIGHTHOUSE_INFO*>( pBuffer + curOffset );
         curOffset += lhInfoBlockSize;
      }

      const long strNameSize = extractTrsString( pBuffer + curOffset, szBuffer - curOffset, _lhDesc.pName );
      if ( strNameSize == 0 )
         return 0;
      curOffset += strNameSize;

      const long strNoteSize = extractTrsString( pBuffer + curOffset, szBuffer - curOffset, _lhDesc.pNote );
      if ( strNoteSize == 0 )
         return 0;
      curOffset += strNoteSize;

      pObjStruct = &_lhDesc;
      return curOffset;
   }

private:
   LIGHTHOUSE_DESC _lhDesc;
};

//////////////////////////////////////////////////////////////////////////

template<>
class Extractor<BUOY_DESC>
{
public:
   long Get ( const DESCRIPTION* pDesc, const byte* pBuffer, unsigned szBuffer, const BUOY_DESC*& pObjStruct )
   {
      long curOffset = 0;

      const long constSize = sizeof(BUOY);
      if ( szBuffer < constSize )
         return 0;
      _buoyDesc.pBuoy = reinterpret_cast<const BUOY*>( pBuffer );
      curOffset += constSize;

      const long strNameSize = extractTrsString( pBuffer + curOffset, szBuffer - curOffset, _buoyDesc.pName );
      if ( strNameSize == 0 )
         return 0;
      curOffset += strNameSize;

      const long strNoteSize = extractTrsString( pBuffer + curOffset, szBuffer - curOffset, _buoyDesc.pNote );
      if ( strNoteSize == 0 )
         return 0;
      curOffset += strNoteSize;

      pObjStruct = &_buoyDesc;
      return curOffset;
   }

private:
   BUOY_DESC _buoyDesc;
};

//////////////////////////////////////////////////////////////////////////

template<>
class Extractor<RACON>
{
public:
   long Get ( const DESCRIPTION* pDesc, const byte* pBuffer, unsigned szBuffer, const RACON*& pObjStruct )
   {
      const long constSize = sizeof(RACON) - sizeof(char);
      if ( szBuffer < constSize )
         return 0;
      pObjStruct = reinterpret_cast<const RACON*>( pBuffer );

      long fullSize = constSize;
      if( pObjStruct->nm != 0 ) 
         fullSize += pObjStruct->nm * sizeof(char);

      if ( szBuffer < static_cast<unsigned>(fullSize) )
         return 0;

      return fullSize;
   }
};

//////////////////////////////////////////////////////////////////////////

}