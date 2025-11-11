import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from typing import Union, Optional
from src.models.base_model import BaseForecaster


class RandomForestForecaster(BaseForecaster):
    """
    A forecasting class using RandomForestRegressor.

    Implements the BaseForecaster interface for training, prediction, evaluation,
    and feature importance visualization.
    """

    def __init__(self, params: Optional[dict] = None):
        """
        Initialize the RandomForestRegressor with default or custom parameters.

        Parameters:
        - params (dict, optional): Dictionary of hyperparameters for RandomForestRegressor.
        """
        default_params = {"n_estimators": 200, "max_depth": 7, "random_state": 42}
        self.model = RandomForestRegressor(**(params or default_params))
        self.feature_names = None

    def fit(self, x_train, y_train, x_test=None, y_test=None):
        """
        Fit the RandomForest model to training data.

        Parameters:
        - x_train: Training features
        - y_train: Training targets
        - x_test: (optional) Testing features
        - y_test: (optional) Testing targets
        """
        self.model.fit(x_train, y_train)
        self.feature_names = x_train.columns

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
        Plot normalized feature importances across all trees.

        Returns:
        - matplotlib Axes object with the plot.
        """
        importances = np.std(
            [tree.feature_importances_ for tree in self.model.estimators_], axis=0
        )
        ax = plt.barh(self.feature_names, importances)
        plt.xlabel("Feature Labels")
        plt.ylabel("Feature Importances")
        plt.title("Comparison of different Feature Importances")
        plt.tight_layout()
        plt.show()
        return ax
