#include <complex>
#include <iostream>
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/op_kernel.h"


REGISTER_OP("Arg")
    .Input("complex: complex128")
    .Output("arg: float64");

using namespace tensorflow;


class ArgOp : public OpKernel {

    public:

        explicit ArgOp(OpKernelConstruction* context) : OpKernel(context) {}

        void Compute(OpKernelContext* context) override {
            // Grab the input tensor
            const Tensor& input_tensor = context->input(0);
            auto input = input_tensor.flat<complex128>();

            // Create an output tensor
            Tensor* output_tensor = NULL;
            OP_REQUIRES_OK(
                context,
                context->allocate_output(
                    0, input_tensor.shape(), &output_tensor
                    ));
            auto output = output_tensor->template flat<double>();

            // compute the output values
            const int N = input.size();
            for (int i = 0; i < N; i++) {
                output(i) = std::arg(input(i));
            }
        }
};


REGISTER_KERNEL_BUILDER(Name("Arg").Device(DEVICE_CPU), ArgOp);
