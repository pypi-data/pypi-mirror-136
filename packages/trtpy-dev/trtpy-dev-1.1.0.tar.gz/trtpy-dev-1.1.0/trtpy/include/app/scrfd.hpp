#ifndef SCRFD_HPP
#define SCRFD_HPP

#include <vector>
#include <memory>
#include <string>
#include <future>
#include <common/face_detector.hpp>
#include <common/trt_image.hpp>

namespace Scrfd{

    using namespace std;
    using namespace FaceDetector;

    class Infer{
    public:
        virtual shared_future<BoxArray> commit(const TRT::ImageBGR8U& image) = 0;
        virtual vector<shared_future<BoxArray>> commits(const vector<TRT::ImageBGR8U>& images) = 0;
    };

    shared_ptr<Infer> create_infer(const string& engine_file, int gpuid, float confidence_threshold=0.5f, float nms_threshold=0.5f);

}; // namespace Scrfd

#endif // SCRFD_HPP