#pragma once

#include <vector>

struct memory_stream 
{
   memory_stream() : pos_ ( 0 ) {}

   memory_stream& write(const void * data, unsigned int size)
    {
        if ( !size )
            return *this;
        if ( data_.size () < pos_ + size ) 
            data_.resize(pos_ + size) ; 
        memcpy ( &data_[pos_], data, size ) ; 
        pos_ += size ;  
        return *this;
    }

    unsigned int getPos() const
    {
        return pos_ ; 
    }

    void setPos(unsigned int position)
    {
        if ( data_.size () < position ) 
            data_.resize(position) ; 
        pos_ = position; 
    }

    struct rawdata 
    {
        void swap ( std::vector<unsigned char>& data )
        {
            std::swap ( data, data_ ) ; 
        }
        const unsigned char * data () const 
        {
            if ( data_.size( ) )
               return &data_[0] ; 

            return NULL;
        }

        size_t size () const 
        {    
            return data_.size() ; 
        }
    private : 
        std::vector<unsigned char> data_;
    } ; 

    template<class RD>
    void flush_to( RD& dst ) 
    {
        pos_ = 0 ; 
        dst.swap(data_);
    } 

    void clear()
    {
        pos_ = 0;
        data_.resize(0);
    }

    unsigned int       getSize() const { return (unsigned int)data_.size(); }
    unsigned char const *getData() const { return data_.data(); }

    void reserve(size_t count)
    {
       data_.reserve(count);
    }

protected:
    std::vector<unsigned char> data_;
    unsigned int             pos_ ;
};

template<class T>
void raw_write(memory_stream& out, const T& t)
{
   out.write(&t, sizeof(T));
}

