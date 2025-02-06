"""
Analyze features that predict OpenHands performance gaps.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import numpy as np

def main():
    # Load features
    df = pd.DataFrame(pd.read_csv("data/features.csv"))
    
    # Create binary target: 1 if top models significantly outperform OpenHands
    df['performance_gap'] = (df['top_model_success_rate'] > 0.6).astype(int)
    
    # Prepare features
    categorical_features = ['repo_name', 'org_name']
    numerical_features = ['patch_size', 'files_modified', 'problem_desc_length']
    
    # One-hot encode categorical features
    X = pd.get_dummies(df[categorical_features + numerical_features], 
                      columns=categorical_features)
    y = df['performance_gap']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale numerical features
    scaler = StandardScaler()
    X_train[numerical_features] = scaler.fit_transform(X_train[numerical_features])
    X_test[numerical_features] = scaler.transform(X_test[numerical_features])
    
    # Train model
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Print classification report
    y_pred = clf.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Get feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10))
    
    # Analyze numerical feature distributions
    print("\nNumerical Feature Statistics for Cases with Performance Gap:")
    gap_stats = df[df['performance_gap'] == 1][numerical_features].describe()
    print(gap_stats)
    
    print("\nNumerical Feature Statistics for Cases without Performance Gap:")
    no_gap_stats = df[df['performance_gap'] == 0][numerical_features].describe()
    print(no_gap_stats)

if __name__ == "__main__":
    main()