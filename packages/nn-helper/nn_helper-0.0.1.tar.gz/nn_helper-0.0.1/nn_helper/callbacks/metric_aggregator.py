"""Contains metric aggregator callbacks."""
from typing import Dict, Union

from nn_helper.callbacks.base_callback import BaseCallback


class MetricAggregator(BaseCallback):
    """Callback that records metrics over epochs by taking the mean.

    It makes these computed means available to next callbacks. This callback
    is already incorporated in the `fit` function from the `train.py` script.
    """

    def on_epoch_begin(self, batch_index: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Initialises the metric aggregator for the current epoch.

        Args:
            batch_index (int): The batch number.
            logs (Dict[str, Union[int, float]], optional): The logs. Defaults to None.
        """
        self.batches = 0
        self.totals = {}
        self.metrics = ["loss"] + self.params["metrics"]

    def on_batch_end(self, batch_index: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Is called on every batch ending to store metrics from logs.

        Multiple losses can be captured from logs. If the loss function returns,
        for example, `loss`, which also returns the loss splitted into `loss_1` and `loss_2`,
        all three losses are stored.

        Args:
            batch_index (int): The batch number.
            logs (Dict[str, Union[int, float]], optional): The logs from the batch. This includes, among others
                the loss values and metrics. Defaults to None.
        """
        logs = logs or {}

        batch_size = logs.get("size", 1)
        self.batches += batch_size

        for key, value in logs.items():
            if key in self.totals:
                self.totals[key] += value * batch_size
            elif key in self.metrics:
                self.totals[key] = value * batch_size

    def on_epoch_end(self, epoch: int, logs: Dict[str, Union[int, float]] = None) -> None:
        """Make the mean of the metrics in the current epoch available for next callbacks.

        Args:
            epoch (int): The epoch number.
            logs (Dict[str, Union[int, float]], optional): The logs. Defaults to None.
        """
        if not logs:
            for key in self.metrics:
                if key in self.totals:
                    # Make value available to next callbacks.
                    logs[key] = self.totals[key] / self.batches
