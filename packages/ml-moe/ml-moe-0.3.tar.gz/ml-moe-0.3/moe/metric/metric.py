from typing import Any

import functorch
import torch

from moe.data.feature import Feature as FeatureTensor


def compute_f(x1: FeatureTensor, x2: FeatureTensor, f: Any) -> torch.Tensor:
    # f is a function that operates on two 1-d tensors
    assert x1.batch_size == x2.batch_size
    assert x1.feature_dim == x2.feature_dim

    return functorch.vmap(f)(
        x1.unsqueeze(2)
        .repeat(1, 1, x2.num_experts, 1)
        .view(x1.batch_size * x1.num_experts * x2.num_experts, x1.feature_dim),
        x1.unsqueeze(1)
        .repeat(1, x1.num_experts, 1, 1)
        .view(x2.batch_size * x2.num_experts * x1.num_experts, x2.feature_dim),
    ).view(x1.batch_size, x1.num_experts, x2.num_experts, 1)
