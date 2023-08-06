import torch
import torch.nn as nn
from torch import tensor
from torch.nn import Module
from torch.autograd import Function

__all__ = ['GradNorm']


class ScaleGrad_func(Function):
  @staticmethod
  def forward(ctx, input_, alpha_, debug_):
    ctx.save_for_backward(input_, alpha_, debug_)
    output = input_
    return output

  @staticmethod
  def backward(ctx, grad_output):  # pragma: no cover
    grad_input = None
    _, alpha_, debug_ = ctx.saved_tensors
    if ctx.needs_input_grad[0]:
      # grad_input = -grad_output * alpha_
      # grad_input = grad_output * alpha_

      total_norm = torch.norm(grad_output).item()



      if total_norm >= 1e-5:
        # clip_coef = alpha_ / (total_norm + 1e-6)
        clip_coef = alpha_ / total_norm
        grad_input = grad_output * clip_coef
        if debug_:
          print(f"{total_norm} -> {alpha_}")

      else:
        grad_input = grad_output
        if debug_:
          print(f"{total_norm} -> unchanged")

    return grad_input, None, None


scalegrad = ScaleGrad_func.apply


class GradNorm(Module):
  def __repr__(self):
    return f"{self.__class__.__name__}({self.repr_str})"

  def __init__(self,
               norm=1.,
               *args,
               **kwargs):
    """
    This layer has no parameters, and simply scale the gradient in the backward pass.

    """
    super(GradNorm, self).__init__(*args, **kwargs)

    self.repr_str = f"norm={norm}"

    self._norm = tensor(norm, requires_grad=False)
    pass

  def forward(self, input_, debug=False):

    debug = tensor(debug, requires_grad=False)

    return scalegrad(input_, self._norm, debug)
