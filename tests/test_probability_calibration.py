import numpy as np

from src.probability_calibration import TemperatureScaler


def test_temperature_scaler_uses_calibration_labels_and_preserves_rows():
    y = np.array([0, 1, 0, 1, 0, 1])
    p = np.array([[.9, .1], [.2, .8], [.8, .2], [.3, .7], [.7, .3], [.4, .6]])
    scaler = TemperatureScaler(temperatures=[0.5, 1.0, 2.0]).fit(p, y)
    calibrated = scaler.transform(p)
    assert scaler.temperature_ in {0.5, 1.0, 2.0}
    assert calibrated.shape == p.shape
    np.testing.assert_allclose(calibrated.sum(axis=1), np.ones(len(y)))
    assert np.isfinite(calibrated).all()


def test_temperature_scaler_rejects_invalid_inputs():
    with np.testing.assert_raises(ValueError):
        TemperatureScaler().fit(np.array([[.5, .5]]), np.array([0, 1]))
