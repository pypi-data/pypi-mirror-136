import random
from copy import deepcopy
from typing import Iterable, List

import numpy as np
import torch
from torch import nn
from torch.optim.optimizer import Optimizer


class PCGrad:
    """
    Reference : https://github.com/WeiChengTseng/Pytorch-PCGrad
    Example :
        from pytorch_optimizer import AdamP, PCGrad
        ...
        model = YourModel()
        optimizer = PCGrad(AdamP(model.parameters()))

        loss_1, loss_2 = nn.L1Loss(), nn.MSELoss()
        ...
        for input, output in data:
          optimizer.zero_grad()
          loss1, loss2 = loss1_fn(y_pred, output), loss2_fn(y_pred, output)
          optimizer.pc_backward([loss1, loss2])
          optimizer.step()
    """

    def __init__(self, optimizer: Optimizer, reduction: str = 'mean'):
        self.optimizer = optimizer
        self.reduction = reduction

    def check_valid_parameters(self):
        if self.reduction not in ('mean', 'sum'):
            raise ValueError(f'invalid reduction : {self.reduction}')

    @staticmethod
    def flatten_grad(grads) -> torch.Tensor:
        return torch.cat([g.flatten() for g in grads])

    @staticmethod
    def un_flatten_grad(grads, shapes) -> List[torch.Tensor]:
        un_flatten_grad = []
        idx: int = 0
        for shape in shapes:
            length = np.prod(shape)
            un_flatten_grad.append(grads[idx : idx + length].view(shape).clone())
            idx += length
        return un_flatten_grad

    def zero_grad(self):
        return self.optimizer.zero_grad(set_to_none=True)

    def step(self):
        return self.optimizer.step()

    def set_grad(self, grads):
        idx: int = 0
        for group in self.optimizer.param_groups:
            for p in group['params']:
                p.grad = grads[idx]
                idx += 1

    def retrieve_grad(self):
        """get the gradient of the parameters of the network with specific objective"""
        grad, shape, has_grad = [], [], []
        for group in self.optimizer.param_groups:
            for p in group['params']:
                if p.grad is None:
                    shape.append(p.shape)
                    grad.append(torch.zeros_like(p).to(p.device))
                    has_grad.append(torch.zeros_like(p).to(p.device))
                    continue

                shape.append(p.grad.shape)
                grad.append(p.grad.clone())
                has_grad.append(torch.ones_like(p).to(p.device))

        return grad, shape, has_grad

    def pack_grad(self, objectives: Iterable[nn.Module]):
        """pack the gradient of the parameters of the network for each objective
        :param objectives: Iterable[float]. a list of objectives
        :return:
        """
        grads, shapes, has_grads = [], [], []
        for objective in objectives:
            self.zero_grad()

            objective.backward(retain_graph=True)

            grad, shape, has_grad = self.retrieve_grad()

            grads.append(self.flatten_grad(grad))
            has_grads.append(self.flatten_grad(has_grad))
            shapes.append(shape)

        return grads, shapes, has_grads

    def project_conflicting(self, grads, has_grads) -> torch.Tensor:
        """
        :param grads: a list of the gradient of the parameters
        :param has_grads: a list of mask represent whether the parameter has gradient
        :return:
        """
        shared = torch.stack(has_grads).prod(0).bool()

        pc_grad = deepcopy(grads)
        for g_i in pc_grad:
            random.shuffle(grads)
            for g_j in grads:
                g_i_g_j = torch.dot(g_i, g_j)
                if g_i_g_j < 0:
                    g_i -= g_i_g_j * g_j / (g_j.norm() ** 2)

        merged_grad = torch.zeros_like(grads[0]).to(grads[0].device)
        merged_grad[shared] = torch.stack([g[shared] for g in pc_grad])

        if self.reduction == 'mean':
            merged_grad = merged_grad.mean(dim=0)
        else:  # self.reduction == 'sum'
            merged_grad = merged_grad.sum(dim=0)

        merged_grad[~shared] = torch.stack([g[~shared] for g in pc_grad]).sum(dim=0)

        return merged_grad

    def pc_backward(self, objectives: Iterable[nn.Module]):
        """calculate the gradient of the parameters
        :param objectives: Iterable[nn.Module]. a list of objectives
        :return:
        """
        grads, shapes, has_grads = self.pack_grad(objectives)
        pc_grad = self.project_conflicting(grads, has_grads)
        pc_grad = self.un_flatten_grad(pc_grad, shapes[0])

        self.set_grad(pc_grad)
