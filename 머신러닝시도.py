import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
import numpy as np
from scipy.stats import randint

# Load datasets
batter_data = pd.read_csv('data_batter.csv')
pitcher_data = pd.read_csv('data_pitcher.csv')

# Print the columns of batter_data to find the correct target column
print("Columns of batter_data:", batter_data.columns)

# Assuming 'H' is the hits column and '2B' is the doubles column
hit_column = 'H'
double_column = '2B'

# Prepare data for merging
batter_data = batter_data.rename(columns={'Name': 'Batter_Name'})
pitcher_data = pitcher_data.rename(columns={'Name': 'Pitcher_Name'})

# Add binary hit and double columns to the batter data
batter_data['Hit'] = (batter_data[hit_column] > 0).astype(int)
batter_data['Double'] = (batter_data[double_column] > 0).astype(int)

# Select only relevant columns for merging
batter_columns = ['Batter_Name', 'Hit', 'Double']
pitcher_columns = ['Pitcher_Name'] + [col for col in pitcher_data.columns if col != 'Pitcher_Name']

# Merge datasets on common columns if any, else use batter_name and pitcher_name to create combinations
merged_data = batter_data[batter_columns].merge(pitcher_data[pitcher_columns], how='cross')

# Print the columns of the merged data to debug
print("Columns of merged data:", merged_data.columns)

# Encode categorical features
label_encoders = {}
for column in ['Batter_Name', 'Pitcher_Name']:
    le = LabelEncoder()
    merged_data[column] = le.fit_transform(merged_data[column])
    label_encoders[column] = le

# Define feature columns (selecting only a few important ones)
# Select a subset of columns for simplicity, for example
selected_features = ['Batter_Name', 'Pitcher_Name', 'G', 'IP', 'ERA', 'WHIP']  # Example features

# Ensure selected features exist in the merged data
selected_features = [col for col in selected_features if col in merged_data.columns]

# Sample a fraction of the data for faster training (e.g., 10%)
sample_fraction = 0.1
sampled_data = merged_data.sample(frac=sample_fraction, random_state=42)

# Split the data into features and targets
X = sampled_data[selected_features]
y_hit = sampled_data['Hit']
y_double = sampled_data['Double']

# Split the data into training and validation sets
X_train, X_val, y_train_hit, y_val_hit = train_test_split(X, y_hit, test_size=0.2, random_state=42)
_, _, y_train_double, y_val_double = train_test_split(X, y_double, test_size=0.2, random_state=42)

# Normalize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

# Define the model pipeline for hits
pipeline_hit = Pipeline([
    ('classifier', RandomForestClassifier(random_state=42))
])

# Define the model pipeline for doubles
pipeline_double = Pipeline([
    ('classifier', RandomForestClassifier(random_state=42))
])

# Define the parameter distribution for randomized search
param_dist = {
    'classifier__n_estimators': randint(50, 100),
    'classifier__max_depth': [None, 10, 20],
    'classifier__min_samples_split': randint(2, 5),
    'classifier__min_samples_leaf': randint(1, 3),
}

# Initialize and perform randomized search with cross-validation for hits
random_search_hit = RandomizedSearchCV(pipeline_hit, param_dist, n_iter=10, cv=3, scoring='roc_auc', random_state=42,
                                       n_jobs=-1)
random_search_hit.fit(X_train_scaled, y_train_hit)

# Initialize and perform randomized search with cross-validation for doubles
random_search_double = RandomizedSearchCV(pipeline_double, param_dist, n_iter=10, cv=3, scoring='roc_auc',
                                          random_state=42, n_jobs=-1)
random_search_double.fit(X_train_scaled, y_train_double)

# Get the best models from randomized search
best_model_hit = random_search_hit.best_estimator_
best_model_double = random_search_double.best_estimator_

# Calibrate the classifiers to improve probability estimates
calibrated_model_hit = CalibratedClassifierCV(best_model_hit, cv=3)
calibrated_model_hit.fit(X_train_scaled, y_train_hit)

calibrated_model_double = CalibratedClassifierCV(best_model_double, cv=3)
calibrated_model_double.fit(X_train_scaled, y_train_double)

# Cross-validation to check for overfitting
cv_scores_hit = cross_val_score(calibrated_model_hit, X_val_scaled, y_val_hit, cv=3, scoring='roc_auc')
print(f'Cross-validated AUC scores for hits: {cv_scores_hit}')
print(f'Average AUC score for hits: {np.mean(cv_scores_hit)}')

cv_scores_double = cross_val_score(calibrated_model_double, X_val_scaled, y_val_double, cv=3, scoring='roc_auc')
print(f'Cross-validated AUC scores for doubles: {cv_scores_double}')
print(f'Average AUC score for doubles: {np.mean(cv_scores_double)}')


# Prediction function
def predict_probabilities(batter_name, pitcher_name):
    # Check if the batter name is in the LabelEncoder
    if batter_name not in label_encoders['Batter_Name'].classes_:
        return f"Batter name '{batter_name}' not found in the dataset."

    # Check if the pitcher name is in the LabelEncoder
    if pitcher_name not in label_encoders['Pitcher_Name'].classes_:
        return f"Pitcher name '{pitcher_name}' not found in the dataset."

    batter_encoded = label_encoders['Batter_Name'].transform([batter_name])[0]
    pitcher_encoded = label_encoders['Pitcher_Name'].transform([pitcher_name])[0]
    # Create a sample with zeros and then set the specific batter and pitcher
    sample = pd.DataFrame([0] * len(selected_features), index=selected_features).T
    sample['Batter_Name'] = batter_encoded
    sample['Pitcher_Name'] = pitcher_encoded
    sample_scaled = scaler.transform(sample)
    probability_hit = calibrated_model_hit.predict_proba(sample_scaled)[0][1]*batter_data[batter_data['Name'] == batter_name]['AVG']  # Probability of hit (class 1)
    probability_double = calibrated_model_double.predict_proba(sample_scaled)[0][1]*batter_data[batter_data['Name'] == batter_name]['2B']  # Probability of double (class 1)
    return probability_hit, probability_double


# Example usage
batter_name = '최지훈'
pitcher_name = '최지강'
probability_hit, probability_double = predict_probabilities(batter_name, pitcher_name)
print(
    f'The predicted probability of a hit for batter {batter_name} against pitcher {pitcher_name} is: {probability_hit:.2f}')
print(
    f'The predicted probability of a double for batter {batter_name} against pitcher {pitcher_name} is: {probability_double:.2f}')

# Test with different names to see varying results
batter_name = '홍창기'
pitcher_name = '이병헌'
probability_hit, probability_double = predict_probabilities(batter_name, pitcher_name)
print(
    f'The predicted probability of a hit for batter {batter_name} against pitcher {pitcher_name} is: {probability_hit:.2f}')
print(
    f'The predicted probability of a double for batter {batter_name} against pitcher {pitcher_name} is: {probability_double:.2f}')

# Print the percentage of data used for training
total_data_size = merged_data.shape[0]
sampled_data_size = sampled_data.shape[0]
percentage_used = (sampled_data_size / total_data_size) * 100
print(f'Percentage of data used for training: {percentage_used:.2f}%')


# 대개 타율이 9할이 나오는 말이 안되는 값이 나옴.