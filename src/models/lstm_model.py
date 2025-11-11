import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense
from sklearn.preprocessing import MinMaxScaler
from typing import Union
from src.models.base_model import BaseForecaster  # Adjust path if needed


class LSTMForecaster(BaseForecaster):
    """
    A forecasting class using LSTM neural networks.
    """

    def __init__(self, past_days=4, future_days=1, steps=96):
        self.past_days = past_days
        self.future_days = future_days
        self.steps = steps
        self.model = None
        self.y_scaler = None

    def scale_data(self, data):
        """
        Scale features and target using MinMaxScaler.

        Returns:
        - scaled_data: Scaled DataFrame
        """
        features = data.iloc[:, 1:]
        target = data.iloc[:, 0]

        x_scaler = MinMaxScaler()
        X = pd.DataFrame(x_scaler.fit_transform(features))

        self.y_scaler = MinMaxScaler()
        Y = pd.DataFrame(self.y_scaler.fit_transform(target.values.reshape(-1, 1)))

        scaled_data = pd.concat([Y, X], axis=1)
        scaled_data.columns = data.columns

        return scaled_data

    def create_lstm_data(self, data):
        """
        Create fixed-shape LSTM windows using deterministic sliding windows.
        - X arrays shape: (n_windows, train_size, n_features)
        - y arrays shape: (n_windows, test_size)
        """
        test_size = self.future_days * self.steps
        train_size = self.past_days * self.steps
        n = len(data)
        if n < train_size + test_size:
            raise ValueError("Not enough samples for requested past_days/future_days")

        # number of non-overlapping windows available
        max_windows = (n - train_size) // test_size
        if max_windows <= 0:
            raise ValueError("Not enough windows available given test_size/train_size")

        n_splits = min(30, max_windows)

        # ensure at least one training window; reserve last `future_days` windows for test
        cutoff = max(1, n_splits - self.future_days)

        X_train, y_train = [], []
        X_test, y_test = [], []

        for k in range(n_splits):
            train_end = train_size + k * test_size - 1
            train_start = train_end - train_size + 1
            test_start = train_end + 1
            test_end = test_start + test_size - 1

            if test_end >= n:
                break

            Xw = data.iloc[
                train_start : train_end + 1
            ].values  # shape: train_size x n_features
            yw = (
                data["actual power"].iloc[test_start : test_end + 1].values
            )  # length: test_size

            if k < cutoff:
                X_train.append(Xw)
                y_train.append(yw)
            else:
                X_test.append(Xw)
                y_test.append(yw)

        if len(X_train) == 0:
            raise ValueError(
                "No training windows created. Reduce future_days or provide more data."
            )

        return np.array(X_train), np.array(y_train), np.array(X_test), np.array(y_test)

    def fit(self, x_train, y_train, x_test, y_test):
        """
        Train the LSTM model.
        """
        self.model = Sequential()
        self.model.add(
            LSTM(
                256,
                return_sequences=True,
                kernel_initializer=tf.initializers.zeros(),
                input_shape=x_train.shape[1:],
            )
        )
        self.model.add(Dropout(0.3))
        self.model.add(LSTM(256, kernel_initializer=tf.initializers.zeros()))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(self.steps))
        self.model.summary()

        self.model.compile(optimizer="adam", loss="MSE")

        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=20, mode="min", restore_best_weights=True
        )

        self.history = self.model.fit(
            x_train,
            y_train,
            validation_data=(x_test, y_test),
            epochs=200,
            callbacks=[early_stopping],
            verbose=0,
        )

    def predict(self, x):
        """
        Predict using the trained LSTM model.
        """
        return self.model.predict(x)

    def evaluate(self, scaled_data, data):
        """
        Evaluate the LSTM model on the last 4 days of data.

        Parameters:
        - scaled_data: DataFrame with scaled input features
        - data: Original DataFrame with actual values

        Returns:
        - results: DataFrame with actual and predicted values
        - lstm_errors: Dictionary of prediction error metrics
        """
        # Construct input windows for the last 3 days
        input_test_days = np.array(
            [
                scaled_data.iloc[
                    -(6 - i) * self.steps : -(4 - i) * self.steps, :
                ].to_numpy()
                for i in range(4)
            ]
        )

        # Predict
        predicted = self.predict(input_test_days)

        # Inverse transform predictions
        y_pred = self.y_scaler.inverse_transform(predicted.reshape(-1, 1)).flatten()

        # Get actual values
        y_test = data.iloc[-4 * self.steps :, 0]
        y_test_series = pd.Series(y_test.values, index=data.index[-4 * self.steps :])

        # Create results DataFrame
        results = pd.DataFrame(
            {"Actual": y_test_series, "Predicted": y_pred}, index=y_test_series.index
        )

        return results

    def predict_from_date(
        self, data_all: pd.DataFrame, start_date: Union[str, pd.Timestamp]
    ):
        """
        Predict future values from a given date using the last LSTM window.
        """
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)

        last_day = np.array(data_all[start_date:])[-self.past_days * self.steps :, :]
        last_day_arr = np.array([last_day])
        future_day_pred = self.model.predict(last_day_arr)
        return self.y_scaler.inverse_transform(
            future_day_pred.reshape(self.steps, 1)
        ).reshape(-1)
