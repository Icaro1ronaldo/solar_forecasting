import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


# Compute the accuracy errors : MAE, RMSE, R2 score.
def get_prediction_errors(y_true, y_pred):
    R2_score = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"R2 score: {R2_score}")
    print(f"MAE: {mae}")
    print(f"RMSE: {rmse}")
    return [R2_score, mae, rmse]
