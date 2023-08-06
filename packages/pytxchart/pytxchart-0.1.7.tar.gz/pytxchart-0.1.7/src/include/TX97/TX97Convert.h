#pragma once
#include "windows.h"
#include "assert.h"
#include "vector"

#ifndef ATLASSERT
#define ATLASSERT(expr) assert(expr)
#endif // ATLASSERT

#ifndef ATLVERIFY
#ifdef _DEBUG
#define ATLVERIFY(expr) ATLASSERT(expr)
#else
#define ATLVERIFY(expr) (expr)
#endif // DEBUG
#endif // ATLVERIFY


namespace TX97Convert 
{
   //////////////////////////////////////////////////////////////////////////
   // conversions functions

   inline std::wstring convert_from_tx_string(const char* pSrc, unsigned szSrc)
   {
      if (szSrc == 0)
         return L"";

      const int charsCount = MultiByteToWideChar(866, MB_PRECOMPOSED, pSrc, szSrc, nullptr, 0);
      ATLASSERT(charsCount);
      if (charsCount)
      {
         std::vector<wchar_t> buf(charsCount + 1);
         MultiByteToWideChar(866, MB_PRECOMPOSED, pSrc, szSrc, buf.data(), static_cast<int>(buf.size()));
         return std::wstring(buf.data());
      }

      return L"";
   }

   template<size_t Size>
   std::wstring convert_from_tx_string(const char(&src)[Size])
   {
      return convert_from_tx_string(src, Size);
   }

   inline std::vector<char> convert_to_tx_string(const std::wstring& wstr)
   {
      if (wstr.empty())
         return std::vector<char>();

      std::vector<char> buf(WideCharToMultiByte(866, 0, wstr.c_str(), (int)wstr.length(), nullptr, 0, nullptr, nullptr));
      ATLASSERT(!buf.empty());
      if (!buf.empty())
         ATLVERIFY(WideCharToMultiByte(866, 0, wstr.c_str(), (int)wstr.length(), buf.data(), (int)buf.size(), nullptr, nullptr) == buf.size());

      return buf;
   }

   template<size_t Size>
   void convert_to_tx_string(const std::wstring& src, char(&dst)[Size])
   {
      memset(dst, 0, sizeof(dst));

      const std::vector<char> buf = convert_to_tx_string(src);
      if (!buf.empty())
         memcpy(dst, &buf[0], __min(buf.size(), Size));
   }

   //////////////////////////////////////////////////////////////////////////

   inline double convert_from_tx_depth(unsigned short depth)
   {
      return depth / 10.0;
   }

   inline unsigned short convert_to_tx_depth(double depth)
   {
      return static_cast<unsigned short>(round(depth * 10));
   }

   //////////////////////////////////////////////////////////////////////////

   inline double convert_from_tx_dir(unsigned short dir)
   {
      return dir / 10.0;
   }

   inline unsigned short convert_to_tx_dir(double dir)
   {
      return static_cast<unsigned short>(round(dir * 10));
   }

   //////////////////////////////////////////////////////////////////////////

   inline double convert_from_tx_height(char val)
   {
      return (val < 0 ? __max(abs(val) * 10 + 100, 128) : val);
   }

   inline char convert_to_tx_height(double val)
   {
      const int intVal = static_cast<int>(round(val));
      return intVal > 127 ? static_cast<char>(-(intVal - 100) / 10) : static_cast<char>(intVal);
   }

   //////////////////////////////////////////////////////////////////////////

   inline double convert_from_tx_duration(char val)
   {
      return (val < 0 ? __max(abs(val) * 10 + 100, 128) : val) / 10.0;
   }

   inline char convert_to_tx_duration(double val)
   {
      const int intVal = static_cast<int>(round(val * 10));
      return intVal > 127 ? static_cast<char>(-(intVal - 100) / 10) : static_cast<char>(intVal);
   }

   //////////////////////////////////////////////////////////////////////////

   inline double convert_from_tx_latlon(float val)
   {
      return val / 60.0;
   }

   inline float convert_to_tx_latlon(double val)
   {
      return static_cast<float>(val * 60);
   }

   //////////////////////////////////////////////////////////////////////////

   template<typename TX97DESCRIPTION>
   bool is_iTx_chart(const TX97DESCRIPTION* pTxDesc)
   {
      const char iTxType = 6;
      return pTxDesc->Type == iTxType;
   }

   template<typename TX97DESCRIPTION>
   void set_iTx_chart(TX97DESCRIPTION* pTxDesc)
   {
      const char iTxType = 6;
      pTxDesc->Type = iTxType;
      pTxDesc->TypeEx = 0;
   }

}