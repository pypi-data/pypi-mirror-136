/*
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef NV_ONNX_PARSER_H
#define NV_ONNX_PARSER_H

#include "NvInfer.h"
#include <stddef.h>
#include <vector>
#include <functional>
#include <string>

//!
//! \file NvOnnxParser.h
//!
//! This is the API for the ONNX Parser
//!

#define NV_ONNX_PARSER_MAJOR 0
#define NV_ONNX_PARSER_MINOR 1
#define NV_ONNX_PARSER_PATCH 0

static const int NV_ONNX_PARSER_VERSION = ((NV_ONNX_PARSER_MAJOR * 10000) + (NV_ONNX_PARSER_MINOR * 100) + NV_ONNX_PARSER_PATCH);

//! \typedef SubGraph_t
//!
//! \brief The data structure containing the parsing capability of
//! a set of nodes in an ONNX graph.
//!
typedef std::pair<std::vector<size_t>, bool> SubGraph_t;

//! \typedef SubGraphCollection_t
//!
//! \brief The data structure containing all SubGraph_t partitioned
//! out of an ONNX graph.
//!
typedef std::vector<SubGraph_t> SubGraphCollection_t;

//!
//! \namespace nvonnxparser
//!
//! \brief The TensorRT ONNX parser API namespace
//!
namespace nvonnxparser
{

template <typename T>
inline int32_t EnumMax();

/** \enum ErrorCode
 *
 * \brief the type of parser error
 */
enum class ErrorCode : int
{
    kSUCCESS = 0,
    kINTERNAL_ERROR = 1,
    kMEM_ALLOC_FAILED = 2,
    kMODEL_DESERIALIZE_FAILED = 3,
    kINVALID_VALUE = 4,
    kINVALID_GRAPH = 5,
    kINVALID_NODE = 6,
    kUNSUPPORTED_GRAPH = 7,
    kUNSUPPORTED_NODE = 8
};

template <>
inline int32_t EnumMax<ErrorCode>()
{
    return 9;
}

/** \class IParserError
 *
 * \brief an object containing information about an error
 */
class IParserError
{
public:
    /** \brief the error code
     */
    virtual ErrorCode code() const = 0;
    /** \brief description of the error
     */
    virtual const char* desc() const = 0;
    /** \brief source file in which the error occurred
     */
    virtual const char* file() const = 0;
    /** \brief source line at which the error occurred
     */
    virtual int line() const = 0;
    /** \brief source function in which the error occurred
     */
    virtual const char* func() const = 0;
    /** \brief index of the ONNX model node in which the error occurred
     */
    virtual int node() const = 0;

protected:
    virtual ~IParserError() {}
};

/** \class IParser
 *
 * \brief an object for parsing ONNX models into a TensorRT network definition
 */
class IParser
{
public:
    /** \brief Parse a serialized ONNX model into the TensorRT network.
     *         This method has very limited diagnostics. If parsing the serialized model
     *         fails for any reason (e.g. unsupported IR version, unsupported opset, etc.)
     *         it the user responsibility to intercept and report the error.
     *         To obtain a better diagnostic, use the parseFromFile method below.
     *
     * \param serialized_onnx_model Pointer to the serialized ONNX model
     * \param serialized_onnx_model_size Size of the serialized ONNX model
     *        in bytes
     * \param model_path Absolute path to the model file for loading external weights if required
     * \return true if the model was parsed successfully
     * \see getNbErrors() getError()
     */
    virtual bool parse(void const* serialized_onnx_model,
                       size_t serialized_onnx_model_size,
                       const char* model_path = nullptr)
        = 0;

    /** \brief Parse an onnx model file, which can be a binary protobuf or a text onnx model
     *         calls parse method inside.
     *
     * \param File name
     * \param Verbosity Level
     *
     * \return true if the model was parsed successfully
     *
     */
    virtual bool parseFromFile(const char* onnxModelFile, int verbosity) = 0;
    virtual bool parseFromData(const void* onnx_data, size_t size, int verbosity) = 0;

    /** \brief Check whether TensorRT supports a particular ONNX model
     *
     * \param serialized_onnx_model Pointer to the serialized ONNX model
     * \param serialized_onnx_model_size Size of the serialized ONNX model
     *        in bytes
     * \param sub_graph_collection Container to hold supported subgraphs
     * \param model_path Absolute path to the model file for loading external weights if required
     * \return true if the model is supported
     */
    virtual bool supportsModel(void const* serialized_onnx_model,
                               size_t serialized_onnx_model_size,
                               SubGraphCollection_t& sub_graph_collection,
                               const char* model_path = nullptr)
        = 0;

    /** \brief Parse a serialized ONNX model into the TensorRT network
     * with consideration of user provided weights
     *
     * \param serialized_onnx_model Pointer to the serialized ONNX model
     * \param serialized_onnx_model_size Size of the serialized ONNX model
     *        in bytes
     * \return true if the model was parsed successfully
     * \see getNbErrors() getError()
     */
    virtual bool parseWithWeightDescriptors(
        void const* serialized_onnx_model, size_t serialized_onnx_model_size)
        = 0;

    /** \brief Returns whether the specified operator may be supported by the
     *         parser.
     *
     * Note that a result of true does not guarantee that the operator will be
     * supported in all cases (i.e., this function may return false-positives).
     *
     * \param op_name The name of the ONNX operator to check for support
     */
    virtual bool supportsOperator(const char* op_name) const = 0;
    /** \brief destroy this object
     *
     * \warning deprecated and planned on being removed in TensorRT 10.0
     */
    TRT_DEPRECATED virtual void destroy() = 0;
    /** \brief Get the number of errors that occurred during prior calls to
     *         \p parse
     *
     * \see getError() clearErrors() IParserError
     */
    virtual int getNbErrors() const = 0;
    /** \brief Get an error that occurred during prior calls to \p parse
     *
     * \see getNbErrors() clearErrors() IParserError
     */
    virtual IParserError const* getError(int index) const = 0;
    /** \brief Clear errors from prior calls to \p parse
     *
     * \see getNbErrors() getError() IParserError
     */
    virtual void clearErrors() = 0;

    virtual ~IParser() noexcept = default;
};

} // namespace nvonnxparser

extern "C" TENSORRTAPI void* createNvOnnxParser_INTERNAL(void* network, void* logger, int version, const std::vector<nvinfer1::Dims>& input_dims);
extern "C" TENSORRTAPI int getNvOnnxParserVersion();
extern "C" TENSORRTAPI void register_layerhook_reshape(const std::function<std::vector<int64_t>(const std::string& name, const std::vector<int64_t>& shape)>&);

namespace nvonnxparser
{

namespace
{

/** \brief Create a new parser object
 *
 * \param network The network definition that the parser will write to
 * \param logger The logger to use
 * \return a new parser object or NULL if an error occurred
 *
 * Any input dimensions that are constant should not be changed after parsing,
 * because correctness of the translation may rely on those constants.
 * Changing a dynamic input dimension, i.e. one that translates to -1 in
 * TensorRT, to a constant is okay if the constant is consistent with the model.
 *
 * \see IParser
 */
inline IParser* createParser(nvinfer1::INetworkDefinition& network, nvinfer1::ILogger& logger, const std::vector<nvinfer1::Dims>& input_dims={})
{
    return static_cast<IParser*>(createNvOnnxParser_INTERNAL(&network, &logger, NV_ONNX_PARSER_VERSION, input_dims));
}

} // namespace

} // namespace nvonnxparser

#endif // NV_ONNX_PARSER_H
