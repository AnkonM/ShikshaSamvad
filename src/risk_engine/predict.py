from pathlib import Path
import pandas as pd
import torch

# Handle both relative and absolute imports
try:
    from .bnn_model import SimpleBNN, predict_with_uncertainty
    from .preprocess import add_last_activity_days, select_features
except ImportError:
    # When running directly, use absolute imports
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.risk_engine.bnn_model import SimpleBNN, predict_with_uncertainty
    from src.risk_engine.preprocess import add_last_activity_days, select_features

def run_inference(input_path: str, model_dir: str, output_csv: str) -> None:
    df = pd.read_csv(input_path)
    df = add_last_activity_days(df)
    X = select_features(df).values
    X_t = torch.tensor(X, dtype=torch.float32)

    model = SimpleBNN(input_dim=X_t.shape[1])
    model.load_state_dict(torch.load(Path(model_dir) / "model.pt", map_location="cpu"))

    mean, lower, upper = predict_with_uncertainty(model, X_t, num_samples=20)
    df_out = df.copy()
    df_out["dropout_risk"] = mean.numpy()
    df_out["risk_ci_lower"] = lower.numpy()
    df_out["risk_ci_upper"] = upper.numpy()

    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    run_inference("data/raw/lms_data.csv", "models/risk_engine", "data/processed/risk_predictions.csv")