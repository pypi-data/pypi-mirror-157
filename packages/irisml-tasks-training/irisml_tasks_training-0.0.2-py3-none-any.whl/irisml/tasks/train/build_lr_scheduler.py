import dataclasses
import torch


@dataclasses.dataclass
class LrSchedulerConfig:
    name: str = 'cosine_annealing'


def build_lr_scheduler(config, optimizer, num_epochs):
    config = config or LrSchedulerConfig()

    if config.name == 'cosine_annealing':
        return torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, num_epochs)
    elif config.name == 'linear_decreasing':
        return torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=1, end_factor=0, total_iters=num_epochs)

    raise ValueError(f"Unsupported lr scheduler name: {config.name}")
