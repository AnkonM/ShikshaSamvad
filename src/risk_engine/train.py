from pathlib import Path
import pandas as pd
import torch
from torch.utils.data import TensorDataset, DataLoader

# Handle both relative and absolute imports
try:
    from .bnn_model import SimpleBNN
    from .preprocess import add_last_activity_days, select_features
except ImportError:
    # When running directly, use absolute imports
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.risk_engine.bnn_model import SimpleBNN
    from src.risk_engine.preprocess import add_last_activity_days, select_features

def train_dummy(input_path: str, model_dir: str) -> None:
    df = pd.read_csv(input_path)
    df = add_last_activity_days(df)
    X = select_features(df).values
    y = (df["avg_grade"] < 60).astype(int).values  # dummy target
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

    model = SimpleBNN(input_dim=X_t.shape[1])
    ds = TensorDataset(X_t, y_t)
    dl = DataLoader(ds, batch_size=16, shuffle=True)

    loss_fn = torch.nn.BCELoss()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    for _ in range(3):
        for xb, yb in dl:
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()

    out_dir = Path(model_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "model.pt")

if __name__ == "__main__":
    train_dummy("data/raw/lms_data.csv", "models/risk_engine")