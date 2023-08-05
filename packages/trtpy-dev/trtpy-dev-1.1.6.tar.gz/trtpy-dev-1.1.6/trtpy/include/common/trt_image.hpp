#ifndef TRT_IMAGE_HPP
#define TRT_IMAGE_HPP

namespace TRT{

class Size{
public:
    Size() = default;
    Size(int width, int height){
        this->width = width;
        this->height = height;
    }

    int width = 0;
    int height = 0;
};

class ImageBGR8U{
public:
    ImageBGR8U(){
    }

    ImageBGR8U(int height, int width, const void* pdata){
        this->pdata_ = (unsigned char*)(pdata);
        this->width_ = width;
        this->height_ = height;
        this->rows = this->height_;
        this->cols = this->width_;
    }

    const int width() const{ return width_; }
    const int height() const{ return height_; }
    const unsigned char* data() const{ return pdata_; }
    const Size size() const{ return Size(width_, height_); }
    const bool empty() const{ return this->pdata_ == nullptr || this->width_ == 0 || this->height_ == 0; }

public:
    int rows = 0;
    int cols = 0;

private:
    int width_ = 0;
    int height_ = 0;
    unsigned char* pdata_ = nullptr;
};

inline void invertAffineTransform(float imat[6], float omat[6]){

    float i00 = imat[0];  float i01 = imat[1];  float i02 = imat[2];
    float i10 = imat[3];  float i11 = imat[4];  float i12 = imat[5];

    float D = i00 * i11 - i01 * i10;
    D = D != 0 ? 1.0 / D : 0;

    float A11 = i11 * D;
    float A22 = i00 * D;
    float A12 = -i01 * D;
    float A21 = -i10 * D;
    float b1 = -A11 * i02 - A12 * i12;
    float b2 = -A21 * i02 - A22 * i12;
    omat[0] = A11;  omat[1] = A12;  omat[2] = b1;
    omat[3] = A21;  omat[4] = A22;  omat[5] = b2;
}

}; // namespace TRT

#endif // TRT_IMAGE_HPP