import torch


class Feature(torch.Tensor):  # type: ignore
    """
    Class to wrap over a data tensor representing a timeseries
    (generally output of a moe model at different timesteps).

    We expect the input tensor to have 4 dimensions, first corresponding
    to timestep, second corresponding to the batch, thrid corresponding
    to the number of experts in the moe model and the fourth
    corresponding to the feature dim.
    """

    def validate(self) -> None:
        if len(self.shape) != 4:
            raise ValueError(
                """data must be a 4-dimensional tensor of shape
                (batch, num_experts, dim)"""
            )

    @property
    def num_timesteps(self) -> int:
        return self.shape[0]  # type: ignore

    @property
    def batch_size(self) -> int:
        return self.shape[1]  # type: ignore

    @property
    def num_experts(self) -> int:
        return self.shape[2]  # type: ignore

    @property
    def feature_dim(self) -> int:
        return self.shape[3]  # type: ignore

    @classmethod
    def build_from_tensor(cls, data: torch.Tensor) -> "Feature":
        device = data.device
        feature = cls(data.to("cpu")).to(device)
        assert isinstance(feature, Feature)
        feature.validate()
        return feature

    @classmethod
    def build(cls, data: torch.Tensor) -> "Feature":
        device = data.device
        feature = cls(data.to("cpu")).to(device)
        assert isinstance(feature, Feature)
        feature.validate()
        return feature
