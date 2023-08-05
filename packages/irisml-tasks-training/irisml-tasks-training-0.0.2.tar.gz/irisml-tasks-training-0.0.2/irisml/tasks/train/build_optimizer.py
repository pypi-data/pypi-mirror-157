import torch.optim


def build_optimizer(name: str, parameters, base_lr, weight_decay=0, momentum=0):
    if name == 'sgd':
        return torch.optim.SGD(parameters, lr=base_lr, weight_decay=weight_decay, momentum=momentum)
    elif name == 'adam':
        return torch.optim.Adam(parameters, lr=base_lr, weight_decay=weight_decay)
    elif name == 'amsgrad':
        return torch.optim.Adam(parameters, lr=base_lr, weight_decay=weight_decay, amsgrad=True)
    elif name == 'rmsprop':
        return torch.optim.RMSprop(parameters, lr=base_lr, weight_decay=weight_decay, momentum=momentum)
    else:
        raise ValueError(f"Unsupported optimizer: {name}")
