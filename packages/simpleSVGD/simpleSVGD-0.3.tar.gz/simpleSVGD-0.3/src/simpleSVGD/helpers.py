import torch


def TorchWrapper(g_fn, kernel):
    class _internalClass(torch.autograd.Function):
        @staticmethod
        def forward(ctx, input):
            ctx.save_for_backward(input)
            return input.type(torch.FloatTensor)

        @staticmethod
        def backward(ctx, grad_output):
            (input,) = ctx.saved_tensors

            kxy, dxkxy = kernel(input.numpy(), h=-1)

            K = torch.from_numpy(kxy).type(torch.FloatTensor)
            dk = torch.from_numpy(dxkxy).type(torch.FloatTensor)

            return grad_output * (
                K
                @ torch.from_numpy(g_fn(input.numpy())).type(torch.FloatTensor)
                - dk
            ).type(torch.FloatTensor)

    return _internalClass.apply
