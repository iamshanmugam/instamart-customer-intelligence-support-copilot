# Churn Modelling Decision

Genuine churn column present: **False**

Supervised churn modelling was **not** performed.
RFM-based at-risk segments in `retention_list.csv` are behavioural retention indicators,
not probability-of-churn predictions.

To train Logistic Regression or Random Forest, historical churn labels would be required,
e.g. `churned` within 90 days after last order, with features frozen before that window.