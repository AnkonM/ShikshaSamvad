from typing import Tuple
import torch
import torch.nn as nn

class SimpleBNN(nn.Module):
    """
    Placeholder Bayesian-like model. Replace with real Bayesian layers (e.g., pyro/pytorch distributions)
    or approximate inference strategy. For now, acts as a stub.
    """
    def __init__(self, input_dim: int, hidden_dim: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

def predict_with_uncertainty(model: nn.Module, x: torch.Tensor, num_samples: int = 30) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    MC-dropout style uncertainty as a stand-in. Replace with true BNN predictive distribution later.
    Returns mean, lower_ci, upper_ci.
    """
    model.train()  # enable dropout
    preds = []
    with torch.no_grad():
        for _ in range(num_samples):
            preds.append(model(x).squeeze(-1))
    samples = torch.stack(preds, dim=0)
    mean = samples.mean(dim=0)
    lower = samples.quantile(0.05, dim=0)
    upper = samples.quantile(0.95, dim=0)
    return mean, lower, upper