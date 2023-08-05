import copy
import dataclasses
import importlib
import logging
import typing
import torch
import irisml.core

from .build_dataloader import build_dataloader
from .build_lr_scheduler import build_lr_scheduler, LrSchedulerConfig
from .build_optimizer import build_optimizer
from .trainer import Trainer

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Train a pytorch model.

    This is a simple training baseline.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        num_epochs: int
        batch_size: int = 1
        base_lr: float = 1e-5
        device: typing.Optional[typing.Literal['cpu', 'cuda']] = None
        lr_scheduler: typing.Optional[LrSchedulerConfig] = None
        momentum: float = 0
        optimizer: str = 'sgd'
        val_check_interval: typing.Optional[typing.Union[int, float]] = None
        weight_decay: float = 0
        plugins: typing.List[str] = dataclasses.field(default_factory=list)

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module
        train_dataset: torch.utils.data.Dataset
        train_transform: typing.Callable
        val_dataset: torch.utils.data.Dataset = None
        val_transform: typing.Callable = None

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    def execute(self, inputs):
        model = self.train(inputs, Trainer)
        return self.Outputs(model)

    def train(self, inputs, trainer_class, dry_run=False) -> torch.nn.Module:
        plugins = [self._load_plugin(p) for p in self.config.plugins]
        train_dataloader = build_dataloader(inputs.train_dataset, inputs.train_transform, batch_size=self.config.batch_size)
        val_dataloader = inputs.val_dataset and build_dataloader(inputs.val_dataset, inputs.val_transform, batch_size=self.config.batch_size)
        device = self._get_device()
        model = copy.deepcopy(inputs.model).to(device)
        optimizer = build_optimizer(self.config.optimizer, model.parameters(), self.config.base_lr, weight_decay=self.config.weight_decay, momentum=self.config.momentum)
        lr_scheduler = build_lr_scheduler(self.config.lr_scheduler, optimizer, self.config.num_epochs)

        trainer = trainer_class(model, lr_scheduler=lr_scheduler, optimizer=optimizer, plugins=plugins, device=device, val_check_interval=self.config.val_check_interval)

        if not dry_run:
            trainer.train(train_dataloader, val_dataloader, num_epochs=self.config.num_epochs)
        model = trainer.model.to(torch.device('cpu'))
        return model

    def dry_run(self, inputs):
        model = self.train(inputs, Trainer, dry_run=True)
        return self.Outputs(model)

    def _get_device(self) -> torch.device:
        """Get a torch device based on the configuration. If not specified explicitly, it uses cuda if available."""
        if self.config.device:
            device_name = self.config.device
        else:
            device_name = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Training device is selected automatically: {device_name}. To specify the device manually, please set Config.device.")

        return torch.device(device_name)

    def _load_plugin(self, plugin_name):
        try:
            plugin_module = importlib.import_module('irisml.tasks.train.plugins.' + plugin_name)
        except ModuleNotFoundError as e:
            raise RuntimeError(f"Plugin {plugin_name} is not found.") from e

        plugin_class = getattr(plugin_module, 'Plugin', None)
        return plugin_class()
