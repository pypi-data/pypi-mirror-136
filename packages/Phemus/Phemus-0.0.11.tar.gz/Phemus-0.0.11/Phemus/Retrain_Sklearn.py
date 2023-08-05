import joblib
import time
import random
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

# too specific to original input, deprecated
# def extract_inputs_old(filename):
#     X = []
#     Y = []
#     i = 0
#     neg_count = 0
#     pos_count = 0
#     with open(filename, "r") as ins:
#         for line in ins:
#             line = line.strip()
#             line1 = line.split(',')
#             if (i == 0):
#                 i += 1
#                 continue
#             L = list(map(int, line1[:-1]))
#             # L[sens_arg-1]=-1
#             X.append(L)

#             if (int(line1[-1]) == 0):
#                 Y.append(-1)
#                 neg_count = neg_count + 1
#             else:
#                 Y.append(1)
#                 pos_count = pos_count + 1

#     return X, Y

def extract_inputs(input_csv_dir, col_to_be_predicted_idx):
    df = open(input_csv_dir).readlines()
    
    X = []
    Y = []
    i = 0
    neg_count = 0
    pos_count = 0
    
    for line in df:
        if (i == 0): # first row, col name, skip
            i += 1
            continue
        line = line.strip().split(",")
        L = list(map(int, line[:col_to_be_predicted_idx] + line[col_to_be_predicted_idx + 1:])) # exclude col to be predicted 
        X.append(L)
        if (int(line[-1]) == -1):
            Y.append(-1)
            neg_count = neg_count + 1
        else:
            Y.append(1)
            pos_count = pos_count + 1

    return X, Y

def extract_array(input_csv_dir, col_to_be_predicted_idx):
    X, Y = extract_inputs(input_csv_dir, col_to_be_predicted_idx)
    X_original = np.array(X)
    Y_original = np.array(Y)
    return X, Y, X_original, Y_original

# num_trials = 100
# samples = 100

# classifier_name = config.classifier_name
# input_bounds = config.input_bounds
# num_params = config.num_params
# sensitive_param_idx = config.sensitive_param_idx

# retraining_inputs = config.retraining_inputs

def retrain(model, X_original, Y_original, X_additional, Y_additional):
    X = np.concatenate((X_original, X_additional), axis = 0)
    Y = np.concatenate((Y_original, Y_additional), axis = 0)

    model.fit(X, Y)
    return model

def get_random_input(num_params, input_bounds, sensitive_param_idx):
    x = []
    for i in range(num_params):
        random.seed(time.time())
        x.append(random.randint(input_bounds[i][0], input_bounds[i][1]))

    x[sensitive_param_idx] = 0
    return x

def evaluate_input(inp, model, sensitive_param_idx):
    inp0 = [int(i) for i in inp]
    inp1 = [int(i) for i in inp]

    inp0[sensitive_param_idx] = 0
    inp1[sensitive_param_idx] = 1

    inp0 = np.asarray(inp0)
    inp0 = np.reshape(inp0, (1, -1))

    inp1 = np.asarray(inp1)
    inp1 = np.reshape(inp1, (1, -1))

    out0 = model.predict(inp0)
    out1 = model.predict(inp1)

    return (abs(out0 + out1) == 0)

def get_estimate(model, num_trials, samples, sensitive_param_idx, num_params, input_bounds):
    estimate_array = []
    rolling_average = 0.0
    for i in range(num_trials):
        disc_count = 0
        total_count = 0
        for j in range(samples):
            total_count = total_count + 1
            if(evaluate_input(get_random_input(num_params, input_bounds, sensitive_param_idx), model, sensitive_param_idx)):
                disc_count = disc_count + 1

        estimate = float(disc_count)/total_count
        rolling_average = ((rolling_average * i) + estimate)/(i + 1)
        estimate_array.append(estimate)

        # print(estimate, rolling_average)

    print("Current biasedness:", np.average(estimate_array))
    return np.average(estimate_array)


def retrain_search(model, input_csv_dir, num_trials, samples, sensitive_param_idx, num_params, input_bounds, col_to_be_predicted_idx):
    current_model = model
    current_estimate = get_estimate(model, num_trials, samples, sensitive_param_idx, num_params, input_bounds)
    fairness = [] 
    fairness.append(current_estimate)
    
    X, Y, X_original, Y_original = extract_array(input_csv_dir, col_to_be_predicted_idx)
    X_retrain, Y_retrain = extract_inputs(input_csv_dir, col_to_be_predicted_idx)
    retrain_len = len(X_retrain)
    for i in range(7):
        X_additional = []
        Y_additional = []
        retraining_input_set = set()
        additive_percentage = random.uniform(pow(2, i), pow(2, i + 1))
        num_inputs_for_retrain = int((additive_percentage * len(X))/100)

        if (num_inputs_for_retrain > retrain_len):
            raise ValueError('Number of inputs in retraining are not enough. Please add more inputs')

        while (len(retraining_input_set) < num_inputs_for_retrain):
            retraining_input_set.add(random.randint(0, retrain_len - 1))

        for i in retraining_input_set:
            X_additional.append(X_retrain[i])
            Y_additional.append(Y_retrain[i])
        retrained_model = retrain(current_model, X_original, Y_original, np.array(X_additional), np.array(Y_additional))
        retrained_estimate = get_estimate(current_model, num_trials, samples, sensitive_param_idx, num_params, input_bounds)
        fairness.append(retrained_estimate)
        if (retrained_estimate > current_estimate):
            return current_model
        else:
            current_model = retrained_model
            current_estimate = retrained_estimate
            del retrained_estimate
            del retrained_model
    return current_model, fairness

def retrain_sklearn(input_pkl_dir, improved_pkl_dir, input_csv_dir, num_trials, samples,\
                            sensitive_param_idx, num_params, input_bounds, col_to_be_predicted_idx):
    
    original_model = joblib.load(input_pkl_dir)
    improved_model, fairness= retrain_search(original_model, input_csv_dir, num_trials, samples, \
                                                sensitive_param_idx, num_params, input_bounds, col_to_be_predicted_idx)
    # file_to_save_model = config.improved_classfier_name

    joblib.dump(improved_model, improved_pkl_dir)

    # display fairness improvement 
    plt.plot(fairness)
    plt.xticks(np.arange(0, len(fairness), 1.0))
    plt.xlabel("Number of Iterations")
    plt.ylabel("Percentage of Biased Outputs")
    plot_dir = input_csv_dir(".")[0].lower() + "_fairness_improvement.png"
    plt.savefig(plot_dir)

