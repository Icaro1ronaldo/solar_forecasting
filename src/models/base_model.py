from abc import ABC, abstractmethod
import pandas as pd
from typing import Union


class BaseForecaster(ABC):
    """
    Abstract base class for forecasting models.
    All forecasters must implement the following methods.
    """

    @abstractmethod
    def fit(self, x_train, y_train, x_test, y_test):
        """Train the forecasting model."""
        pass

    @abstractmethod
    def predict(self, x):
        """Make predictions using the trained model."""
        pass

    @abstractmethod
    def evaluate(self, x_test, y_test, data_all, day: int) -> pd.DataFrame:
        """Evaluate model predictions against actual values."""
        pass

    @abstractmethod
    def predict_from_date(
        self, data_all: pd.DataFrame, start_date: Union[str, pd.Timestamp]
    ):
        """Predict values starting from a given date."""
        pass
