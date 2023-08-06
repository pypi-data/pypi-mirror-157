# Taken from https://github.com/facebookresearch/mtrl/blob/main/mtrl/agent/components/moe_layer.py
from __future__ import annotations

import torch
from torch import nn


class Linear(nn.Module):  # type: ignore[misc]
    # error: Class cannot subclass "Module" (has type "Any")
    def __init__(
        self, num_experts: int, in_features: int, out_features: int, bias: bool = True
    ):
        """torch.nn.Linear layer extended for use as a mixture of experts.

        Args:
            num_experts (int): number of experts in the mixture.
            in_features (int): size of each input sample for one expert.
            out_features (int): size of each output sample for one expert.
            bias (bool, optional): if set to ``False``, the layer will
                not learn an additive bias. Defaults to True.
        """
        super().__init__()
        self.num_experts = num_experts
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(
            torch.rand(self.num_experts, self.in_features, self.out_features)
        )
        if bias:
            self.bias = nn.Parameter(torch.rand(self.num_experts, 1, self.out_features))
            self.use_bias = True
        else:
            self.use_bias = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.use_bias:
            return x.matmul(self.weight) + self.bias
        else:
            return x.matmul(self.weight)

    def extra_repr(self) -> str:
        return f"num_experts={self.num_experts}, in_features={self.in_features}, out_features={self.out_features}, bias={self.use_bias}"


class FunctionalLinear(nn.Module):  # type: ignore[misc]
    # Class cannot subclass "Module" (has type "Any")
    def forward(
        self, input: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor
    ) -> torch.Tensor:
        # shape of weight is (num_experts, in_features, out_features)
        # shape of bias is (num_experts, 1, out_features)

        return input.matmul(weight) + bias

    def extra_repr(self) -> str:
        return "FunctionalLinear layer"
