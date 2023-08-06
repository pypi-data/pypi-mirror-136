"""Contains logic to train Pytorch Neural networks."""
from typing import Any, Dict, List, Tuple

import torch

from nn_helper.base.model import ModelBase
from nn_helper.callbacks.base_callback import BaseCallback, CallbackList
from nn_helper.callbacks.metric_aggregator import MetricAggregator


def fit(
    model: ModelBase,
    data_loader: torch.utils.data.DataLoader,
    epochs: int,
    loss_fn: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    callbacks: List[BaseCallback] = None,
    metrics: List[str] = [],
    verbose: int = 1,
    device: str = "cpu",
    start_epoch: int = 1,
) -> None:
    """Fits the model on the training data and calls callbacks during training in different phases.

    Args:
        model (ModelBase): The model that should be trained.
        data_loader (torch.utils.data.DataLoader): The training data.
        epochs (int): The number of passes through the training data.
        loss_fn (torch.nn.Module): The loss function.
        optimizer (torch.optim.Optimizer): The optimizer.
        fit_function (Callable, optional): Function that defines how to train
            the model. Defaults to standard_fit_function.
        callbacks (List[BaseCallback], optional): Which functions to call at the start
            or end of every batch and epoch. Defaults to None.
        metrics (List[str], optional): Which metrics that should
            be tracked. Defaults to [].
        verbose (int, optional): [description]. Defaults to 1.
        device (str, optional): Whether training is done on cpu or gpu.
            Defaults to 'cpu'.
        start_epoch (int, optional): Where to start training. This is useful
            when training needs to resume from a certain epoch point.
            Defaults to 1.
    """
    assert isinstance(model, ModelBase), f"Your {str(model)} must be of type {str(ModelBase)}."
    num_batches = len(data_loader)

    batch_size = data_loader.batch_size

    callbacks = CallbackList([MetricAggregator()] + (callbacks or []))
    callbacks.set_model(model)
    callbacks.set_params(
        {
            "optimizer": optimizer,
            "num_batches": num_batches,
            "batch_size": batch_size,
            "metrics": metrics,
            "verbose": verbose,
        }
    )

    callbacks.on_train_begin()

    for epoch in range(start_epoch, epochs + 1):
        callbacks.on_epoch_begin(epochs)

        epoch_logs = {}
        for batch_index, batch in enumerate(data_loader):
            batch_logs = dict(batch=batch_index, size=(batch_size or 1))

            def handle_batch(batch_logs: Dict[str, Any], batch: Tuple[torch.Tensor, torch.Tensor]) -> None:
                """Processes the batch through the neural network.

                Preprocesses the batch, adds it to the device, and applies a forward and a backward pass.

                Args:
                    batch_logs (Dict[str, Any]): The logs.
                    batch (Tuple[torch.Tensor, torch.Tensor]): The data.
                """
                x, y = model.prepare_batch(batch)

                callbacks.on_batch_begin(batch_index, batch_logs)

                losses = model.fit_function((x, y), loss_fn, optimizer)

                for loss in losses:
                    batch_logs[loss] = losses[loss].item()

            handle_batch(batch_logs, batch)

            callbacks.on_batch_end(batch_index, batch_logs)

        callbacks.on_epoch_end(epoch, epoch_logs)

    callbacks.on_train_end()
