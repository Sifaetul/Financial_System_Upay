# Machine Learning Architecture

## Pipeline Lifecycle
1. **Data Ingestion:** Async job dumps transaction + feature tables.
2. **Feature Engineering:** Batch and streaming feature calculations.
3. **Dataset Creation:** Automated snapshot generation.
4. **Training:** Scikit-learn/XGBoost pipelines (Phase 6+).
5. **Validation:** Hold-out sets, precision/recall constraints.
6. **Registry:** MLflow or similar for versioning (`v1.0.0-fraud-xgb`).
7. **Deployment:** Seamless API / Worker load.
8. **Inference:** Celery worker loads model into memory.
9. **Monitoring & Drift Detection:** Distribution divergence analysis.
10. **Retraining:** Feedback loop triggered via investigator feedback.

## Explainability
- SHAP values calculated alongside prediction.
- Stored in `model_predictions` for dashboard retrieval.\n