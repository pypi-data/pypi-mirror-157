import torch


class Feature(torch.Tensor):  # type: ignore
    """
    Class to wrap over a data tensor (generally output of a moe model).

    We expect the input tensor to have 3 dimensions, first corresponding
    to the batch, second to the number of experts in the moe model and the
    third corresponding to the feature dim.
    """

    def validate(self) -> None:
        if len(self.shape) != 3:
            raise ValueError(
                """data must be a 3-dimensional tensor of shape
                (batch, num_experts, dim)"""
            )

    @property
    def batch_size(self) -> int:
        return self.shape[0]  # type: ignore

    @property
    def num_experts(self) -> int:
        return self.shape[1]  # type: ignore

    @property
    def feature_dim(self) -> int:
        return self.shape[2]  # type: ignore

    @classmethod
    def build_from_tensor(cls, data: torch.Tensor) -> "Feature":
        device = data.device
        feature = cls(data.to("cpu")).to(device)
        assert isinstance(feature, Feature)
        feature.validate()
        return feature
