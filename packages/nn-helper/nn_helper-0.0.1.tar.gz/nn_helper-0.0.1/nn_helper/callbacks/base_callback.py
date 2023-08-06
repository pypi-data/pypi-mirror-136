"""Provides BaseCallback for callbacks and CallbackList functions as wrapper for callbacks."""
from __future__ import annotations

from typing import Any, Dict, List, Union

from nn_helper import ModelBase


class CallbackList:
    """Container abstracting a list of callbacks."""

    def __init__(self, callbacks: List[BaseCallback]):
        """Provide a list of callbacks to be used.

        Args:
            callbacks (List[Callback]): Callback classes that
                inherit the Callback base class.
        """
        self.callbacks = callbacks

    def set_params(self, params: Dict[str, Any]) -> None:
        """Sets the training parameters.

        Args:
            params (Dict[str, Any]): Training parameters.
        """
        for callback in self.callbacks:
            callback.set_params(params)

    def set_model(self, model: ModelBase) -> None:
        """Sets the available models.

        Args:
            model (ModelBase): The model(s).
        """
        for callback in self.callbacks:
            callback.set_model(model)

    def on_train_begin(self, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the beginning of training.

        Args:
            logs (Dict[str, Union[int, float]]): dictionary of logs. Defaults to None.
        """
        logs = logs or {}
        for callback in self.callbacks:
            callback.on_train_begin(logs)

    def on_train_end(self, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the end of training.

        Args:
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """
        logs = logs or {}
        for callback in self.callbacks:
            callback.on_train_end(logs)

    def on_epoch_begin(self, epoch: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the beginning of an epoch.

        Args:
            epoch (int): Index of epoch.
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """
        logs = logs or {}
        for callback in self.callbacks:
            callback.on_epoch_begin(epoch, logs)

    def on_epoch_end(self, epoch: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the end of an epoch.

        Args:
            epoch (int): Index of epoch.
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """
        logs = logs or {}
        for callback in self.callbacks:
            callback.on_epoch_end(epoch, logs)

    def on_batch_begin(self, batch_index: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the start of a batch.

        Args:
            batch_index (int): Index of batch whithin current epoch.
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """
        logs = logs or {}
        for callback in self.callbacks:
            callback.on_batch_begin(batch_index, logs)

    def on_batch_end(self, batch_index: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the end of a batch.

        Args:
            batch_index (int): Index of batch whithin current epoch.
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """
        logs = logs or {}
        for callback in self.callbacks:
            callback.on_batch_end(batch_index, logs)


class BaseCallback:
    """Base class that every Callback must inherit."""

    def __init__(self):
        """Initialise BaseCallback."""
        self.model = None

    def set_params(self, params: Dict[str, Any]) -> None:
        """Set parameters.

        Args:
            params (Dict[str, Any]): Training parameters.
        """
        self.params = params

    def set_model(self, model: ModelBase) -> None:
        """Set model(s).

        Args:
            model (ModelBase): The model(s).
        """
        self.model = model

    def on_epoch_begin(self, epoch: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the beginning of every epoch.

        Args:
            epoch (int): At which epoch the training loop is.
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """

    def on_epoch_end(self, epoch: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the end of every epoch.

        Args:
            epoch (int): At which epoch the training loop is.
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """

    def on_batch_begin(self, batch_index: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the beginning of every batch.

        Args:
            batch_index (int): At which batch the epoch loop is.
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """

    def on_batch_end(self, batch_index: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called at the end of every batch.

        Args:
            batch_index (int): At which batch the epoch loop is.
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """

    def on_train_begin(self, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called once at the beginning of training.

        Args:
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """

    def on_train_end(self, logs: Dict[str, Union[int, float]] = None) -> None:
        """Called once at the end of training.

        Args:
            logs (Dict[str, Union[int, float]], optional): Dictionary of logs. Defaults to None.
        """
