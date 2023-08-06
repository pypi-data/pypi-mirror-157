#pragma once
//https://stackoverflow.com/questions/2573834/c-convert-string-or-char-to-wstring-or-wchar-t

inline std::wstring string_to_wstring(const std::string& s)
{
   return std::wstring(s.begin(), s.end());
}

inline std::string wstring_to_string(const std::wstring& s)
{
   //suppress warning C4244: 'argument': conversion from 'const wchar_t' to 'const _Elem', possible loss of data
   //return std::string(s.begin(), s.end());

   std::string str;
   std::transform(s.begin(), s.end(), std::back_inserter(str), [](wchar_t c) { return (char)c; });

   return str;
}

