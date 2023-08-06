# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 13:41:26 2021

This file contains the functions to automate evaluate the classification models in
a detailed way: using repeated K-Fold CV to estimate the uncertainty of CV metrics;
using bootstrap to estimate the uncertainty of test metrics; and using custom cutoff
, which is optimal respect to a specific metric, for both CV and test metrics.

@author: yipeng.song@hotmail.com
"""
# %% load into required packages
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn import model_selection

# when necessary, suppress the warnings, mainly for testing
from warnings import simplefilter
from sklearn.exceptions import ConvergenceWarning

# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 13:41:26 2021

This file contains the functions to automate evaluate the classification models

@author: yipeng.song@hotmail.com
"""
# %% detailed CV metrics for binary classification problems
def repeated_KFold_CV(
    results,
    X,
    y,
    labels=[0, 1],
    cv=10,
    n_times=10,
    custom=False,
    given_metric=metrics.balanced_accuracy_score,
    n_jobs=10,
):
    """evaluate the selected models' performance using K-Fold CV

    Args:
        results (dict): key, model name; value, saved models and model selection.
        X (np.ndarray): X
        y (np.ndarray): y
        lables (list): [negative_level, positive_level]
        cv (int, optional): K-Fold CV. Defaults to 10.
        n_times (int, optional): repeated K-Fold CV. Defaults to 10.
        custom (bool, optional): whether to use custom cutoff. Only necessary for imbalanced classification problem.
        given_metric (function, optional): used to tune the custom cutoff.
        n_jobs (int, optional): number of cores to be used. Defaults to 10.

    Returns:
        RKFold_metrics: key, "custom" and "standard".
        RKFold_metrics["custom"] contains the results using custom cutoff optimal for a given metric;
        RKFold_metrics["standard"] contains the results using standard cutoff.
    """
    # extract the keys in the dict of the results
    model_names = list(results.keys())

    # get the metrics on all the data using K-Fold CV for the models
    RKFold_metrics_custom = {}
    RKFold_metrics_standard = {}
    for key in model_names:
        print(f"working on {key} ----------")
        selected_model = results[key].selected_model_
        metrics_custom, metrics_standard = repeated_KFold_CV_base_(
            selected_model,
            X=X,
            y=y,
            labels=labels,
            cv=cv,
            n_times=n_times,
            custom=custom,
            given_metric=given_metric,
            n_jobs=n_jobs,
        )
        if custom:
            RKFold_metrics_custom[key] = metrics_custom
        RKFold_metrics_standard[key] = metrics_standard

    # generate the model evaluation metrics
    RKFold_metrics = {}
    RKFold_metrics["custom"] = RKFold_metrics_custom
    RKFold_metrics["standard"] = RKFold_metrics_standard
    return RKFold_metrics


# %% repated K Fold CV for a specific model
def repeated_KFold_CV_base_(
    selected_model,
    X,
    y,
    labels,
    cv=10,
    n_times=10,
    custom=False,
    given_metric=metrics.balanced_accuracy_score,
    n_jobs=10,
):
    # create struct to hold the results
    metrics_custom = {}
    metrics_standard = {}

    # permutate the sample index to avoid exactly the same KFold splitting
    original_index = np.arange(len(y))
    for i in range(n_times):
        print(f"time {i} evaluation")

        # permutate the y index
        perm_index = np.random.permutation(original_index)
        X_perm = X[perm_index, :]
        y_perm = y[perm_index]

        custom_errors, standard_errors = KFold_CV_base_(
            selected_model,
            X_perm=X_perm,
            y_perm=y_perm,
            labels=labels,
            cv=cv,
            custom=custom,
            given_metric=given_metric,
            n_jobs=n_jobs,
        )
        if custom:
            metrics_custom[i] = custom_errors
        metrics_standard[i] = standard_errors

    # dict to dataframe
    if custom:
        metrics_custom = pd.DataFrame(metrics_custom)
    metrics_standard = pd.DataFrame(metrics_standard)

    return metrics_custom, metrics_standard


# %% K Fold CV for a specific model
def KFold_CV_base_(
    selected_model,
    X_perm,
    y_perm,
    labels,
    cv=10,
    custom=False,
    given_metric=metrics.balanced_accuracy_score,
    n_jobs=10,
):
    # get cv split for generating reproduiable results
    skcv = model_selection.StratifiedKFold(n_splits=cv, shuffle=False)

    # y_prob K-Fold CV
    y_prob = get_y_prob_cv(selected_model, X_perm, y_perm, cv=skcv, n_jobs=n_jobs)

    if custom:
        # generate cutoffs
        cutoffs = cutoffs = np.linspace(y_prob.min(), y_prob.max(), num=1000)

        # get the model's training scores for different cutoffs
        train_scores = get_train_scores(
            selected_model,
            X_perm,
            y_perm,
            cutoffs,
            labels,
            skcv=skcv,
            given_metric=given_metric,
        )

        # find the cut off
        mean_KFold_train_scores = train_scores.mean(axis=0)  # mean across to KFolds
        max_value = np.max(mean_KFold_train_scores)
        max_cutoffs = cutoffs[mean_KFold_train_scores == max_value]
        mean_cutoff = 0.5 * (max_cutoffs.min() + max_cutoffs.max())

        # evaluate the model for all the given metrics using custom cutoff
        y_hat_custom = prob_discretize(y_perm, y_prob, labels, cutoff=mean_cutoff)
        custom_errors = eval_metrics(y_perm, y_hat_custom, labels)

    # evaluate the model for all the given metrics using standard cutoff
    standard_cutoff = 0.5
    if hasattr(selected_model, "decision_function"):
        standard_cutoff = 0
    y_hat_standard = prob_discretize(y_perm, y_prob, labels, cutoff=standard_cutoff)
    standard_errors = eval_metrics(y_perm, y_hat_standard, labels)

    # compute the AUC and add AUC to above metrics
    AUC = metrics.roc_auc_score(y_perm, y_prob)
    if custom:
        custom_errors["AUC"] = AUC
    else:
        custom_errors = None
    standard_errors["AUC"] = AUC

    return custom_errors, standard_errors


# %% utility functions
# define a function to discretize the probability outputs to binary predictions
def prob_discretize(y, y_prob, labels, cutoff=0.5):
    """Dichotomize continuous probabilities to binary predictions

    Args:
        y (np.ndarray): outcome label
        y_prob (np.ndarray): the probability predictions of a machine learning model
        labels (list): the list contains the binary labels, [negative case, positive case]
        cutoff (float, optional): [description]. Defaults to 0.5.

    Returns:
        np.ndarray: the binary labels transformed from probability
    """
    y_pred = np.empty_like(y)
    y_pred.fill(labels[0])

    # discretize prob to binary labels
    y_pred[y_prob > cutoff] = labels[1]
    return y_pred


# get the training scores for different cutoffs
def get_train_scores(selected_model, X, y, cutoffs, labels, skcv, given_metric):
    cv_metrics = []
    for train_index, _ in skcv.split(X, y):
        # index out training data
        X_train, y_train = X[train_index, :], y[train_index]

        # fit the selected model on the train data
        selected_model.fit(X_train, y_train)

        # predict the train data
        y_train_prob = selected_model.predict_proba(X_train)[:, 1]
        cv_metrics.append(
            get_metrics_all_cutoffs(
                y_train,
                y_train_prob,
                cutoffs=cutoffs,
                labels=labels,
                given_metric=given_metric,
            )
        )
    return pd.DataFrame(cv_metrics)


def get_metrics_all_cutoffs(y_train, y_train_prob, cutoffs, labels, given_metric):
    # go through all the cutoffs
    metrics_cutoffs = np.zeros(len(cutoffs))
    for i, cutoff in enumerate(cutoffs):
        y_train_pred = prob_discretize(y_train, y_train_prob, labels, cutoff=cutoff)
        metrics_cutoffs[i] = given_metric(y_train, y_train_pred)

    return metrics_cutoffs


# define a function to calculate the different metrics
def eval_metrics(y_true, y_hat, labels):
    # confusion matrix
    CM = metrics.confusion_matrix(y_true, y_hat, labels=labels)
    TN = CM[0][0]
    FN = CM[1][0]
    TP = CM[1][1]
    FP = CM[0][1]

    # multiple evaluation metrics
    sensitivity = TP / (TP + FN)
    specificity = TN / (TN + FP)
    balanced_accuracy = (TP / (TP + FN) + TN / (TN + FP)) / 2
    recall = sensitivity
    precision = TP / (TP + FP)
    f1_score = 2 * TP / (2 * TP + FP + FN)

    # add negative and positive predictive value
    pos_pred_value = TP / (TP + FP)
    neg_pred_value = TN / (TN + FN)

    # metrics
    model_metrics = pd.Series(
        [
            sensitivity,
            specificity,
            balanced_accuracy,
            pos_pred_value,
            neg_pred_value,
            recall,
            precision,
            f1_score,
        ],
        index=[
            "sensitivity",
            "specificity",
            "balanced_accuracy",
            "positive_predictive_value",
            "negative_predictive_value",
            "recall",
            "precision",
            "f1_score",
        ],
    )

    return model_metrics


# define a function to return the cross validated predictions
def get_y_prob_cv(selected_model, X, y, cv, n_jobs):
    y_hat_prob = None

    # probability estimation
    if hasattr(selected_model, "predict_proba"):
        y_hat_prob = model_selection.cross_val_predict(
            selected_model, X, y, cv=cv, n_jobs=n_jobs, method="predict_proba"
        )[:, 1]

    # non probability estimation for svm model
    if hasattr(selected_model, "decision_function"):
        y_hat_prob = model_selection.cross_val_predict(
            selected_model, X, y, cv=cv, n_jobs=n_jobs, method="decision_function"
        )

    return y_hat_prob
