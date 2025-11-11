import xgboost as xgb
import pandas as pd
from typing import Union, Optional
from src.models.base_model import BaseForecaster


class XGBoostForecaster(BaseForecaster):
    """
    A forecasting class using XGBoost regression.

    Implements the BaseForecaster interface for training, prediction, evaluation,
    and feature importance visualization.
    """

    def __init__(self, params: Optional[dict] = None):
        """
        Initialize the XGBoost regressor with default or custom parameters.

        Parameters:
        - params (dict, optional): Dictionary of hyperparameters for XGBRegressor.
        """
        default_params = {
            "n_estimators": 200,
            "learning_rate": 0.01,
            "max_depth": 5,
            "min_child_weight": 10,
            "base_score": 0.5,
        }
        self.model = xgb.XGBRegressor(**(params or default_params))

    def fit(self, x_train, y_train, x_test, y_test):
        """
        Fit the XGBoost model to training data and evaluate on test data.

        Parameters:
        - x_train: Training features
        - y_train: Training targets
        - x_test: Testing features
        - y_test: Testing targets
        """
        self.model.fit(
            x_train, y_train, eval_set=[(x_train, y_train), (x_test, y_test)], verbose=0
        )

    def predict(self, x):
        """
        Predict target values using the trained model.

        Parameters:
        - x: Features to predict on

        Returns:
        - np.ndarray of predictions
        """
        return self.model.predict(x)

    def evaluate(self, x_test, y_test, data_all, steps: int) -> pd.DataFrame:
        """
        Evaluate model predictions against actual values.

        Parameters:
        - x_test: Test features
        - y_test: Test targets
        - data_all: Full dataset with datetime index
        - day (int): Number of days to consider for evaluation (multiplied by 4 for hourly data)

        Returns:
        - pd.DataFrame with actual and predicted values
        """
        predicted = self.predict(x_test)
        results = pd.concat([y_test, pd.Series(predicted, index=y_test.index)], axis=1)
        results.index = data_all.index[-4 * steps :]
        results.columns = ["Actual", "Predicted"]
        return results

    def predict_from_date(
        self, data_all: pd.DataFrame, start_date: Union[str, pd.Timestamp]
    ):
        """
        Predict values starting from a given date.

        Parameters:
        - data_all (pd.DataFrame): Full dataset with datetime index
        - start_date (str or pd.Timestamp): Start date for prediction

        Returns:
        - np.ndarray of predicted values
        """
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)

        data_subset = data_all[start_date:]
        return self.predict(data_subset)

    def plot_feature_importance(self):
        """
        Plot feature importance based on the trained model.

        Returns:
        - matplotlib Axes object with the plot.
        """
        return xgb.plot_importance(self.model, height=0.7)
