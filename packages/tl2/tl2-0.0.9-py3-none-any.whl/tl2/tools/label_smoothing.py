import torch
import torch.nn as nn
import torch.nn.functional as F

# """
# https://stackoverflow.com/questions/55681502/label-smoothing-in-pytorch
#
# """


class LabelSmoothingLoss(torch.nn.Module):
  def __init__(self,
               reduction="mean",
               weight=None):
    super(LabelSmoothingLoss, self).__init__()

    self.reduction = reduction
    self.weight = weight
    pass

  def reduce_loss(self, loss):
    return loss.mean() if self.reduction == 'mean' else loss.sum() \
      if self.reduction == 'sum' else loss

  def linear_combination(self,
                         x,
                         y,
                         smoothing):
    return smoothing * x + (1 - smoothing) * y

  def forward(self,
              preds,
              target,
              smoothing=0.1):
    assert 0 <= smoothing < 1

    if self.weight is not None:
      self.weight = self.weight.to(preds.device)

    n = preds.size(-1)
    log_preds = F.log_softmax(preds, dim=-1)
    loss = self.reduce_loss(-log_preds.sum(dim=-1))

    nll = F.nll_loss(log_preds, target, reduction=self.reduction, weight=self.weight)

    return self.linear_combination(loss / n, nll, smoothing=smoothing)



class LabelSmoothing(nn.Module):
  """NLL loss with label smoothing.
  """

  def __init__(self):
    """Constructor for the LabelSmoothing module.
    :param smoothing: label smoothing factor
    """
    super(LabelSmoothing, self).__init__()

    pass

  def forward(self,
              x,
              target,
              smoothing=0.1):
    """

    :param x: (b, c)
    :param target:  (b, )
    :param smoothing:
    :return:
    """
    confidence = 1.0 - smoothing

    logprobs = torch.nn.functional.log_softmax(x, dim=-1)
    nll_loss = -logprobs.gather(dim=-1, index=target.unsqueeze(1))
    nll_loss = nll_loss.squeeze(1)
    smooth_loss = -logprobs.mean(dim=-1)
    loss = confidence * nll_loss + smoothing * smooth_loss
    return loss.mean()


if __name__=="__main__":
    # Wangleiofficial

    predict = torch.tensor([[0, 0.2, 0.7, 0.1, 0],
                            [0, 0.9, 0.2, 0.2, 1],
                            [1, 0.2, 0.7, 0.9, 1]])
    label = torch.tensor([2, 1, 0])

    crit1 = LabelSmoothingLoss(reduction="mean")
    v1 = crit1(predict, label, smoothing=0.3, )

    # NVIDIA
    crit2 = LabelSmoothing()
    v2 = crit2(predict, label, smoothing=0.3)

    assert v1 == v2
    pass

