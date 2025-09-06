def test_imports():
    from src.risk_engine.data_loader import load_raw_lms  # noqa:F401
    from src.risk_engine.preprocess import add_last_activity_days  # noqa:F401
    from src.risk_engine.bnn_model import SimpleBNN  # noqa:F401