"""
Implement the following models for classification.

Feel free to modify the arguments for each of model's __init__ function.
This will be useful for tuning model hyperparameters such as hidden_dim, num_layers, etc,
but remember that the grader will assume the default constructor!
"""

from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F


class ClassificationLoss(nn.Module):
    def forward(self, logits: torch.Tensor, target: torch.LongTensor) -> torch.Tensor:
        """
        Multi-class classification loss
        Hint: simple one-liner

        Args:
            logits: tensor (b, c) logits, where c is the number of classes
            target: tensor (b,) labels

        Returns:
            tensor, scalar loss
        """
        return F.cross_entropy(logits, target)
        raise NotImplementedError("ClassificationLoss.forward() is not implemented")


class LinearClassifier(nn.Module):
    def __init__(
        self,
        h: int = 64,
        w: int = 64,
        num_classes: int = 6,
    ):
        """
        Args:
            h: int, height of the input image
            w: int, width of the input image
            num_classes: int, number of classes
        """
        super().__init__()
        input_dim = 3 * h * w
        self.classifier = nn.Linear(input_dim, num_classes)

        

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: tensor (b, 3, H, W) image

        Returns:
            tensor (b, num_classes) logits
        """
        x = x.view(x.size(0), -1)  # (B, 3*H*W)
        logits = self.classifier(x)
        return logits
        


class MLPClassifier(nn.Module):
    def __init__(
        self,
        h: int = 64,
        w: int = 64,
        num_classes: int = 6,
        hidden_dim: int = 128,
    ):
        """
        An MLP with a single hidden layer

        Args:
            h: int, height of the input image
            w: int, width of the input image
            num_classes: int, number of classes
        """
        super().__init__()
        input_dim = 3 * h * w  # input is flattened (3 channels, H x W pixels)
        
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),  # hidden layer
            nn.ReLU(),  # ReLU activation
            nn.Linear(hidden_dim, num_classes)  # output layer
        )
        

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.view(x.size(0), -1)  # Flatten the input tensor (B, 3*H*W)
        logits = self.mlp(x)
        return logits
        """
        Args:
            x: tensor (b, 3, H, W) image

        Returns:
            tensor (b, num_classes) logits
        """
        


class MLPClassifierDeep(nn.Module):
    def __init__(
        self,
        h: int = 64,
        w: int = 64,
        num_classes: int = 6,
        hidden_dim: int = 128, # hidden layer dimension (width of each layer)
        num_layers: int = 4    
    ):
        """
        An MLP with multiple hidden layers

        Args:
            h: int, height of image
            w: int, width of image
            num_classes: int

        Hint - you can add more arguments to the constructor such as:
            hidden_dim: int, size of hidden layers
            num_layers: int, number of hidden layers
        """
        super().__init__()
        # Compute the input dimension
        input_dim = 3 * h * w

        # Building the sequential model with layers
        layers = []
        
        # Input layer
        layers.append(nn.Linear(input_dim, hidden_dim))
        layers.append(nn.ReLU())  # Add ReLU after the first layer
        
        # Add additional hidden layers
        for _ in range(num_layers - 1):  # num_layers-1 because one layer is already added
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.ReLU())  # Add ReLU after each hidden layer

        # Output layer
        layers.append(nn.Linear(hidden_dim, num_classes))

        # Define the sequential model
        self.mlp = nn.Sequential(*layers)
        

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.view(x.size(0), -1)  # Flatten the input tensor
        logits = self.mlp(x)
        return logits
        """
        Args:
            x: tensor (b, 3, H, W) image

        Returns:
            tensor (b, num_classes) logits
        """
       


class MLPClassifierDeepResidual(nn.Module):
    def __init__(
        self,
        h: int = 64,
        w: int = 64,
        num_classes: int = 6,
        hidden_dim: int = 64,  # hidden layer dimension (width of each layer)
        num_layers: int = 3     # number of layers
    ):
        """
        Args:
            h: int, height of image
            w: int, width of image
            num_classes: int

        Hint - you can add more arguments to the constructor such as:
            hidden_dim: int, size of hidden layers
            num_layers: int, number of hidden layers
        """
        super().__init__()
        input_dim = 3 * h * w  # Calculate the input dimension

        # Store layers in ModuleList to iterate over them
        self.layers = nn.ModuleList()

        # First layer (linear transformation of the input)
        self.layers.append(nn.Linear(input_dim, hidden_dim))
        self.layers.append(nn.ReLU())  # Non-in-place ReLU

        # Add subsequent layers with residual connections
        for _ in range(num_layers - 1):  # num_layers-1 because we already added the first layer
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))
            self.layers.append(nn.ReLU())  # Non-in-place ReLU

        # Final output layer
        self.output_layer = nn.Linear(hidden_dim, num_classes)

        # A linear layer to transform residuals to the correct dimension if needed
        self.residual_transform = nn.Linear(input_dim, hidden_dim)

        

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.view(x.size(0), -1)  # Flatten to (B, 3*H*W)

        # First residual transformation to match dimensions
        residual = self.residual_transform(x)
        for i in range(0, len(self.layers), 2):  # Skip ReLU layers
            # Apply Linear layer
            x = self.layers[i](x)
            # Apply ReLU activation
            x = self.layers[i+1](x)

            # Ensure the dimensions match before adding residual
            if x.size() != residual.size():
                residual = self.residual_transform(x)  # Update residual to match current x size

            # Add residual connection (make sure dimensions match)
            x = x + residual  # Use out-of-place addition (avoid in-place modification)
            residual = x  # Update residual for the next layer

        # Output layer
        logits = self.output_layer(x)
        return logits

       


model_factory = {
    "linear": LinearClassifier,
    "mlp": MLPClassifier,
    "mlp_deep": MLPClassifierDeep,
    "mlp_deep_residual": MLPClassifierDeepResidual,
}


def calculate_model_size_mb(model: torch.nn.Module) -> float:
    """
    Args:
        model: torch.nn.Module

    Returns:
        float, size in megabytes
    """
    return sum(p.numel() for p in model.parameters()) * 4 / 1024 / 1024


def save_model(model):
    """
    Use this function to save your model in train.py
    """
    for n, m in model_factory.items():
        if isinstance(model, m):
            return torch.save(model.state_dict(), Path(__file__).resolve().parent / f"{n}.th")
    raise ValueError(f"Model type '{str(type(model))}' not supported")


def load_model(model_name: str, with_weights: bool = False, **model_kwargs):
    """
    Called by the grader to load a pre-trained model by name
    """
    r = model_factory[model_name](**model_kwargs)
    if with_weights:
        model_path = Path(__file__).resolve().parent / f"{model_name}.th"
        assert model_path.exists(), f"{model_path.name} not found"
        try:
            r.load_state_dict(torch.load(model_path, map_location="cpu"))
        except RuntimeError as e:
            raise AssertionError(
                f"Failed to load {model_path.name}, make sure the default model arguments are set correctly"
            ) from e

    # Limit model sizes since they will be zipped and submitted
    model_size_mb = calculate_model_size_mb(r)
    if model_size_mb > 10:
        raise AssertionError(f"{model_name} is too large: {model_size_mb:.2f} MB")
    print(f"Model size: {model_size_mb:.2f} MB")

    return r
