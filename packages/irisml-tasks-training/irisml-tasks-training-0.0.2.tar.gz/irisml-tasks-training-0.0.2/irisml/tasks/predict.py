import dataclasses
import itertools
import typing
import torch.nn
import torch.utils.data
import irisml.core
from irisml.tasks.train.build_dataloader import build_dataloader


class Predictor:
    def __init__(self, model):
        self._model = model
        self._predictor = getattr(model, 'predictor', None)

    @torch.no_grad()
    def predict(self, dataloader):
        was_training = self._model.training
        self._model.eval()
        results = []
        for batch_index, batch in enumerate(dataloader):
            batch_results = self.prediction_step(batch, batch_index)
            results.append(batch_results)

        if was_training:
            self._model.train()

        return self._aggregate_results(results)

    def prediction_step(self, batch, batch_index):
        inputs, targets = batch
        if hasattr(self._model, 'prediction_step'):
            batch_results = self._model.prediction_step(inputs)
        else:
            outputs = self._model(inputs)
            batch_results = self._predictor(outputs)
        return batch_results

    def _aggregate_results(self, results):
        if torch.is_tensor(results[0]):
            return torch.cat(results)
        elif isinstance(results[0], list):
            return list(itertools.chain(*results))
        else:
            raise RuntimeError(f"Unexpected result types: {results[0]}")


class Task(irisml.core.TaskBase):
    """Predict using a given model.

    This class assumes that the model.predictor returns a Tensor or a list of results.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset
        transform: torch.nn.Module
        model: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        batch_size: int = 1

    @dataclasses.dataclass
    class Outputs:
        predictions: typing.List = dataclasses.field(default_factory=list)

    def execute(self, inputs):
        results = self._predict(inputs, Predictor)
        return self.Outputs(results)

    def _predict(self, inputs, predictor_class):
        dataloader = build_dataloader(inputs.dataset, inputs.transform, batch_size=self.config.batch_size)
        predictor = predictor_class(inputs.model)
        results = predictor.predict(dataloader)
        return results
