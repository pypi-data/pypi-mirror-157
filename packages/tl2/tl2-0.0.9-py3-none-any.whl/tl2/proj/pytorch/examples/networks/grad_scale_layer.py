from torch import tensor
from torch.nn import Module
from torch.autograd import Function

__all__ = ['GradScale']


class ScaleGrad_func(Function):
  @staticmethod
  def forward(ctx, input_, alpha_):
    ctx.save_for_backward(input_, alpha_)
    output = input_
    return output

  @staticmethod
  def backward(ctx, grad_output):  # pragma: no cover
    grad_input = None
    _, alpha_ = ctx.saved_tensors
    if ctx.needs_input_grad[0]:
      # grad_input = -grad_output * alpha_
      grad_input = grad_output * alpha_
    return grad_input, None


scalegrad = ScaleGrad_func.apply


class GradScale(Module):
  def __repr__(self):
    return f"{self.__class__.__name__}({self.repr_str})"

  def __init__(self,
               alpha=1.,
               *args,
               **kwargs):
    """
    This layer has no parameters, and simply scale the gradient in the backward pass.

    """
    super(GradScale, self).__init__(*args, **kwargs)

    self.repr_str = f"alpha={alpha:.3f}, alpha=1/{1 / alpha:.3f}"

    self._alpha = tensor(alpha, requires_grad=False)
    pass

  def forward(self, input_):
    return scalegrad(input_, self._alpha)
