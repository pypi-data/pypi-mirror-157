import logging
import time
from .plugin_base import PluginBase

logger = logging.getLogger(__name__)


class Plugin(PluginBase):
    def on_train_epoch_start(self, trainer, model, epoch_index):
        self._epoch_sum_loss = 0
        self._epoch_num_samples = 0
        self._epoch_start = time.time()

    def on_train_epoch_end(self, trainer, model, epoch_index):
        loss = self._epoch_sum_loss / self._epoch_num_samples
        training_time = time.time() - self._epoch_start
        logger.info(f"Epoch {epoch_index}: Training loss: {loss:.4f}, time: {training_time:.2f}s")

    def on_train_batch_end(self, trainer, model, loss, batch, batch_index):
        self._epoch_sum_loss += float(loss.item()) * len(batch[0])
        self._epoch_num_samples += len(batch[0])
        return loss

    def on_validation_start(self, trainer, model):
        self._validation_sum_loss = 0
        self._validation_num_samples = 0

    def on_validation_batch_end(self, trainer, model, loss, batch, batch_index):
        self._validation_sum_loss += float(loss.item()) * len(batch[0])
        self._validation_num_samples += len(batch[0])

    def on_validation_end(self, trainer, model):
        loss = self._validation_sum_loss / self._validation_num_samples
        logger.info(f"Validation loss: {loss:.4f}")
