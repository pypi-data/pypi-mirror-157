import dataclasses
import pathlib
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Load a state_dict from the specified file and load it to the input model."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        path: pathlib.Path

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    def execute(self, inputs: Inputs):
        state_dict = torch.load(self._config.path, map_location='cpu')
        inputs.model.load_state_dict(state_dict)
        return self.Outputs(model=inputs.model)
