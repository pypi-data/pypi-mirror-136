"""Contains base classes for models that must be used in the nn_helper package."""
from abc import ABC, abstractmethod
from typing import Dict, Tuple

import torch


class ModelBase(ABC, torch.nn.Module):
    """A simple model base class."""

    def __init__(self):
        """Initialisation of an instance."""
        super(ModelBase, self).__init__()

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """The forward pass function.

        Args:
            x (torch.Tensor): Training data.

        Returns:
            torch.Tensor: Output of the forward pass.
        """

    def prepare_batch(
        self, batch: Tuple[torch.Tensor, torch.Tensor], device: str = "cpu"
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Prepares the batch before it is forwarded into the model.

        This function can be overriden if different functionality is needed.

        Args:
            batch (Tuple[torch.Tensor, torch.Tensor]): The training batch data.
            device (str, optional): Whether trained on GPU or CPU. Defaults to "cpu".

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Preprocessed batch.
        """
        return batch[0].to(device), batch[1].to(device)

    def fit_function(
        self, input_batch: Tuple[torch.Tensor, torch.Tensor], loss_fn: torch.nn.Module, optimizer: torch.optim.Optimizer
    ) -> Dict[str, torch.Tensor]:
        """This orchistrates the complete forward and backward pass.

        This function can be overriden if different functionality is needed.

        Args:
            input_batch (Tuple[torch.Tensor, torch.Tensor]): The training data.
            loss_fn (torch.nn.Module): The loss function that should be used.
            optimizer (torch.optim.Optimizer): The optimizer that should be used.

        Returns:
            Dict[str, torch.Tensor]: The loss value(s).
        """
        self.train()
        optimizer.zero_grad()

        outputs = self(input_batch[0])

        losses = loss_fn(input_batch[1], *outputs)

        if isinstance(losses, torch.Tensor):
            losses = {"loss": losses}

        losses["loss"].backward()
        optimizer.step()

        return losses
