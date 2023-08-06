#pragma once
#include <map>
#include <any>

struct props_on_map
{
   using container_type = std::map<std::wstring, std::any>;
   using container_ptr = std::shared_ptr<container_type>;
   container_ptr container = std::make_shared<container_type>();
   bool is_valid() const 
   {
      return (bool)container;
   }
};

// implementation
namespace PropSerialTraits
{
   inline bool is_valid(const props_on_map& props)
   {
      return props.is_valid();
   }

   template<class T>
   bool get_item(const wchar_t* itemName, T& itemValue, const props_on_map& props)
   {
      auto it = props.container->find(itemName);
      if (it == props.container->end())
         return false;
      itemValue = std::any_cast<T>(it->second);
      return true;
   }

   template<class T>
   void put_item(const wchar_t* itemName, T itemValue, props_on_map& props)
   {
      props.container->insert(std::make_pair(itemName, itemValue));
   }
   
   template<class ElementIter>
   inline void put_array(const wchar_t* itemName, ElementIter begin, ElementIter end, props_on_map& props)
   {
      //std::vector<std::any> v;
      //for (auto it = begin; it != end; ++it )
      //{
      //   props_on_map elemProps;
      //   props.container->insert(std::make_pair(name, result.container));

      //}
      assert(!"put_array not implemented yet");
   }

   inline props_on_map create_branch(props_on_map& props, const wchar_t* name)
   {
      props_on_map result;
      props.container->insert(std::make_pair(name, result.container));
      return result;
   }

   inline props_on_map get_branch(props_on_map& props, const wchar_t* name)
   {
      auto it = props.container->find(name);
      return props_on_map{ it != props.container->end() 
         ? std::any_cast<props_on_map::container_ptr>(it->second) 
         : nullptr };
   }
}

