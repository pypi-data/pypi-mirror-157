#pragma once
#include <iostream>
#include <fstream>
#include <vector>
#include "memory_stream.h"

#undef max
#undef min
using raw_pipeline_ostream = memory_stream;

inline std::vector<char> read_file_to_buffer(const char* filePath)
{
   std::ifstream file(filePath, std::ios::binary | std::ios::ate);
   if (!file.is_open())
      return std::vector<char>();
   std::streamsize size = file.tellg();
   file.seekg(0, std::ios::beg);

   std::vector<char> buffer(size);
   return file.read(buffer.data(), size) ? buffer : std::vector<char>();
}

inline bool write_buffer_to_file(const char* data, size_t size, const char* filePath)
{
   std::ofstream fs(filePath, std::ios::out | std::ios::binary);
   if (!fs)
      return false;
   fs.write(data, size);
   return !fs.bad();
}


