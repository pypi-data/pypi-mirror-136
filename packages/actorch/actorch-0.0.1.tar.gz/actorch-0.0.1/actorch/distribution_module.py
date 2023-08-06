# ==============================================================================
# Copyright 2022 Luca Della Libera. All Rights Reserved.
# ==============================================================================

"""Deterministic distribution."""

from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union

import torch
from torch import Size, Tensor
from torch.distributions import Distribution, Independent
from torch.nn import Module

from actorch.distributions import (
    MaskedDistribution,
    NormalizingFlow,
    TransformedDistribution,
)
from actorch.models import Model


__all__ = [
    "Approximator",
]


_T = TypeVar("_T")

_Parameterization = Dict[str, Tuple[str, Tuple[int, ...], Callable[[Tensor], Tensor]]]

_Config = Dict[str, Any]


class Approximator(Distribution, Module):
    """Distribution module."""

    def __init__(
        self,
        input_transforms: "Dict[str, Callable[..., Distribution]]",
        distribution_builders: "Dict[str, Callable[..., Distribution]]",
        distribution_parameterizations: "Dict[str, _Parameterization]",
        distribution_output_transforms: "Dict[str, Callable[..., Distribution]]",
        model_builder: "Callable[..., Model]",
        distribution_configs: "Optional[Dict[str, _Config]]" = None,
        model_config: "Optional[_Config]" = None,
        normalizing_flow_builders: "Optional[Dict[str, Callable[..., NormalizingFlow]]]" = None,
        normalizing_flow_configs: "Optional[Dict[str, _Config]]" = None,
    ) -> "None":
        Module.__init__(self)
        self.input_transforms = input_transforms
        self.distribution_builders = distribution_builders
        self.distribution_parameterizations = distribution_parameterizations
        self.distribution_output_transforms = distribution_output_transforms
        self.model_builder = model_builder
        self.distribution_configs = distribution_configs or {}
        self.model_config = model_config or {}
        self.normalizing_flow_builders = normalizing_flow_builders
        self.normalizing_flow_configs = normalizing_flow_configs or {}
        in_shapes = {
            key: transform.out_shape for key, transform in input_transforms.items()
        }
        out_shapes = {}
        for key, parameterization in distribution_parameterizations.items():
            for param_name in parameterization:
                name, out_shape, _ = parameterization[param_name]
                out_shapes[f"{key}/{name}"] = out_shape
        self._model = model_builder(
            in_shapes,
            out_shapes,
            **self.model_config,
        )
        self._normalizing_flows = {}
        if self.normalizing_flow_builders:
            self._normalizing_flows = {k: None for k in self.normalizing_flow_builders}

    def forward(
        self,
        input: "Tensor",
        state: "Optional[Tensor]" = None,
        mask: "Optional[Tensor]" = None,
    ) -> "Tuple[Tensor, Tensor]":
        model_inputs = {}
        start = stop = 0
        for key, transform in self.input_transforms.items():
            stop += transform.in_shape[0]
            model_inputs[key] = transform(input[..., start:stop])
            start = stop
        model_states = state
        model_outputs, model_states = self._model(model_inputs, model_states, mask)
        self._distributions = {}
        for key, builder in self.distribution_builders.items():
            parameterization = self.distribution_parameterizations[key]
            params = {
                param_name: transform(model_outputs[f"{key}/{name}"])
                for param_name, (name, _, transform) in parameterization.items()
            }
            config = self.distribution_configs.get(key, {})
            distribution = builder(**params, **config)
            reinterpreted_batch_ndims = len(distribution.batch_shape) - mask.ndim
            if reinterpreted_batch_ndims > 0:
                distribution = Independent(distribution, reinterpreted_batch_ndims)
            distribution = MaskedDistribution(distribution, mask)
            if self._normalizing_flows:
                if key in self._normalizing_flows:
                    normalizing_flow = self._normalizing_flows[key]
                    if not normalizing_flow:
                        # First call
                        in_shape = distribution.event_shape
                        config = self.normalizing_flow_configs.get(key, {})
                        normalizing_flow = builder(in_shape, **config)
                        self._normalizing_flow[key] = normalizing_flow
                    distribution = TransformedDistribution(
                        distribution, normalizing_flow
                    )
            self._distributions[key] = distribution
