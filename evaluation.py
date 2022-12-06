import numpy as np
from pandas import *
 
# reading CSV file
data = read_csv("results/performance-correctness.csv")
 
# converting column data to list
fit_original = data['fitness original'].tolist()
fit_bt_factor = data['fitness BT-Factor'].tolist()
fit_re_bt = data['fitness RE-BT'].tolist()

battery_bt_factor = data['BT-Factor battery over?'].tolist()
battery_re_bt = data['RE:BT battery over?'].tolist()
battery_re_bt_0_pruning = data['RE:BT (no pruning) battery over?'].tolist()


correctness_bt_factor = (len(battery_bt_factor) - sum(battery_bt_factor))/len(battery_bt_factor)*100
print("correctness_bt_factor", correctness_bt_factor)

correctness_re_bt = (len(battery_re_bt) - sum(battery_re_bt))/len(battery_re_bt)*100
print("correctness_re_bt", correctness_re_bt)

correctness_re_bt_0_pruning = (len(battery_re_bt_0_pruning) - sum(battery_re_bt_0_pruning))/len(battery_re_bt_0_pruning)*100
print("correctness_re_bt_0_pruning", correctness_re_bt_0_pruning)

print("\n\n200 simulations")
mean_original = np.mean(fit_original)
variance_original = np.var(fit_original)
print("\nOriginal BT")
print("mean is", mean_original)
print("var is", variance_original)

mean_bt_factor= np.mean(fit_bt_factor)
variance_bt_factor = np.var(fit_bt_factor)
print("\nBT Factor")
print("mean is", mean_bt_factor)
print("var is", variance_bt_factor)

mean_re_bt = np.mean(fit_re_bt)
variance_re_bt = np.var(fit_re_bt)
print("\nRE:BT")
print("mean is", mean_re_bt)
print("var is", variance_re_bt)

print("\n\nOnly", (len(battery_re_bt) - sum(battery_re_bt)) ,"RE:BT correct simulations")
correct_re_bt = [not elem for elem in battery_re_bt]

original = np.array(fit_original)[np.array(correct_re_bt)]
mean_original = np.mean(original)
variance_original = np.var(original)
print("\nOriginal BT")
print("mean is", mean_original)
print("var is", variance_original)

bt_factor = np.array(fit_bt_factor)[np.array(correct_re_bt)]
mean_bt_factor= np.mean(bt_factor)
var_bt_factor = np.var(bt_factor)
print("\nBT Factor")
print("mean is", mean_bt_factor)
print("var is", var_bt_factor)

re_bt = np.array(fit_re_bt)[np.array(correct_re_bt)]
mean_re_bt = np.mean(re_bt)
variance_re_bt = np.var(re_bt)
print("\nRE:BT")
print("mean is", mean_re_bt)
print("var is", variance_re_bt)