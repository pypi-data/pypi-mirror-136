"""Contains logger classes that, for example, print metrics to terminal."""
from typing import Dict, Union

from nn_helper.callbacks.base_callback import BaseCallback


class VerboseLogger(BaseCallback):
    """Callback that prints training information to the terminal.

    For example, epoch number and corresponding average loss.
    """

    def __init__(self, log_interval: int = 1):
        """Initialise instance variables.

        Args:
            log_interval (int, optional): The interval at which metrics
                are printed to terminal during an epoch. Defaults to 1.
        """
        self.log_interval = log_interval

    def on_train_begin(self, logs: Dict[str, Union[int, float]] = None) -> None:
        """Initialises the verbose logger before training.

        Args:
            logs (Dict[str, Union[int, float]], optional): The logs. Defaults to None.
        """
        self.metrics = ["loss"] + self.params["metrics"]
        if self.params["verbose"] > 0:
            print("Begin training...")

    def on_epoch_begin(self, epoch: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Initialises the verbose logger for the current epoch.

        Args:
            epoch (int): The epoch number.
            logs (Dict[str, Union[int, float]], optional): The logs. Defaults to None.
        """
        self.batch_iterations = 0

    def on_batch_begin(self, batch_index: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Initialises the verbose logger for the current batch.

        Args:
            batch_index (int): The batch number.
            logs (Dict[str, Union[int, float]], optional): The logs from the batch. Defaults to None.
        """
        if self.params["verbose"] == 2:
            self.batch_iterations += 1
            if self.batch_iterations % self.log_interval == 0:
                print("Batch:", self.batch_iterations)

    def on_batch_end(self, batch_index: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Is called at the end of every batch in an epoch.

        Args:
            batch_index (int): The batch number.
            logs (Dict[str, Union[int, float]], optional): The logs from the batch. Defaults to None.
        """
        if self.params["verbose"] == 2:
            if self.batch_iterations % self.log_interval == 0:
                for key in self.metrics:
                    if logs.get(key, None):
                        print(f"{key}: {logs[key]}")

    def on_epoch_end(self, epoch: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Is called at the end of every epoch in training.

        Args:
            epoch (int): The epoch number.
            logs (Dict[str, Union[int, float]], optional): The logs. Defaults to None.
        """
        if self.params["verbose"] > 0:
            print("Epoch:", epoch)
            for key in self.metrics:
                if logs.get(key, None):
                    print(f"{key}: {logs[key]}")

    def on_train_end(self, logs: Dict[str, Union[int, float]] = None) -> None:
        """Is called once at the end of training.

        Args:
            logs (Dict[str, Union[int, float]], optional): The logs. Defaults to None.
        """
        if self.params["verbose"] > 0:
            print("Finished.")
