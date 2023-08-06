#pragma once

#include <limits>
#include <regex>
#include <sstream>
#include "TX97Structs.h"
#include "TX97StructsDesc.h"
#include "TX97Convert.h"
#include "TX97PointConvert.h"
#include "..\Common\common.h"
#include "..\Common\string_convert.h"
#include "..\PropsIO\PropsIO.h"
#include "..\props_on_map.h"


//////////////////////////////////////////////////////////////////////////
// additional functions for tx97 strings serialization
namespace PropsIO 
{
   template<size_t Size, class PropsType>
   void put(LPCWSTR name, const char(&src)[Size], PropsType& props)
   {
      put(name, TX97Convert::convert_from_tx_string(src), props);
   }

   template<size_t Size, class PropsType>
   void get(LPCWSTR name, char(&dst)[Size], PropsType& props)
   {
      std::wstring st;
      get(name, st, props);
      TX97Convert::convert_to_tx_string(st, dst);
   }
}

//////////////////////////////////////////////////////////////////////////

namespace TX97ImportExport 
{


template<class SizeType>
void write_tx_string_t ( raw_pipeline_ostream& out, const std::vector<char>& st )
{
   ATLASSERT( st.size() <= std::numeric_limits<SizeType>::max() );
   const SizeType N = static_cast<SizeType>( __min(st.size(), std::numeric_limits<SizeType>::max()) );
   raw_write( out, N );
   if ( N )
      out.write( &st[0], N * sizeof(char) );
}

inline void write_tx_string      ( raw_pipeline_ostream& out, const std::vector<char>& st ) { write_tx_string_t<unsigned char>  ( out, st ); }
inline void write_tx_long_string ( raw_pipeline_ostream& out, const std::vector<char>& st ) { write_tx_string_t<unsigned short> ( out, st ); }

inline void write_tx_string      ( raw_pipeline_ostream& out, std::wstring st ) { write_tx_string_t<unsigned char>  ( out, TX97Convert::convert_to_tx_string(st) ); }
inline void write_tx_long_string ( raw_pipeline_ostream& out, std::wstring st ) { write_tx_string_t<unsigned short> ( out, TX97Convert::convert_to_tx_string(st) ); }

//////////////////////////////////////////////////////////////////////////

// структуры поддерживают сериализацию в произвольные атрибуты
// структуры поддерживают вывод в стрим в TX97 формате

#pragma pack (1)


template<class _TxStruct, tx97::Layer _TxLayer>
struct Common_Attrs
{
   typedef _TxStruct TxStruct;

   static const tx97::Layer TxLayer = _TxLayer;
};

struct CHARTLET_Attrs : Common_Attrs<tx97::CHARTLET, tx97::TX_DZ>
{
   CHARTLET_Attrs ( ) { }
   CHARTLET_Attrs ( const TxStruct* pTxStruct ) { }

   PROP_SERIAL_BEGIN()
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const { }
};

//////////////////////////////////////////////////////////////////////////

struct COAST_LINE_Attrs : Common_Attrs<tx97::COAST_LINE, tx97::TX_CL>
{
   COAST_LINE_Attrs ( )
      : fs ( 0 )
   { }

   COAST_LINE_Attrs ( const TxStruct* pTxStruct )
      : fs ( pTxStruct->fs )
   { }

   short fs;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( fs )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write(out, fs);
   }
};

//////////////////////////////////////////////////////////////////////////

struct COVERS_AREA_Attrs : Common_Attrs<tx97::COVERS_AREA, tx97::TX_DL>
{
   COVERS_AREA_Attrs ( )
      : fs ( 0 )
   { }

   COVERS_AREA_Attrs ( const TxStruct* pTxStruct )
      : fs ( pTxStruct->fs )
   { }

   short fs;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( fs )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write(out, fs);
   }
};

//////////////////////////////////////////////////////////////////////////

struct ISOBATHS_Attrs : Common_Attrs<tx97::ISOBATHS, tx97::TX_IB>
{
   ISOBATHS_Attrs ( )
      : depth ( 0 )
      , fs ( 0 )
   { }

   ISOBATHS_Attrs ( const TxStruct* pTxStruct )
      : depth ( TX97Convert::convert_from_tx_depth(pTxStruct->depth) )
      , fs    ( pTxStruct->fs )
   {
   }

   double depth;  // Значение глубины (в метрах)
   short  fs;     

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( depth )
      SERIAL_ITEM( fs )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, TX97Convert::convert_to_tx_depth(depth) );
      raw_write( out, fs );
   }
};

//////////////////////////////////////////////////////////////////////////

struct LIGHTHOUSE_INFO_Attrs
{
   LIGHTHOUSE_INFO_Attrs ( )
      : color     ( 0 )
      , range     ( 0 )
      , begAngle  ( 0 )
   {}

   LIGHTHOUSE_INFO_Attrs ( const tx97::LIGHTHOUSE_INFO* pTxStruct )
      : color     ( pTxStruct->col )
      , range     ( pTxStruct->vl )
      , begAngle  (TX97Convert::convert_from_tx_dir(pTxStruct->ang) )
   {}

   char   color;
   char   range;
   double begAngle;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( color )
      SERIAL_ITEM( range  )
      SERIAL_ITEM( begAngle )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, color );                        // col
      raw_write( out, range );                        // vl
      raw_write( out, TX97Convert::convert_to_tx_dir(begAngle) );  // ang
   }
};

//////////////////////////////////////////////////////////////////////////

struct FLASH_ECLIPSE_Attrs
{
   FLASH_ECLIPSE_Attrs ( )
      : flash   ( 0 )
      , eclipse ( 0 )
   {}

   FLASH_ECLIPSE_Attrs ( const tx97::FLASH_ECLIPSE* pTxStruct )
      : flash   (TX97Convert::convert_from_tx_duration( pTxStruct->flash   ))
      , eclipse (TX97Convert::convert_from_tx_duration( pTxStruct->eclipse ))
   {}

   double flash;
   double eclipse;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( flash   )
      SERIAL_ITEM( eclipse )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, TX97Convert::convert_to_tx_duration(flash  ) );
      raw_write( out, TX97Convert::convert_to_tx_duration(eclipse) );
   }
};

//////////////////////////////////////////////////////////////////////////

namespace note_parser {

struct NamedVal
{
   NamedVal (byte _val, const wchar_t* _name )
      : val  ( _val )
      , name ( _name )
   {}

   const byte     val;
   const wchar_t* const name;
};

// значения разделителяются точкой с пробелом
const wchar_t* const Delimiter = L". ";

template<class NamedValIter>
std::wregex create_regex_keywords ( NamedValIter first, NamedValIter last )
{
   // prepare regex: "^(keyword_1|...|keyword_n)(delimeter|$)"
   // (иногда нет delimeter, когда после атрибутов нет текста)
   ATLASSERT( first != last );
   if ( first == last )
      return std::wregex( std::wstring(L"^()") + L"(" + Delimiter + L"|$)" );

   std::wstringstream ss;
   ss << L"^(" << first->name;
   while ( ++first != last )
      ss << L"|" << first->name;
   ss << L")" << L"(" << Delimiter << L"|$)";

   return std::wregex( ss.str().c_str() );
}

const NamedVal LightColorDefs[] = 
{
   NamedVal ( tx97::light_color::Yellow, L"Y Lt"  ),
   NamedVal ( tx97::light_color::Violet, L"Vi Lt" ),
   NamedVal ( tx97::light_color::Amber,  L"Am Lt" ),
   NamedVal ( tx97::light_color::Orange, L"Or Lt" )
};

#define ARRAY_END(a) ((a) + _countof(a))

const std::wregex g_regexLtColor = create_regex_keywords( LightColorDefs, ARRAY_END(LightColorDefs) );

inline bool extract_keyword ( const std::wregex& regExKeyword, std::wstring& note, std::wstring& keyword, const wchar_t* replaceWith = L"" )
{
   const std::wstring stNote = note;

   std::wsmatch match;
   if ( !std::regex_search(stNote, match, regExKeyword) )
      return false;

   ATLASSERT( match.size() == 3 );  // match and sub-match
   keyword = match.str( 1 );
   // из note всегда выкусываем, чтобы потом чисто записать обратно
   note = std::regex_replace( stNote, regExKeyword, std::wstring(replaceWith) ).c_str();

   return true;
}

inline bool replace_keyword ( const std::wregex& regExKeyword, std::wstring& note, const wchar_t* replaceWith )
{
   std::wstring keyword;
   return extract_keyword(regExKeyword, note, keyword, replaceWith);
}

inline bool decode_ex_color ( const wchar_t* pszLtColor, char& colorId )
{
   if ( colorId != tx97::light_color::White && colorId != tx97::light_color::Blue )
      return false;

   auto it = std::find_if(LightColorDefs, ARRAY_END(LightColorDefs),
      [ pszLtColor ] ( const NamedVal& nv ) { return wcscmp(pszLtColor, nv.name) == 0; } );

   ATLASSERT( it != ARRAY_END(LightColorDefs) );
   if ( it == ARRAY_END(LightColorDefs) )
      return false;

   // Цвета 5,7,8 кодируются значением 3 (белый), цвет 6 кодируется как 4 (голубой)
   if ( colorId == tx97::light_color::White )
   {
      if ( it->val == tx97::light_color::Yellow || 
           it->val == tx97::light_color::Amber  || 
           it->val == tx97::light_color::Orange )
      {
         colorId = it->val;
         return true;
      }
   }
   else if ( colorId == tx97::light_color::Blue )
   {
      if ( it->val == tx97::light_color::Violet )
      {
         colorId = it->val;
         return true;
      }
   }

   return false;
}

// если цвет новый, в note вставляется подстрока с ним, colorId выставляется старым
// если цвет не новый, colorId и note остаётся без изменений
inline bool encode_ex_color ( std::wstring& note, char& colorId, bool insertColorToNote = true )
{
   if (  colorId == tx97::light_color::NoLight
      || colorId == tx97::light_color::Red
      || colorId == tx97::light_color::Green
      || colorId == tx97::light_color::White
      || colorId == tx97::light_color::Blue )
      return false;

   if (insertColorToNote)
   {
      auto it = std::find_if( LightColorDefs, ARRAY_END(LightColorDefs),
                             [ colorId ] ( const NamedVal& nv ) { return nv.val == colorId; } );

      ATLASSERT( it != ARRAY_END(LightColorDefs) );
      if ( it == ARRAY_END(LightColorDefs) )
         return false;

      const bool existingReplaced = note_parser::replace_keyword(note_parser::g_regexLtColor, note, it->name);
      if (!existingReplaced)
      {
         // если текста нет, то разделитель не ставим
         note = std::wstring(it->name) + (note.length() == 0 ? L"" : Delimiter) + note;
      }
   }

   // Цвета 5,7,8 кодируются значением 3 (белый), цвет 6 кодируется как 4 (голубой)
   colorId = ( colorId == tx97::light_color::Violet  ? tx97::light_color::Blue : tx97::light_color::White );

   return true;
}

}

//////////////////////////////////////////////////////////////////////////

inline bool has_racon ( char ra )
{
   const char racon = ( ra & 0x07 );
   return ( racon == tx97::lighthouse_ra::RaconIsAvailable || racon == tx97::lighthouse_ra::RaconIsAvailableInSea );
}

//https://stackoverflow.com/questions/1903954/is-there-a-standard-sign-function-signum-sgn-in-c-c
template <typename T> int sign(T val) {
   return (T(0) < val) - (val < T(0));
}

struct LIGHTHOUSE_DESC_Attrs : Common_Attrs<tx97::LIGHTHOUSE_DESC, tx97::TX_LH>
{
   LIGHTHOUSE_DESC_Attrs() = default;

   LIGHTHOUSE_DESC_Attrs ( const TxStruct* pTxStruct )
      : period          ( pTxStruct->pLighthouse->pe / 10.0 )
      , lightType       ( pTxStruct->pLighthouse->ft )
      , ra              ( pTxStruct->pLighthouse->ra )
      , heightAboveGnd  ( TX97Convert::convert_from_tx_height(pTxStruct->pLighthouse->hl) )
      , heightAboveSea  ( TX97Convert::convert_from_tx_height(pTxStruct->pLighthouse->hs) )
      , numberNational  ( TX97Convert::convert_from_tx_string(pTxStruct->pLighthouse->rn) )
      , numberInternat  ( TX97Convert::convert_from_tx_string(pTxStruct->pLighthouse->un) )
      , dubLightsCount  ( abs(pTxStruct->pLighthouse->fl) )
      , dubLightsOrient ( sign(pTxStruct->pLighthouse->fl) )
      , mainOrAux       ( pTxStruct->pLighthouse->pr )
      , topmarkType     ( pTxStruct->pLighthouse->tf )
      , name            ( TX97Convert::convert_from_tx_string(pTxStruct->pName->Data, pTxStruct->pName->N) )
      , note            ( TX97Convert::convert_from_tx_string(pTxStruct->pNote->Data, pTxStruct->pNote->N) )
      , nf              ( pTxStruct->pLighthouse->nf )
      , ns              (pTxStruct->pLighthouse->ns)
   {
      std::transform( pTxStruct->pLhInfo, pTxStruct->pLhInfo + pTxStruct->lhInfoNum, std::back_inserter(sectors),
         [] (const tx97::LIGHTHOUSE_INFO& lhInfo) { return LIGHTHOUSE_INFO_Attrs(&lhInfo); } );

       if ( lightType == tx97::lighthouse_ft::MorseCode )
         // в pNfInfo закодирован morse код (в стандарте про это не написано)
         morseCode = TX97Convert::convert_from_tx_string( pTxStruct->pNfInfo, pTxStruct->nfInfoSize );
      else
      {
         for (short i = 0; i < pTxStruct->nfInfoSize; i += 2)
            durations.push_back( FLASH_ECLIPSE_Attrs(reinterpret_cast<const tx97::FLASH_ECLIPSE*>(&pTxStruct->pNfInfo[i])) );
      }

      if ( note.length() > 0 )
      {
         // стандарт - кодирование расширенного набора цветов огней
         std::wstring stLtColor;
         if ( note_parser::extract_keyword(note_parser::g_regexLtColor, note, stLtColor) )
         {
            // для первого сектора с цветом White или Blue производим замену цвета (если это закодировано в примечании)
            // для остальных секторов (если эту обработку уже сделали) ничего не делаем.
            // т.е. декодируем цвет только для первого подходящего сектора
            for (auto& sector : sectors)
            {
               if (note_parser::decode_ex_color(stLtColor.c_str(), sector.color))
                  break;
            }
         }
      }
   }

   double   period = 0;
   char     lightType = 0;
   char     ra = 0;
   double   leadLightDir = 0;
   double   heightAboveGnd = 0;
   double   heightAboveSea = 0;
   std::wstring  numberNational;
   std::wstring  numberInternat;
   char     dubLightsCount = 0;
   char     dubLightsOrient = 0;
   char     mainOrAux = 0;
   char     topmarkType = 0;
   std::wstring  name;
   std::wstring  note;
   std::wstring  morseCode;
   std::vector<FLASH_ECLIPSE_Attrs>    durations;
   std::vector<LIGHTHOUSE_INFO_Attrs>  sectors;
   // для совместимости храним nf - оно для определенных типов маяков не обязательно совпадает с количеством durations
   char     nf = 0;
   char     ns = 0; // TODO: количество секторов не равно реальному количеству секторов lhInfoNum, поэтому храним
   
   PROP_SERIAL_BEGIN()
      SERIAL_ITEM(period)
      SERIAL_ITEM(lightType)
      SERIAL_ITEM(ra)
      SERIAL_ITEM(heightAboveGnd)
      SERIAL_ITEM(heightAboveSea)
      SERIAL_ITEM(numberNational)
      SERIAL_ITEM(numberInternat)
      SERIAL_ITEM(dubLightsCount)
      SERIAL_ITEM(dubLightsOrient)
      SERIAL_ITEM(mainOrAux)
      SERIAL_ITEM(topmarkType)
      SERIAL_ITEM(name)
      SERIAL_ITEM(note)
      SERIAL_ITEM(morseCode)
      // TODO: implement SERIAL_ITEM_AS_COLLECTION
      ////////////
      //SERIAL_ITEM_AS_COLLECTION(durations )
      //SERIAL_ITEM_AS_COLLECTION(sectors )
      ///////////
      SERIAL_ITEM              ( nf )
      SERIAL_ITEM              ( ns )
      PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      std::vector<LIGHTHOUSE_INFO_Attrs> txSectors;
      std::wstring txNote;
      const tx97::LIGHTHOUSE txLh = getTxLH(txSectors, txNote);
      // геометрия записывается в другом месте
      out.write( &txLh.pe, sizeof(tx97::LIGHTHOUSE) - sizeof(tx97::TRS_GEO_POINT) );

      // <nf_info>
      if ( txLh.ft == tx97::lighthouse_ft::MorseCode )
      {
         const std::vector<char> morse = TX97Convert::convert_to_tx_string(morseCode);
         ATLASSERT( txLh.nf == morse.size() );
         if ( !morse.empty() )
            out.write( &morse[0], (unsigned int)morse.size() );
      }
      else if ( tx97::is_nf_info_type(txLh.ft) )
      {
         ATLASSERT( txLh.nf == durations.size() );
         for ( size_t i = 0; i < durations.size(); ++i )
            durations[ i ].write_tx( out );
      }

      // <lhs_info>
      //ATLASSERT( txLh.ns == txSectors.size() );
      for ( size_t i = 0; i < txSectors.size(); ++i )
         txSectors[ i ].write_tx( out );

      write_tx_string( out, name );
      write_tx_string( out, txNote );
   }

private:
   tx97::LIGHTHOUSE getTxLH ( std::vector<LIGHTHOUSE_INFO_Attrs>& txSectors, std::wstring& txNote ) const
   {
      txSectors = sectors;
      txNote = note;

      // перед записью возвращаем note и lightColor в первозданное состояние
      bool insertColorToNote = true;
      for (auto& sector : txSectors)
      {
         // если уже закодировали какой-нибудь сектор, значение остальных секторов c расширенными цветами просто сбрасываем в White или Blue
         if (note_parser::encode_ex_color(txNote, sector.color, insertColorToNote))
            insertColorToNote = false;
      }

      tx97::LIGHTHOUSE lh;
      memset( &lh, 0, sizeof(lh) );

      lh.pe = static_cast<short>( period * 10 );
      lh.ft = lightType;
      if ( lightType == tx97::lighthouse_ft::MorseCode )
         lh.nf = static_cast<byte>(morseCode.length());
      else if ( tx97::is_nf_info_type(lightType) )
      {
         ATLASSERT(durations.size() < 256);
         lh.nf = static_cast<char>( durations.size() );
      }
      else
         lh.nf = nf;

      lh.ra = ra;

      ATLASSERT(txSectors.size() < 256);
      //lh.ns = static_cast<char>( txSectors.size() );
      lh.ns = ns;

      lh.hl = TX97Convert::convert_to_tx_height( heightAboveGnd );
      lh.hs = TX97Convert::convert_to_tx_height( heightAboveSea );

      const std::vector<char> rn = TX97Convert::convert_to_tx_string(numberNational);
      memcpy_s( lh.rn, sizeof(lh.rn), rn.data(), __min(rn.size(), sizeof(lh.rn)) );

      const std::vector<char> un = TX97Convert::convert_to_tx_string(numberInternat);
      memcpy_s( lh.un, sizeof(lh.un), un.data(), __min(un.size(), sizeof(lh.un)) );

      lh.fl = dubLightsCount * dubLightsOrient;
      lh.pr = mainOrAux;
      lh.tf = topmarkType;

      return lh;
   }
};

//////////////////////////////////////////////////////////////////////////

// типы буев для которых имеет смысл buoy shape
const char BuoyTypesWithShape[] = { 0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 22 };

inline bool is_buoy_type_with_shape ( char tp )
{
   return std::find(BuoyTypesWithShape, ARRAY_END(BuoyTypesWithShape), tp) != ARRAY_END(BuoyTypesWithShape);
}

namespace note_parser {

// циферки соответствуют enum-у в шаблоне 
const NamedVal BuoyShapeDefs[] = 
{
   NamedVal ( 1, L"Pillar"     ),
   NamedVal ( 2, L"Can"        ),
   NamedVal ( 3, L"Conical"    ),
   NamedVal ( 4, L"Spherical"  ),
   NamedVal ( 5, L"Spar"       ),
   // поддерживаем разные типы написания
   NamedVal ( 6, L"Superbuoy"  ),
   NamedVal ( 6, L"Super buoy" ),
   NamedVal ( 6, L"Super-buoy" ),
   NamedVal ( 7, L"Barrel"     ),
   // поддерживаем разные типы написания
   NamedVal ( 8, L"Ice buoy"   ),
   NamedVal ( 8, L"Icebuoy"    ),
   NamedVal ( 8, L"Ice-buoy"   ),
};

inline char parse_buoy_shape ( const wchar_t* pszBuoyShape, char buoyType, char defBuoyShape )
{
   if ( !is_buoy_type_with_shape(buoyType) )
      return defBuoyShape;

   auto it = std::find_if( BuoyShapeDefs, ARRAY_END(BuoyShapeDefs),
      [ pszBuoyShape ] ( const NamedVal& nv ) { return wcscmp(pszBuoyShape, nv.name) == 0; } );

   ATLASSERT( it != ARRAY_END(BuoyShapeDefs) );
   if ( it == ARRAY_END(BuoyShapeDefs) )
      return defBuoyShape;

   return it->val;
}

inline void put_buoy_shape ( std::wstring& note, char buoyType, char buoyShape )
{
   if ( !is_buoy_type_with_shape(buoyType) )
      return;

   auto it = std::find_if( BuoyShapeDefs, ARRAY_END(BuoyShapeDefs),
      [ buoyShape ] ( const NamedVal& nv ) { return nv.val == buoyShape; } );
   if ( it == ARRAY_END(BuoyShapeDefs) )
      return;

   // если текста нет, то разделитель не ставим
   note = std::wstring(it->name) + (note.length() == 0 ? L"" : Delimiter) + note;
}

const std::wregex g_regexBuoyShape = create_regex_keywords( BuoyShapeDefs,  ARRAY_END(BuoyShapeDefs)  );

}



struct BUOY_DESC_Attrs : Common_Attrs<tx97::BUOY_DESC, tx97::TX_BO>
{
   BUOY_DESC_Attrs() = default;

   BUOY_DESC_Attrs ( const tx97::BUOY_DESC* pTxStruct )
      : period          ( pTxStruct->pBuoy->pe / 10.0 )
      , lightType       ( pTxStruct->pBuoy->ft )
      , flashCount      ( pTxStruct->pBuoy->nf )
      , ra              ( pTxStruct->pBuoy->ra )
      , buoyType        ( pTxStruct->pBuoy->tp )
      , buoyColor       ( pTxStruct->pBuoy->bc )
      , lightColor      ( pTxStruct->pBuoy->lc )
      , numberInternat  ( TX97Convert::convert_from_tx_string(pTxStruct->pBuoy->un) )
      , name            ( TX97Convert::convert_from_tx_string(pTxStruct->pName->Data, pTxStruct->pName->N) )
      , note            ( TX97Convert::convert_from_tx_string(pTxStruct->pNote->Data, pTxStruct->pNote->N) )
   {
      if ( lightType == tx97::lighthouse_ft::MorseCode )
      {
         // код morse - один символ в nf (код ASCII)
         morseCode = string_to_wstring(std::string(static_cast<const char*>(&flashCount), 1));
         flashCount = 0;
      }

      numberNational = TX97Convert::convert_from_tx_string(pTxStruct->pBuoy->rn);

      if ( note.length() > 0 )
      {
         // вырезаем параметры из note
         // первый - цвет (если есть), потом форма (если есть)
         std::wstring stLtColor;
         std::wstring noteBackup = note;
         if (note_parser::extract_keyword(note_parser::g_regexLtColor, note, stLtColor))
         {
            if (!note_parser::decode_ex_color(stLtColor.c_str(), lightColor))
               note = noteBackup;
         }

         std::wstring stBuoyType;
         if ( note_parser::extract_keyword(note_parser::g_regexBuoyShape, note, stBuoyType) )
         {
            // buoyShape может быть уже заполнен для iTx карты из поля bs (из rn)
            // (и является более приоритетным, чем из note)
            if (buoyShape == 0)
               buoyShape = note_parser::parse_buoy_shape( stBuoyType.c_str(), buoyType, buoyShape );
         }
      }
   }

   double   period = 0;
   char     lightType = 0;
   char     flashCount = 0;
   char     ra;
   char     buoyType = 0;
   char     buoyColor = 0;
   char     lightColor = 0;
   std::wstring  numberNational;
   std::wstring  numberInternat;
   std::wstring  name;
   std::wstring  note;
   // fields that do not exist in tx structure separately
   std::wstring  morseCode;
   char     buoyShape = 0;
   // iTX specific
   char     fixedPointCategory = 0;
   bool     fixedPointConspicious = false;
   
   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( period )
      SERIAL_ITEM( lightType )
      SERIAL_ITEM( flashCount )
      SERIAL_ITEM( ra )
      SERIAL_ITEM( buoyType )
      SERIAL_ITEM( buoyColor )
      SERIAL_ITEM( lightColor )
      SERIAL_ITEM( numberNational )
      SERIAL_ITEM( numberInternat )
      SERIAL_ITEM( name )
      SERIAL_ITEM( note )
      SERIAL_ITEM( morseCode )
      SERIAL_ITEM( buoyShape )
      SERIAL_ITEM( fixedPointCategory )
      SERIAL_ITEM( fixedPointConspicious )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      std::wstring txNote;
      const tx97::BUOY txBO = getTxBO(txNote);

      // геометрия записывается в другом месте
      out.write( &txBO.pe, sizeof(tx97::BUOY) - sizeof(tx97::TRS_GEO_POINT) );

      write_tx_string( out, name );
      write_tx_string( out, txNote );
   }

private:
   tx97::BUOY getTxBO ( std::wstring& txNote ) const
   {
      txNote = note;
      char txLightColor = lightColor;
      // перед записью возвращаем note и lightColor в первозданное состояние
      note_parser::put_buoy_shape( txNote, buoyType, buoyShape );
      note_parser::encode_ex_color( txNote, txLightColor );

      tx97::BUOY bo;
      memset( &bo, 0, sizeof(bo) );

      bo.pe = static_cast<short>( period * 10 );
      bo.ft = lightType;
      if (lightType == tx97::lighthouse_ft::MorseCode)
         bo.nf = (morseCode.length() ? (wstring_to_string(morseCode).c_str())[0] : 0);
      else
         bo.nf = flashCount;
      bo.ra = ra;
      bo.tp = buoyType;
      bo.bc = buoyColor;
      bo.lc = txLightColor;

      const std::vector<char> rn = TX97Convert::convert_to_tx_string(numberNational);
      memcpy_s( bo.rn, sizeof(bo.rn), rn.data(), __min(rn.size(), _countof(bo.rn)) * sizeof(char) );

      const std::vector<char> un = TX97Convert::convert_to_tx_string(numberInternat);
      memcpy_s( bo.un, sizeof(bo.un), un.data(), __min(un.size(), sizeof(bo.un)) );

      return bo;
   }

   std::wstring iTxSpecificParse ( const TxStruct* pTxStruct )
   {
      const std::wstring cuttedNumberNational = TX97Convert::convert_from_tx_string(
         pTxStruct->pBuoy->rn, _countof(pTxStruct->pBuoy->rn) - 1);

      const char bs = pTxStruct->pBuoy->rn[_countof(pTxStruct->pBuoy->rn) - 1];

      if ( is_buoy_type_with_shape(pTxStruct->pBuoy->tp) )
         buoyShape = bs;
      else if (pTxStruct->pBuoy->tp == tx97::buoy_tp::FixedPoint)
      {
         fixedPointConspicious = ( (bs & 0x80) == 0x80 );
         fixedPointCategory = (bs & ~0x80);
      }

      return cuttedNumberNational;
   }
};

//////////////////////////////////////////////////////////////////////////

struct RACON_Attrs : Common_Attrs<tx97::RACON, tx97::TX_RA>
{
   RACON_Attrs() = default;
   RACON_Attrs ( const TxStruct* pTxStruct )
   {
      isRacon = (0 != pTxStruct->nm);
      morseCode = string_to_wstring(std::string(pTxStruct->morse, pTxStruct->nm)).c_str();
   }

   // этого параметра нет в Tx, он выставляется по принципу если прописан morseCode это ракон, если нет - отражатель.
   bool     isRacon = false;
   std::wstring  morseCode;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( isRacon)
      SERIAL_ITEM( morseCode )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      // если установлен признак isRacon, то нужно записать поле morseCode (хотя бы из одного символа '\0'
      const char nm = !isRacon ?  0 : (char)__max(__min(morseCode.length(), 255), 1);
      raw_write(out, nm);
      if (nm > 0)
         out.write(wstring_to_string(morseCode).c_str(), nm);
   }
};

//////////////////////////////////////////////////////////////////////////

struct DEPTHS_Attrs : Common_Attrs<tx97::DEPTHS, tx97::TX_DP>
{
   DEPTHS_Attrs() = default;

   DEPTHS_Attrs ( const TxStruct* pTxStruct )
      : depth ( TX97Convert::convert_from_tx_depth(pTxStruct->depth) )
   { }

   double depth = 0;   // Значение глубины (в метрах)

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( depth )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, TX97Convert::convert_to_tx_depth(depth) );
   }
};

//////////////////////////////////////////////////////////////////////////

struct COVERED_HEIGHTS_Attrs : Common_Attrs<tx97::COVERED_HEIGHTS, tx97::TX_DD>
{
   COVERED_HEIGHTS_Attrs() = default;

   COVERED_HEIGHTS_Attrs ( const TxStruct* pTxStruct )
      : depth ( TX97Convert::convert_from_tx_depth(pTxStruct->depth) )
   { }

   double depth = 0;   // // Значение высоты (в метрах)

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( depth )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, TX97Convert::convert_to_tx_depth(depth) );
   }
};

//////////////////////////////////////////////////////////////////////////
struct ISOLATED_DANGER_Attrs : Common_Attrs<tx97::ISOLATED_DANGER, tx97::TX_DG>
{
   ISOLATED_DANGER_Attrs() = default;

   ISOLATED_DANGER_Attrs ( const TxStruct* pTxStruct )
      : depth ( TX97Convert::convert_from_tx_depth(pTxStruct->depth) )
      , type  ( pTxStruct->type )
      , exist ( pTxStruct->exist )
   { 
      if (DepthUndefinedValue == depth)
      {
         depthUndefined = true;
         depth = 0;
      }
   }

   double   depth = 0;   // Значение высоты (в метрах)
   char     type = 0;
   char     exist = 0;
   // fields that do not exist in tx structure separately
   // Данный признак кодируется значением глубины 999.
   bool     depthUndefined = false;

   static const unsigned short DepthUndefinedValue = 999;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( depth )
      SERIAL_ITEM( type )
      SERIAL_ITEM( exist )
      SERIAL_ITEM( depthUndefined)
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      if (depthUndefined)
         raw_write( out, TX97Convert::convert_to_tx_depth( DepthUndefinedValue ) );
      else
         raw_write( out, TX97Convert::convert_to_tx_depth( depth ) );

      raw_write( out, type );
      raw_write( out, exist );
   }
};

//////////////////////////////////////////////////////////////////////////

struct LINE_Attrs : Common_Attrs<tx97::LINE, tx97::TX_LN>
{
   LINE_Attrs() = default;

   LINE_Attrs ( const TxStruct* pTxStruct )
      : color ( pTxStruct->color )
      , style ( pTxStruct->style )
      , type  ( pTxStruct->type )
      , fill  (pTxStruct->fill)
   {
      // TODO: investigate
//       // HACK: UNIDATA-639 в tx-e для границы опасности используется черный цвет (у нас - красный)
//       if (type == 30)  // LN_type_DGL
//          color = 4;  // CL_RED
   }

   short color = 0;
   short style = 0;
   short type = 0;
   short fill = 0;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( color )
      SERIAL_ITEM( style )
      SERIAL_ITEM( type )
      SERIAL_ITEM( fill )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      short txColor = color;
      // HACK: UNIDATA-639 в tx-e для границы опасности используется черный цвет (у нас - красный)
      // TODO: investigate
//       if (type == 30)  // LN_type_DGL
//          txColor = 8;  // CL_BLACK

      raw_write(out, txColor);
      raw_write(out, style);
      raw_write(out, fill);
      raw_write(out, type);
   }
};

//////////////////////////////////////////////////////////////////////////

struct RECOMMENDED_ROUTE_Attrs : Common_Attrs<tx97::RECOMMENDED_ROUTE, tx97::TX_RT>
{
   RECOMMENDED_ROUTE_Attrs() = default;

   RECOMMENDED_ROUTE_Attrs ( const TxStruct* pTxStruct )
      : depth  ( TX97Convert::convert_from_tx_depth(pTxStruct->depth) )
      , dir1   (TX97Convert::convert_from_tx_dir(pTxStruct->dir1) )
      , type   ( pTxStruct->type )
   { }

   double         depth = 0;  // значение глубины (в метрах)
   double         dir1 = 0;   // (в градусах)
   unsigned short type = 0;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( depth )
      SERIAL_ITEM( dir1 )
      SERIAL_ITEM( type )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, TX97Convert::convert_to_tx_depth(depth) );
      raw_write( out, TX97Convert::convert_to_tx_dir(dir1) );
      raw_write( out, type );
   }
};

//////////////////////////////////////////////////////////////////////////

// окружности попадают на слой линий при импорте
struct CIRCLE_Attrs : Common_Attrs<tx97::CIRCLE, tx97::TX_CR>
{
   CIRCLE_Attrs() = default;

   CIRCLE_Attrs ( const TxStruct* pTxStruct )
      : r      ( pTxStruct->r )
      , sa     ( pTxStruct->sa )
      , ea     ( pTxStruct->ea )
      , kind   ( pTxStruct->kind )
      , color  ( pTxStruct->color )
      , style  ( pTxStruct->style )
      , fill   ( pTxStruct->fill)
      , type   ( pTxStruct->type )
   {
   }

   float r;
   short sa;
   short ea;
   short kind;
   short color;
   short style;
   short fill;
   short type;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( r   )
      SERIAL_ITEM( sa  )
      SERIAL_ITEM( ea  )
      SERIAL_ITEM(kind )
      SERIAL_ITEM(color)
      SERIAL_ITEM(style)
      SERIAL_ITEM(fill )
      SERIAL_ITEM(type )
   PROP_SERIAL_END()

   void write_tx(raw_pipeline_ostream& out) const
   {
      raw_write(out, r);
      raw_write(out, sa);
      raw_write(out, ea);
      raw_write(out, kind);
      raw_write(out, color);
      raw_write(out, style);
      raw_write(out, fill);
      raw_write(out, type);
   }
};

//////////////////////////////////////////////////////////////////////////

struct STREAM_Attrs : Common_Attrs<tx97::STREAM, tx97::TX_FL>
{
   STREAM_Attrs() = default;

   STREAM_Attrs ( const TxStruct* pTxStruct )
      : num ( pTxStruct->num )
   {
      memcpy_s(direction, sizeof(direction), pTxStruct->direction, sizeof(pTxStruct->direction));
      memcpy_s(speed,     sizeof(speed),     pTxStruct->speed,     sizeof(pTxStruct->speed));
   }

   struct
   {
      short dir = 0; // Оборачиваем для получения именованного (в шаблонах) и ссылочного (в cs) значения

      PROP_SERIAL_BEGIN()
         SERIAL_ITEM(dir)
      PROP_SERIAL_END()
   } direction[13] = {};

   struct
   {
      char syzygy = 0, quadrature = 0;

      PROP_SERIAL_BEGIN()
         SERIAL_ITEM( syzygy )
         SERIAL_ITEM( quadrature )
      PROP_SERIAL_END()
   } speed[13] = {};

   short num = 0;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM_AS_COLLECTION( direction )
      SERIAL_ITEM_AS_COLLECTION( speed )
      SERIAL_ITEM              ( num )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write(out, direction);
      raw_write(out, speed);
      raw_write(out, num);
   }
};

//////////////////////////////////////////////////////////////////////////

struct TEXT_Attrs : Common_Attrs<tx97::TEXT, tx97::TX_TX>
{
   TEXT_Attrs() = default;

   TEXT_Attrs ( const TxStruct* pTxStruct )
      : color ( pTxStruct->color )
      , s     ( TX97Convert::convert_from_tx_string(pTxStruct->s.Data, pTxStruct->s.N) )
   { }

   short color = 0;
   std::wstring  s;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( color )
      SERIAL_ITEM( s )
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, color );
      write_tx_string( out, s );
   }
};

//////////////////////////////////////////////////////////////////////////

struct InformationPage
{
   InformationPage ()
   {}

   InformationPage (const tx97::INFORMATION* pTxStruct)
   {
      // join information text lines into single string
      const unsigned char* pCurTrsString = reinterpret_cast<const unsigned char*>(pTxStruct->s);
      for (size_t i = 0; i < pTxStruct->num; ++i)
      {
         const tx97::TRS_STRING* pTrsString = reinterpret_cast<const tx97::TRS_STRING*>(pCurTrsString);
         std::wstring bs = TX97Convert::convert_from_tx_string(pTrsString->Data, pTrsString->N);
         strings.push_back(bs);
         pCurTrsString += pTrsString->N * sizeof(char) + sizeof(pTrsString->N);
      }
   }
   
   std::vector<std::wstring> strings;

   PROP_SERIAL_BEGIN()
      // TODO: array
      //SERIAL_ITEM(strings)
      SERIAL_ITEM_AS_COLLECTION(strings)
   PROP_SERIAL_END()

   void write_tx (raw_pipeline_ostream& out) const
   {
      // не совпадает с документом (в нем - два байта)
      const unsigned char num = static_cast<unsigned char>(__min(strings.size(), static_cast<size_t>(std::numeric_limits<unsigned char>::max())));
      raw_write(out, num);
      for (unsigned char i = 0; i < num; ++i)
         write_tx_string(out, strings[i].c_str());
   }
};


struct INFORMATION_Attrs : Common_Attrs<tx97::INFORMATION, tx97::TX_IN>
{
   INFORMATION_Attrs (short _type = 0)
      : type (_type)
      , pages (1)
   {}

   INFORMATION_Attrs (const TxStruct* pTxStruct)
      : type (pTxStruct->type)
   {
      // в TX хранится одна страница - массив строк
      pages.emplace_back(InformationPage(pTxStruct));
   }

   short type;
   // в CrtEditor объекты информации из TX могут объединяться в составные (многостраничные) объекты
   // (один объект TX - одна страница)
   std::vector<InformationPage> pages;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM           (type)
      SERIAL_ITEM_AS_COLLECTION(pages)
   PROP_SERIAL_END()

   void write_tx (raw_pipeline_ostream& out) const
   {
      raw_write(out, type);

      ATLASSERT(pages.size() == 1 || !"Составной объект должен разделяться раньше (так как геометрия записывается в другом месте)!");
      pages.front().write_tx(out);
   }
};

//////////////////////////////////////////////////////////////////////////

struct OTHER_OBJECT_Attrs : Common_Attrs<tx97::OTHER_OBJECT, tx97::TX_OT>
{
   OTHER_OBJECT_Attrs() = default;

   OTHER_OBJECT_Attrs ( const TxStruct* pTxStruct )
      : type ( pTxStruct->type )
   { }

   short type = 0;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM(type)
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, type );
   }
};

//////////////////////////////////////////////////////////////////////////

struct SEABED_NATURE_Attrs : Common_Attrs<tx97::SEABED_NATURE, tx97::TX_SB>
{
   SEABED_NATURE_Attrs() = default;
   SEABED_NATURE_Attrs ( const TxStruct* pTxStruct )
      : s ( TX97Convert::convert_from_tx_string(pTxStruct->s.Data, pTxStruct->s.N) )
   { }

   std::wstring  s;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM(s)
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      write_tx_string( out, s );
   }
};

//////////////////////////////////////////////////////////////////////////

struct HORISONTAL_LANDMARKS_Attrs : Common_Attrs<tx97::HORISONTAL_LANDMARKS, tx97::TX_HL>
{
   HORISONTAL_LANDMARKS_Attrs() = default;

   HORISONTAL_LANDMARKS_Attrs ( const TxStruct* pTxStruct )
      : depth ( TX97Convert::convert_from_tx_depth(pTxStruct->depth) )
      , type  ( pTxStruct->type )
   {
      //TODO: investigate
      // в слой HL_area попадают только мосты type == 2
//       if (type == 2)
//          _convLayer = CONV_TX_HL_AREA;
   }

   double depth = 0;  // Значение глубины / высоты (в метрах)
   short  type = 0;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM(depth)
      SERIAL_ITEM(type)
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, TX97Convert::convert_to_tx_depth(depth));
      raw_write( out, type );
   }
};

//////////////////////////////////////////////////////////////////////////

struct HEIGHT_Attrs : Common_Attrs<tx97::HEIGHT, tx97::TX_HG>
{
   HEIGHT_Attrs() = default;

   HEIGHT_Attrs ( const TxStruct* pTxStruct )
      : height ( TX97Convert::convert_from_tx_depth(pTxStruct->depth) )
      , type  ( pTxStruct->type )
   { }

   double height = 0;   // Значение высоты (в метрах)
   short  type = 0;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM(height)
      SERIAL_ITEM(type)
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      raw_write( out, TX97Convert::convert_to_tx_depth(height) );
      raw_write( out, type );
   }
};

//////////////////////////////////////////////////////////////////////////

struct COASTAL_FEATURE_Attrs : Common_Attrs<tx97::COASTAL_FEATURE, tx97::TX_HO>
{
   COASTAL_FEATURE_Attrs() = default;

   COASTAL_FEATURE_Attrs ( const TxStruct* pTxStruct )
      : color ( pTxStruct->color )
      , style ( pTxStruct->style )
      , type  ( pTxStruct->type )
      , fill  ( pTxStruct->fill )
   {
   }

   short color = 0;
   short style = 0;
   short fill  = 0;
   short type  = 0;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM(color )
      SERIAL_ITEM(style )
      SERIAL_ITEM(type )
      SERIAL_ITEM(fill)
   PROP_SERIAL_END()

   void write_tx( raw_pipeline_ostream& out ) const
   {
      raw_write(out, color);
      raw_write(out, style);
      raw_write(out, fill);
      raw_write(out, type);
   }
};


//////////////////////////////////////////////////////////////////////////

struct DESCRIPTION_Attrs
{
   typedef tx97::DESCRIPTION TxStruct;

   DESCRIPTION_Attrs ( )
   {
      memset( this, 0, sizeof(DESCRIPTION_Attrs) );

      ATLVERIFY( strcpy_s(Date_corr, "01-01-1991") == 0 );

      C0 = 5000;

      year_PD = 1991;
      month_PD = 1;

      year_PP = 1991;
      month_PP = 1;

      year_EC = 1991;
      month_EC = 1;

      Wgs = ' ';

      Datum = tx97::ellipsoid::WGS_84;
      Proj = tx97::projection::Mercator;

      LH_book = tx97::information_sourse::EnglishBook;
      Cntr    = tx97::chart_provider::England_P;
      CntG    = tx97::information_owner::NotDefined_I;
      LangP   = tx97::language::English;
      LangE   = tx97::language::English;
   }

   DESCRIPTION_Attrs ( const TxStruct* pTxStruct )
      : Delta_lat    ( TX97Convert::convert_from_tx_latlon(pTxStruct->Delta_lat) )
      , Delta_lon    ( TX97Convert::convert_from_tx_latlon(pTxStruct->Delta_lon) )
      , Delta_apply  ( false )
      , Latb         ( TX97Convert::convert_from_tx_latlon(pTxStruct->Latb) )
      , Late         ( TX97Convert::convert_from_tx_latlon(pTxStruct->Late) )
      , Lonb         ( TX97Convert::convert_from_tx_latlon(pTxStruct->Lonb) )
      , Lone         ( TX97Convert::convert_from_tx_latlon(pTxStruct->Lone) )
      , Latm         ( TX97Convert::convert_from_tx_latlon(pTxStruct->Latm) )
      , C0           ( pTxStruct->C0 )
      , year_PD      ( pTxStruct->year_PD  )
      , month_PD     ( pTxStruct->month_PD )
      , year_PP      ( pTxStruct->year_PP  )
      , month_PP     ( pTxStruct->month_PP )
      , year_EC      ( pTxStruct->year_EC  )
      , month_EC     ( pTxStruct->month_EC )
      , Wgs          ( pTxStruct->Wgs        )
      , DP_mean      ( pTxStruct->DP_mean    )
      , LH_book      ( pTxStruct->LH_book    )
      , Datum        ( pTxStruct->Datum      )
      , Proj         ( pTxStruct->Proj       )
      , Type         ( pTxStruct->Type       )
      , Cntr         ( pTxStruct->Cntr       )
      , LangP        ( pTxStruct->LangP      )
      , LangE        ( pTxStruct->LangE      )
      , Reg          ( pTxStruct->Reg        )
      , CntG         ( pTxStruct->CntG       )
      , compress     ( pTxStruct->compress   )
      , WaterLevel   ( pTxStruct->WaterLevel )
      , HO_mean      ( pTxStruct->HO_mean    )
      , TypeEx       ( pTxStruct->TypeEx     )
      , PubNum       ( pTxStruct->PubNum     )
      , CorrIssue    ( pTxStruct->CorrIssue  )
      , Revision     ( pTxStruct->Revision   )
   {
      memcpy_s( Date_corr,    sizeof(Date_corr),   pTxStruct->Date_corr,   sizeof(pTxStruct->Date_corr) );
      memcpy_s( Chart_name,   sizeof(Chart_name),  pTxStruct->Chart_name,  sizeof(pTxStruct->Chart_name) );
      memcpy_s( File_name,    sizeof(File_name),   pTxStruct->File_name,   sizeof(pTxStruct->File_name) );

      memcpy_s( Reserved,     sizeof(Reserved),    pTxStruct->Reserved,    sizeof(pTxStruct->Reserved) );
   }

   char     Date_corr[11]; // Дата последней коррекции
   char     Chart_name[9]; // Имя бумажной карты
   char     File_name[9];  // Имя электронной карты
   double   Delta_lat;     // Поправка по широте для перехода к WGS
   double   Delta_lon;     // Поправка по долготе для перехода к WGS
   bool     Delta_apply;   // (нет в TX) признак применения поправок
   double   Latb;          // Координаты углов карты - наименьшая широтa
   double   Late;          // Координаты углов карты - наибольшая широтa
   double   Lonb;          // Координаты углов карты - наименьшая долгота
   double   Lone;          // Координаты углов карты - наибольшая долгота
   double   Latm;          // Базовая широта
   double   C0;            // Масштаб исходной карты
   short    year_PD;       // Год издания бумажной карты
   short    month_PD;      // Месяц издания бумажной карты
   short    year_PP;       // Год печати бумажной карты
   short    month_PP;      // Месяц печати бумажной карты
   short    year_EC;       // Год изготовления электронной карты
   short    month_EC;      // Месяц изготовления электронной карты
   char     Wgs;           // Флаг для обработки WGS координат
   char     DP_mean;       // Единицы измерения глубины
   char     LH_book;       // Источник информации по секторам маяков
   char     Datum;         // Эллипсоид
   char     Proj;          // Проекция
   char     Type;          // Тип карты
   char     Cntr;          // Страна изготовитель бумажной карты
   char     LangP;         // Язык бумажной карты
   char     LangE;         // Язык электронной карты
   char     Reg;           // Регион МАМС/IALA
   char     CntG;          // Страна/гидрография владелец информации
   char     compress;      // Зарезервировано для обработки компрессии карты
   char     WaterLevel;    // Уровень воды
   char     HO_mean;       // Единицы измерения высоты
   char     TypeEx;        // Подтип карты (см. поле Type)
   char     PubNum;        // Номер издания карты
   char     CorrIssue;     // Номер выпуска последней внесенной корректуры
   char     Reserved[2];   // Зарезервировано (не используется)
   char     Revision;      // Редакция карты (должно быть равно 0)

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM( Date_corr );
      SERIAL_ITEM( Chart_name );
      SERIAL_ITEM( File_name );
      SERIAL_ITEM( Delta_lat );
      SERIAL_ITEM( Delta_lon );
      SERIAL_ITEM( Delta_apply );
      SERIAL_ITEM( Latb );
      SERIAL_ITEM( Late );
      SERIAL_ITEM( Lonb );
      SERIAL_ITEM( Lone );
      SERIAL_ITEM( Latm );
      SERIAL_ITEM( C0 );
      SERIAL_ITEM( year_PD );
      SERIAL_ITEM( month_PD );
      SERIAL_ITEM( year_PP );
      SERIAL_ITEM( month_PP );
      SERIAL_ITEM( year_EC );
      SERIAL_ITEM( month_EC );
      SERIAL_ITEM( Wgs );
      SERIAL_ITEM( DP_mean );
      SERIAL_ITEM( LH_book );
      SERIAL_ITEM( Datum );
      SERIAL_ITEM( Proj );
      SERIAL_ITEM( Type );
      SERIAL_ITEM( Cntr );
      SERIAL_ITEM( LangP );
      SERIAL_ITEM( LangE );
      SERIAL_ITEM( Reg );
      SERIAL_ITEM( CntG );
      SERIAL_ITEM( compress );
      SERIAL_ITEM( WaterLevel );
      SERIAL_ITEM( HO_mean );
      SERIAL_ITEM( TypeEx );
      SERIAL_ITEM( PubNum );
      SERIAL_ITEM( CorrIssue );
      SERIAL_NAMED_ITEM( L"Reserved0", Reserved[0] );
      SERIAL_NAMED_ITEM( L"Reserved1", Reserved[1] );
      SERIAL_ITEM( Revision );
   PROP_SERIAL_END()

   tx97::DESCRIPTION GetTxDesc ( ) const
   {
      tx97::DESCRIPTION desc;
      memset( &desc, 0, sizeof(tx97::DESCRIPTION) );

      memcpy_s( desc.Head, sizeof(desc.Head), "TRANSAS CE v6.0", 15 * sizeof(char) );

      memcpy_s( desc.Date_corr,  sizeof(desc.Date_corr),   Date_corr,  sizeof(Date_corr)  );
      memcpy_s( desc.Chart_name, sizeof(desc.Chart_name),  Chart_name, sizeof(Chart_name) );
      memcpy_s( desc.File_name,  sizeof(desc.File_name),   File_name,  sizeof(File_name)  );
      // TODO: react Delta_apply
      desc.Delta_lat     = TX97Convert::convert_to_tx_latlon(Delta_lat);
      desc.Delta_lon     = TX97Convert::convert_to_tx_latlon(Delta_lon);
      desc.Latb          = TX97Convert::convert_to_tx_latlon(Latb);
      desc.Late          = TX97Convert::convert_to_tx_latlon(Late);
      desc.Lonb          = TX97Convert::convert_to_tx_latlon(Lonb);
      desc.Lone          = TX97Convert::convert_to_tx_latlon(Lone);
      desc.Latm          = TX97Convert::convert_to_tx_latlon(Latm);
      desc.C0            = static_cast<float>(C0);
      desc.year_PD       = year_PD;
      desc.month_PD      = month_PD;
      desc.year_PP       = year_PP;
      desc.month_PP      = month_PP;
      desc.year_EC       = year_EC;
      desc.month_EC      = month_EC;
      desc.Wgs           = Wgs;
      desc.DP_mean       = DP_mean;
      desc.LH_book       = LH_book;
      desc.Datum         = Datum;
      desc.Proj          = Proj;
      desc.Type          = Type;
      desc.Cntr          = Cntr;
      desc.LangP         = LangP;
      desc.LangE         = LangE;
      desc.Reg           = Reg;
      desc.CntG          = CntG;
      desc.compress      = compress;
      desc.WaterLevel    = WaterLevel;
      desc.HO_mean       = HO_mean;
      desc.TypeEx        = TypeEx;
      desc.PubNum        = PubNum;
      desc.CorrIssue     = CorrIssue;
      memcpy_s( desc.Reserved, sizeof(desc.Reserved), Reserved, sizeof(Reserved) );
      desc.Revision      = Revision;

      return desc;
   }

   bool is_empty() const
   {
      return Latb == 0 && Late == 0 && Lonb == 0 && Lone == 0 && Latm == 0;
   }

   void write_tx ( raw_pipeline_ostream& out ) const { raw_write( out, GetTxDesc() ); }
};

//////////////////////////////////////////////////////////////////////////

struct TAIL_Attrs
{
   typedef tx97::TAIL TxStruct;

   TAIL_Attrs() = default;

   TAIL_Attrs ( const TxStruct* pTxStruct )
      : name (TX97Convert::convert_from_tx_string(pTxStruct->name.Data, pTxStruct->name.N) )
   { }

   std::wstring name;

   PROP_SERIAL_BEGIN()
      SERIAL_ITEM(name)
   PROP_SERIAL_END()

   void write_tx ( raw_pipeline_ostream& out ) const
   {
      write_tx_long_string( out, name );
   }
};

//////////////////////////////////////////////////////////////////////////

// структуры поддерживают вывод в стрим в TX97 формате

template<class TxStruct>
const tx97::TRS_GEO_POINT& extract_point ( const TxStruct* pTxStruct ) { return pTxStruct->point; }

template<>
inline const tx97::TRS_GEO_POINT& extract_point<tx97::LIGHTHOUSE_DESC> ( const tx97::LIGHTHOUSE_DESC* pTxStruct )
{
   return pTxStruct->pLighthouse->point;
}

template<>
inline const tx97::TRS_GEO_POINT& extract_point<tx97::BUOY_DESC> ( const tx97::BUOY_DESC* pTxStruct )
{
   return pTxStruct->pBuoy->point;
}

struct Base_Attrs_Struct
{
   virtual ~Base_Attrs_Struct() {};
   virtual void write_tx(raw_pipeline_ostream& out) const = 0;
   virtual std::vector<tx97::TRS_GEO_POINT> get_points() const = 0;
   virtual void put_points(std::vector<tx97::TRS_GEO_POINT>& points) = 0;
   props_on_map debug_serial_props;
};

template<class ObjAttrsStruct>
struct Point_Holder : ObjAttrsStruct, Base_Attrs_Struct
{
   typename typedef ObjAttrsStruct object_type;

   Point_Holder( ) { }

   Point_Holder( const typename ObjAttrsStruct::TxStruct* pTxStruct)
      : ObjAttrsStruct ( pTxStruct )
   {
      _point = extract_point(pTxStruct);
      PropsIO::Write(*this, debug_serial_props);
   }

   void write_tx ( raw_pipeline_ostream& out ) const override
   {
      // все точечные структуры имеют формат:
      // point
      // ... (другие поля)

      raw_write( out, _point );
      ObjAttrsStruct o;
      PropsIO::Read(o, debug_serial_props);
      o.write_tx(out);
      //      ObjAttrsStruct::write_tx( out );
   }

   virtual std::vector<tx97::TRS_GEO_POINT> get_points() const override
   {
      return {_point};
   }

   virtual void put_points(std::vector<tx97::TRS_GEO_POINT>& points) override
   {
       if (!points.empty())
           _point = points[0];
   }

protected:
   tx97::TRS_GEO_POINT _point;
};

template<class ObjAttrsStruct>
struct Linear_Holder : ObjAttrsStruct, Base_Attrs_Struct
{
   typedef typename ObjAttrsStruct object_type;

   Linear_Holder ( ) { }

   Linear_Holder ( const typename ObjAttrsStruct::TxStruct* pTxStruct )
      : ObjAttrsStruct ( pTxStruct )
   {
      _points.assign(pTxStruct->points, pTxStruct->points + pTxStruct->N);
      PropsIO::Write(*this, debug_serial_props);
   }

   void write_tx ( raw_pipeline_ostream& out ) const 
   {
      // все линейные структуры имеют формат:
      // N
      // ... (другие поля)
      // points

      ATLASSERT( _points.size() < static_cast<size_t>(std::numeric_limits<short>::max()) );
      const short N = static_cast<short>( _points.size() );
      raw_write( out, N );

      ObjAttrsStruct o;
      PropsIO::Read(o, debug_serial_props);
      o.write_tx( out );

      if ( !_points.empty() )
         out.write(_points.data(), sizeof(tx97::TRS_GEO_POINT) * N );
   }

   virtual std::vector<tx97::TRS_GEO_POINT> get_points() const override
   {
      return _points;
   }

   virtual void put_points(std::vector<tx97::TRS_GEO_POINT>& points) override
   {
       _points = points;
   }

private:
   std::vector<tx97::TRS_GEO_POINT> _points;
};

//////////////////////////////////////////////////////////////////////////

typedef Point_Holder<RACON_Attrs>            RACON_Holder;
typedef Point_Holder<DEPTHS_Attrs>           DEPTHS_Holder;
typedef Point_Holder<COVERED_HEIGHTS_Attrs>  COVERED_HEIGHTS_Holder;
typedef Point_Holder<ISOLATED_DANGER_Attrs>  ISOLATED_DANGER_Holder;
typedef Point_Holder<CIRCLE_Attrs>           CIRCLE_Holder;
typedef Point_Holder<STREAM_Attrs>           STREAM_Holder;
typedef Point_Holder<TEXT_Attrs>             TEXT_Holder;
typedef Point_Holder<INFORMATION_Attrs>      INFORMATION_Holder;
typedef Point_Holder<OTHER_OBJECT_Attrs>     OTHER_OBJECT_Holder;
typedef Point_Holder<SEABED_NATURE_Attrs>    SEABED_NATURE_Holder;
typedef Point_Holder<HEIGHT_Attrs>           HEIGHT_Holder;
typedef Point_Holder<LIGHTHOUSE_DESC_Attrs>  LIGHTHOUSE_DESC_Holder;
typedef Point_Holder<BUOY_DESC_Attrs>        BUOY_DESC_Holder;

typedef Linear_Holder<CHARTLET_Attrs>                    CHARTLET_Holder;
typedef Linear_Holder<COAST_LINE_Attrs>                  COAST_LINE_Holder;
typedef Linear_Holder<COVERS_AREA_Attrs>                 COVERS_AREA_Holder;
typedef Linear_Holder<ISOBATHS_Attrs>                    ISOBATHS_Holder;
//typedef Linear_Holder<ISOBATHS_Line_Attrs>               ISOBATHS_Line_Holder;
typedef Linear_Holder<LINE_Attrs>                        LINE_Holder;
//typedef Linear_Holder<LINE_Area_Attrs>                   LINE_Area_Holder;
typedef Linear_Holder<RECOMMENDED_ROUTE_Attrs>           RECOMMENDED_ROUTE_Holder;
typedef Linear_Holder<HORISONTAL_LANDMARKS_Attrs>        HORISONTAL_LANDMARKS_Holder;
//typedef Linear_Holder<HORISONTAL_LANDMARKS_Area_Attrs>   HORISONTAL_LANDMARKS_Area_Holder;
typedef Linear_Holder<COASTAL_FEATURE_Attrs>             COASTAL_FEATURE_Holder;
//typedef Linear_Holder<COASTAL_FEATURE_Area_Attrs>        COASTAL_FEATURE_Area_Holder;

#pragma pack ()

typedef std::vector< std::unique_ptr<Base_Attrs_Struct> > TRSLayerContent;
}