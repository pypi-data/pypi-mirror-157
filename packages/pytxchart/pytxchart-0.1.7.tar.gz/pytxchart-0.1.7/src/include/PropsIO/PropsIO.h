#pragma once
#include <vector>
#include "..\props_on_map.h"

namespace PropsIO
{
   enum class Mode
   {
      Read,
      Write
   };
}

   //////////////////////////////////////////////////////////////////////////
#define PROP_SERIAL_BEGIN()                                  \
   template<class TProps>                                    \
   void PropSerialization(PropsIO::Mode mode, TProps& props) \
   {                                                         \

//////////////////////////////////////////////////////////////////////////
#define PROP_SERIAL_END()                                    \
   }                                                         \

//////////////////////////////////////////////////////////////////////////
#define SERIAL_NAMED_ITEM(itemName, itemValue)                \
   if (mode == PropsIO::Mode::Read)                           \
   {                                                          \
      PropsIO::get(itemName, itemValue, props);               \
   }                                                          \
   else                                                       \
   {                                                          \
      PropsIO::put(itemName, itemValue, props);               \
   }                                                          \

#define SERIAL_ITEM(itemValue) SERIAL_NAMED_ITEM(L#itemValue, itemValue)

#define SERIAL_NAMED_ITEM_ENUM(itemName, itemValue, EnumType)     \
   if (mode == PropsIO::Mode::Read)                               \
   {                                                              \
      unsigned int val;                                           \
      PropsIO::get(itemName, itemValue, props)                    \
      itemValue = static_cast<EnumType>(val);                     \
   }                                                              \
   else                                                           \
   {                                                              \
      PropsIO::put(itemName, unsigned int(itemValue), props)      \
   }                                                              \

#define SERIAL_NAMED_ITEM_AS_COLLECTION(itemName, itemValue)                 \
   if (mode == PropsIO::Mode::Read)                                          \
   {                                                                         \
      PropsIO::get_as_collection(itemName, itemValue, props);                \
   }                                                                         \
   else                                                                      \
   {                                                                         \
      PropsIO::put_as_collection(itemName, itemValue, props);                \
   }                                                                         \

#define SERIAL_ITEM_AS_COLLECTION(itemValue) SERIAL_NAMED_ITEM_AS_COLLECTION(L#itemValue, itemValue)

//////////////////////////////////////////////////////////////////////////

namespace PropsIO
{
   template <class T, class PropsType>
   void Read(T& obj, const PropsType& from)
   {
      obj.PropSerialization(Mode::Read, const_cast<PropsType&>(from));
   }

   template <class T, class PropsType>
   void Write(const T& obj, PropsType& to)
   {
      const_cast<T&>(obj).PropSerialization(Mode::Write, to);
   }

   // struct
   template<class ValueType, class PropsType>
   void put(const wchar_t* name, const ValueType& value, PropsType& props)
   {
      auto branch = PropSerialTraits::create_branch(props, name);
      const_cast<ValueType&>(value).PropSerialization(Mode::Write, branch);
   }

   template<class ValueType, class PropsType>
   bool get(const wchar_t* name, ValueType& value, PropsType& props)
   {
      auto branch = PropSerialTraits::get_branch(props, name);
      if (!PropSerialTraits::is_valid(branch))
         return false;

      value.PropSerialization(Mode::Read, branch);
      return true;
   }
}

#define SIMPLE_PROPS_REPR(TypeName)                                              \
namespace PropsIO                                                             \
{                                                                                \
   template<class PropsType>                                                     \
   inline void put(const wchar_t* name, const TypeName& value, PropsType& props) \
   {                                                                             \
      PropSerialTraits::put_item(name, value, props);                            \
   }                                                                             \
   template<class PropsType>                                                     \
   inline bool get(const wchar_t* name, TypeName& value, PropsType& props)       \
   {                                                                             \
      return PropSerialTraits::get_item(name, value, props);                            \
   }                                                                             \
}                                                                                \

SIMPLE_PROPS_REPR(float);
SIMPLE_PROPS_REPR(double);
SIMPLE_PROPS_REPR(char);
SIMPLE_PROPS_REPR(short);
SIMPLE_PROPS_REPR(int);
SIMPLE_PROPS_REPR(long);
SIMPLE_PROPS_REPR(unsigned char);
SIMPLE_PROPS_REPR(unsigned short);
SIMPLE_PROPS_REPR(unsigned int);
SIMPLE_PROPS_REPR(unsigned long);
SIMPLE_PROPS_REPR(bool);
SIMPLE_PROPS_REPR(std::wstring);



namespace PropsIO
{
   template<class Iter, class PropsType>
   void put_as_collection(const wchar_t* name, const Iter& begin, const Iter& end, PropsType& props)
   {
      auto collectionBranch = PropSerialTraits::create_branch(props, name);
      for (Iter it = begin; it != end; ++it)
      {
         wchar_t itemName[128];
         swprintf_s(itemName, L"#%Iu", std::distance(begin, it)); // нумерация обязательно #n где n-число, #0000n не допускается. Для поддержки в PropertyGrid
         put(itemName, *it, collectionBranch);
      }
   }

   template<class ValueType, class PropsType>
   void put_as_collection(const wchar_t* name, const std::vector< ValueType>& v, PropsType& props)
   {
      put_as_collection(name, v.begin(), v.end(), props);
   }

   // static array as collection
   template<class ValueType, size_t Count, class PropsType>
   void put_as_collection(const wchar_t* name, const ValueType(&values)[Count], PropsType& props)
   {
      put_as_collection(name, &values[0], &values[0] + Count, props);
   }

   // sequence as collection
   template<class ElementType, class ElementIter, class PropsType>
   void get_as_collection(const wchar_t* name, ElementIter out, PropsType& props)
   {
      PropsType collectionBranch = PropSerialTraits::get_branch(props, name);
      if (PropSerialTraits::is_valid(collectionBranch))
      {
         size_t i = 0;
         wchar_t itemName[128];
         swprintf_s(itemName, L"#%zu", i);
         ElementType newElement;
         while (get(itemName, newElement, collectionBranch))
         {
            *out++ = newElement;
            swprintf_s(itemName, L"#%zu", ++i);
         }
      }
   }

   template<class ElementType, class PropsType>
   void get_as_collection(const wchar_t* name, std::vector<ElementType>& values, PropsType& props)
   {
      values.clear();
      get_as_collection<ElementType>(name, std::back_inserter(values), props);
   }

   template<class ElementType, size_t Count, class PropsType>
   void get_as_collection(const wchar_t* name, ElementType(&values)[Count], PropsType& props)
   {
      // casting to pointer to prevent recursive call
      get_as_collection<ElementType>(name, static_cast<ElementType*>(values), props);
   }


}
