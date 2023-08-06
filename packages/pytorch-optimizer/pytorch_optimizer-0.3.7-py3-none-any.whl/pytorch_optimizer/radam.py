import math
from typing import Dict

import torch
from torch.optim.optimizer import Optimizer

from pytorch_optimizer.types import BETAS, BUFFER, CLOSURE, DEFAULTS, LOSS, PARAMETERS
from pytorch_optimizer.utils import is_valid_parameters


class RAdam(Optimizer):
    """
    Reference : https://github.com/LiyuanLucasLiu/RAdam/
    Example :
        from pytorch_optimizer import RAdam
        ...
        model = YourModel()
        optimizer = RAdam(model.parameters())
        ...
        for input, output in data:
          optimizer.zero_grad()
          loss = loss_function(output, model(input))
          loss.backward()
          optimizer.step()
    """

    def __init__(
        self,
        params: PARAMETERS,
        lr: float = 1e-3,
        betas: BETAS = (0.9, 0.999),
        weight_decay: float = 0.0,
        n_sma_threshold: int = 5,
        degenerated_to_sgd: bool = False,
        adamd_debias_term: bool = False,
        eps: float = 1e-8,
    ):
        """RAdam
        :param params: PARAMETERS. iterable of parameters to optimize or dicts defining parameter groups
        :param lr: float. learning rate
        :param betas: BETAS. coefficients used for computing running averages of gradient and the squared hessian trace
        :param weight_decay: float. weight decay (L2 penalty)
        :param n_sma_threshold: int. (recommended is 5)
        :param degenerated_to_sgd: float. degenerated to SGD
        :param adamd_debias_term: bool. Only correct the denominator to avoid inflating step sizes early in training
        :param eps: float. term added to the denominator to improve numerical stability
        """
        self.lr = lr
        self.betas = betas
        self.weight_decay = weight_decay
        self.n_sma_threshold = n_sma_threshold
        self.degenerated_to_sgd = degenerated_to_sgd
        self.eps = eps

        self.check_valid_parameters()

        buffer: BUFFER = [[None, None, None] for _ in range(10)]

        if is_valid_parameters(params):
            for param in params:
                if 'betas' in param and (param['betas'][0] != betas[0] or param['betas'][1] != betas[1]):
                    param['buffer'] = buffer

        defaults: DEFAULTS = dict(
            lr=lr,
            betas=betas,
            eps=eps,
            weight_decay=weight_decay,
            adamd_debias_term=adamd_debias_term,
            buffer=buffer,
        )

        super().__init__(params, defaults)

    def check_valid_parameters(self):
        if self.lr < 0.0:
            raise ValueError(f'Invalid learning rate : {self.lr}')
        if self.weight_decay < 0.0:
            raise ValueError(f'Invalid weight_decay : {self.weight_decay}')
        if not 0.0 <= self.betas[0] < 1.0:
            raise ValueError(f'Invalid beta_0 : {self.betas[0]}')
        if not 0.0 <= self.betas[1] < 1.0:
            raise ValueError(f'Invalid beta_1 : {self.betas[1]}')
        if self.eps < 0.0:
            raise ValueError(f'Invalid eps : {self.eps}')

    def __setstate__(self, state: Dict):
        super().__setstate__(state)

    def step(self, closure: CLOSURE = None) -> LOSS:
        loss: LOSS = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue

                grad = p.grad.data.float()
                if grad.is_sparse:
                    raise RuntimeError('RAdam does not support sparse gradients')

                p_data_fp32 = p.data.float()

                state = self.state[p]

                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p_data_fp32)
                    state['exp_avg_sq'] = torch.zeros_like(p_data_fp32)
                else:
                    state['exp_avg'] = state['exp_avg'].type_as(p_data_fp32)
                    state['exp_avg_sq'] = state['exp_avg_sq'].type_as(p_data_fp32)

                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                beta1, beta2 = group['betas']

                bias_correction1 = 1 - beta1 ** state['step']

                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)

                state['step'] += 1
                buffered = group['buffer'][int(state['step'] % 10)]
                if state['step'] == buffered[0]:
                    n_sma, step_size = buffered[1], buffered[2]
                else:
                    buffered[0] = state['step']
                    beta2_t = beta2 ** state['step']
                    n_sma_max = 2.0 / (1.0 - beta2) - 1.0
                    n_sma = n_sma_max - 2.0 * state['step'] * beta2_t / (1.0 - beta2_t)
                    buffered[1] = n_sma

                    if n_sma >= self.n_sma_threshold:
                        rt = math.sqrt(
                            (1 - beta2_t)
                            * (n_sma - 4)
                            / (n_sma_max - 4)
                            * (n_sma - 2)
                            / n_sma
                            * n_sma_max
                            / (n_sma_max - 2)
                        )

                        if group['adamd_debias_term']:
                            step_size = rt
                        else:
                            step_size = rt / bias_correction1
                    elif self.degenerated_to_sgd:
                        step_size = 1.0 / bias_correction1
                    else:
                        step_size = -1
                    buffered[2] = step_size

                if n_sma >= self.n_sma_threshold:
                    if group['weight_decay'] != 0:
                        p_data_fp32.add_(p_data_fp32, alpha=-group['weight_decay'] * group['lr'])
                    denom = exp_avg_sq.sqrt().add_(group['eps'])
                    p_data_fp32.addcdiv_(exp_avg, denom, value=-step_size * group['lr'])
                    p.data.copy_(p_data_fp32)
                elif step_size > 0:
                    if group['weight_decay'] != 0:
                        p_data_fp32.add_(p_data_fp32, alpha=-group['weight_decay'] * group['lr'])
                    p_data_fp32.add_(exp_avg, alpha=-step_size * group['lr'])
                    p.data.copy_(p_data_fp32)

        return loss
