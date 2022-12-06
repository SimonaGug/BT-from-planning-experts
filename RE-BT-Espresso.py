import pandas as pd
import os
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn import tree
import graphviz
from sklearn.model_selection import KFold
import numpy as np
from sympy import*
import re
from pyeda.inter import *
import shutil

import simulation.notebook_interface as notebook_interface
import simulation.behavior_tree as behavior_tree
behavior_tree.load_settings_from_file('simulation/tests/BT_TEST_SETTINGS.yaml')


X=200
V = symbols(f"VAR0:{X}")
V_dict = {f"VAR{i}": V[i] for i in range(X)}
v = symbols(f"var0:{X}")
v_dict = {f"var{i}": v[i] for i in range(X)}
v_dict.update(V_dict)


##################################################
#  Copying RE:BT-Espresso original code functions

decision_tree_depth = 5
k_fold =  5

cur_prune_num = {
    "val": 0
}

var_cycle_count =  0


ACTION_DIFF_TOLERANCE = {
    "val": 0.3
}


LAST_ACTION_TAKEN_COLUMN_NAME = "LAST_ACTION_TAKEN"

def add_folder_to_directory(folder_name, working_directory):
    new_directory = os.fsdecode(os.path.join(working_directory, folder_name))
    if not os.path.isdir(new_directory):
        os.makedirs(new_directory)
    return new_directory

def plot_decision_tree(decision_tree_model, filename, feature_header):

    dot_data = tree.export_graphviz(decision_tree_model, out_file=None,
                                    feature_names=feature_header)
    graph = graphviz.Source(dot_data)
    graph.render(filename)

def k_fold_train_decision_tree_w_max_depth(num_k_folds, max_depth, output_full_path, features_data, labels_data):

    kf = KFold(shuffle=True, n_splits=num_k_folds)
    # build full tree on all data
    full_tree = tree.DecisionTreeClassifier(random_state=None,
                                            max_depth=max_depth).fit(features_data, labels_data)

    # get set of alphas from cost_complexity_pruning
    prune_path = full_tree.cost_complexity_pruning_path(
        features_data, labels_data)
    ccp_alphas, impurities = prune_path.ccp_alphas, prune_path.impurities

    train_scores = [0] * len(ccp_alphas)
    test_scores = [0] * len(ccp_alphas)

    # split data into train/test
    for train_index, test_index in kf.split(features_data):
        X_train, X_test = features_data.iloc[train_index], features_data.iloc[test_index]
        y_train, y_test = labels_data.iloc[train_index], labels_data.iloc[test_index]

        # create tree on each alpha
        for i, alpha in enumerate(ccp_alphas):
            if alpha < 0:  # bug in sklearn I think
                alpha *= -1
            clf = tree.DecisionTreeClassifier(
                random_state=None,
                max_depth=max_depth,
                ccp_alpha=alpha)
            clf = clf.fit(X_train, y_train)
            train_scores[i] += clf.score(X_train,
                                                y_train) / num_k_folds
            test_scores[i] += clf.score(X_test, y_test) / num_k_folds
    return ccp_alphas

def generate_full_binary_set():
    bin_set = "binary_features"
    # categrorical
    cat_set = "categorical_features"

def dt_to_pstring(dt, feature_names, label_names):
    sym_lookup = {}
    action_to_pstring = {}
    dt_to_pstring_recursive(dt, 0, "", sym_lookup,
                            action_to_pstring, feature_names, label_names)
    return sym_lookup, action_to_pstring

def dt_to_pstring_recursive(dt, node_index, current_pstring, sym_lookup, action_to_pstring, feature_names, label_names):
    if is_leaf_node(dt, node_index):
        process_leaf_node(dt, node_index, label_names,
                          action_to_pstring, current_pstring)
    else:
        process_non_leaf_node(dt, node_index, feature_names, sym_lookup,
                              current_pstring, action_to_pstring, label_names)

def process_leaf_node(dt, node_index, label_names, action_to_pstring, current_pstring):
    max_indices = find_max_indices_given_percent(dt.value[node_index])
    action = ""
    for i in max_indices:
        if action != "":
            action += "~||~"
        action += str(label_names[i])
    add_condition_to_action_dictionary(
        action_to_pstring,
        action,
        current_pstring)

def is_leaf_node(dt, node_index):
    """Checks if node at node_index is a leaf node to a DecisionTree

    Args:
        dt (sklearn.DecisionTree): decision tree to be examined
        node_index (int): index of node in dt

    Returns:
        bool : whether node at index is a leaf node in dt
    """
    return (dt.children_left[node_index] == -1
            and dt.children_right[node_index] == -1)



def add_condition_to_action_dictionary(dictionary, key, value):
    """Adds condition to [action] -> condition string dictionary

    Args:
        dictionary (dict[str,str]): action dictionary from action -> condition string
        key (str): action string
        value (str): condition string
    """
    if not key in dictionary:
        dictionary[key] = value
    elif value != "":  # deal with empty conditions
        dictionary[key] = dictionary[key] + " | " + value

def find_max_indices_given_percent(numpy_1D_array):
    """Finds array of max indices within a given percent
       ex. [[10, 0, 9.5, 7]], 0.1 -> [0,2]

    Args:
        numpy_1D_array (np.arr[int]): numpy array to find max of
        action_diff_tolerance (float): percent [0.0-1.0] to take values of

    Returns:
        np.arr(int) : indices of array falling within percdiff 
    """
    assert ACTION_DIFF_TOLERANCE["val"] >= 0 and ACTION_DIFF_TOLERANCE["val"] <= 1.0
    tmp_arr = numpy_1D_array[0]
    min_val = np.amax(numpy_1D_array) * \
        (1.0 - ACTION_DIFF_TOLERANCE["val"])
    indices = np.where(tmp_arr >= min_val)[0]
    return indices


def process_non_leaf_node(dt, node_index, feature_names, sym_lookup, current_pstring, action_to_pstring, label_names):
    lat_cond_lookup = dict()
    true_rule = None
    if is_bool_feature(dt, node_index, feature_names):
        # the == False exists because the tree denotes it as "IsNewExercise_True <= 0.5" which, when true, is actually Is_NewExercise_False
        true_rule = invert_expression(feature_names[dt.feature[node_index]])
    else:
        true_rule = feature_names[dt.feature[node_index]] + " <= " + str(
            round(dt.threshold[node_index], 3))
    false_rule = invert_expression(true_rule)

    true_letter = None
    false_letter = None

    # Note: this is very jank, we invert the rules of the dt for true letters to be ~ because of set up of dtree
    if (not true_rule in sym_lookup) and (not false_rule in sym_lookup):
        add_condition_to_action_dictionary(
            sym_lookup,
            false_rule,
            get_current_var_name())

    # bug with adding vars multiple times maybe here, likely needs to be moved up, maybe not
    if false_rule in sym_lookup:
        false_letter = sym_lookup.get(false_rule)
        true_letter = "~" + false_letter

    build_last_action_taken_dict(
        false_rule, false_letter)  # uses jank from above

    left_pstring = true_letter if current_pstring == "" else current_pstring + \
        " & " + true_letter
    right_pstring = false_letter if current_pstring == "" else current_pstring + \
        " & " + false_letter

    # traverse left side of tree (true condition)
    dt_to_pstring_recursive(dt,
                            dt.children_left[node_index],
                            left_pstring,
                            sym_lookup,
                            action_to_pstring,
                            feature_names,
                            label_names)

    # traverse right side of tree (false condition)
    dt_to_pstring_recursive(dt,
                            dt.children_right[node_index],
                            right_pstring,
                            sym_lookup,
                            action_to_pstring,
                            feature_names,
                            label_names)
    # remove all LAT from string

def get_current_var_name():
    global var_cycle_count
    tmp = "VAR" + str(var_cycle_count)
    var_cycle_count += 1
    return tmp


def is_bool_feature(dt, node_index, feature_names):
    binary_feature_set = set()
    name = feature_names[dt.feature[node_index]]
    return name in binary_feature_set or is_last_action_taken_condition(name) or ("True" in name)

def is_last_action_taken_condition(condition):
    return LAST_ACTION_TAKEN_COLUMN_NAME in condition and not "No Entry" in condition

def build_last_action_taken_dict(condition, cond_symbol):
    global lat_cond_lookup
    if is_last_action_taken_condition(condition) and cond_symbol not in lat_cond_lookup:
        lat_cond_lookup[cond_symbol] = condition.replace(
            LAST_ACTION_TAKEN_COLUMN_NAME + "_", "")

def invert_expression(exp):
    """Inverts and returns logical operator expressions
       ex. "<" -> ">="

    Args:
        exp (str): original conditional expression


    Returns:
        str: inverted string representation of original conditional expression
    """
    if ">=" in exp:
        return exp.replace(">=", "<")
    elif "<=" in exp:
        return exp.replace("<=", ">")
    elif ">" in exp:
        return exp.replace(">", "<=")
    elif "<" in exp:
        return exp.replace("<", ">=")
    elif "True" in exp:
        return exp.replace("True", "False")
    elif "False" in exp:
        return exp.replace("False", "True")
    else:
        return exp

##################################################

def convert_rules_into_logic_expressions(Rules):
    logic_rules = []
    for rule in Rules:
        rule= Rules.get(rule)
        logic_rules.append(rule)
    return logic_rules


#Espresso minimizer
def espresso_minimazer(Rules):
    rule_dnfs = []
    for idx, rule in enumerate(Rules):
        f = expr(rule)
        f = expr(rule).to_dnf()
        fm, = espresso_exprs(f)
        rule_dnfs.append(str(fm))
    return rule_dnfs

def convert_expr_into_logic(rules):
    logic_minimized_rules= []
    for rule in rules:
        logic_rule=""
        rule=str(rule)
        logic_rule=sympify(str(rule))
        logic_minimized_rules.append(logic_rule)  
    return logic_minimized_rules
                
def upper_repl(match):
     return match.group(1).upper()

def convert_logic_expr_into_algebraic_expr(logic_expressions):
    algebraic_expressions = []
    for expr in logic_expressions:
        expr = str(expr)
        expr = expr.replace("|", "+").replace(" & ", "*")
        expr = re.sub(r'~([a-z])', upper_repl, expr)
        algebraic_expressions.append(expr)  
    return algebraic_expressions

def convert_logic_rules_into_algebraic_expression_(horn_rules):
    logic_horn_rules= []
    actions_in_order = []
    for rule in horn_rules:
        logic_rule=""
        rule=str(rule)
        rule_without_action = re.sub(r'[A-Z], ', '', rule)
        rule_without_action = re.sub(r', [A-Z]\)', ')', rule_without_action)
        action = "".join(set(rule.replace("VAR", "")).difference(set(rule_without_action.replace("VAR", ""))))
        logic_rule=sympify(str(rule_without_action))
        actions_in_order.append(action)
        logic_horn_rules.append(logic_rule)  
    return logic_horn_rules,actions_in_order
    

####################################################
# factorization

def gfactor(f):
    d = divisor(f)
    if d == "0":
        return f   
    q, r = divide(f,d)

    if len(str(q[0])) == 1:
        return lf(f, q[0])   
    else:
        q = make_cube_free(q[0])
        d,r =  divide(f,q)
        if d[0] == 0 :
            return f
        if cube_free(d[0]):
            if "1" not in q:
                q = gfactor(q)
            d = gfactor(d[0])
            if (r != 0):
                r = gfactor(r)
            return sympify(q, locals=v_dict)*sympify(d, locals=v_dict) + sympify(r, locals=v_dict)
        else:
            c = common_cube(d)
            return lf(f,c)
    
def lf(f, c):
    l= str(c).replace("[","").replace("]","")
    q, r = divide (f,l)
    q = gfactor(q[0])
    if (r != 0):
        r = gfactor(r)
    return sympify(l, locals=v_dict)*q + r

def common_cube(f):
    #if single cube
    if "+" not in str(f):
        return f
    cubes =  str(f).replace(" + ","+").replace("[","").replace("]","").split("+")
    c1 = cubes[0]
    c1_var = c1.split("*")
    common_chars_list = []
    for c in range(1, len(cubes)):
        common_chars = ''.join([i for i in c1_var if re.search(i, cubes[c])])
        common_chars_list.append(common_chars)
        if common_chars == [""]:
            return ""
    if len(common_chars) == 0:
        return ""
    elif len(common_chars) == 1:
        common_var = common_chars[0]
    else:
        for i in range(1, len(common_chars),1):
            s1=common_chars[0]
            common_var = ''.join(sorted(set(s1) &
            set(common_chars[i]), key = s1.index)) 
            s1= common_var
    if common_var == "":
            return ""
    common_cube= sympify(common_var, locals=v_dict) 
    return common_cube


def make_cube_free(f):
    if cube_free(f):
        return str(f)
    cube = common_cube(f)
    if str(cube) != "":
        f_cube_free, remainder = divide(f, str(cube))
        return str(f_cube_free).replace("[","").replace("]","")
    else:
        return str(f)
    

def cube_free(f):
    if "+" not in str(f):
        return False
    f_str =  str(f).replace(" ","").replace("+","*").replace("[","").replace("]","")
    literals = f_str.split("*")
    for l in literals:
        q, r = divide(f, l)
        if r == 0:
            return False
    return True

def divide(f, d):
    q, r = reduced(f, [d])
    #Needed for a bug in the sympy library
    r = str(r)
    if "-" in r:
        q= [0]
        r= f
        return q,r
    r = sympify (r, locals=v_dict)
    return q,r

def divisor(f):
    frequencies = {}
    f_str = str(f).replace(" ","").replace("+","*")
    keys = f_str.split("*")
    frequencies = dict()
    for i in keys:
        frequencies[i] = frequencies.get(i, 0) + 1
    most_common_condition = max(frequencies, key=frequencies.get)
    if frequencies[most_common_condition]>1:
        return most_common_condition
    else:
        return "0"

#end factorization
###################################################

############################################
# Build BT 
    
def algebraic_rules_to_BT(min_alg_rules, alg_rules, actions, bt = ""):

    for rule_number, rule in enumerate(min_alg_rules):
        rule = sympify(rule, locals=v_dict)
        rule_simplified = simplify(rule)
        addenda = rule_simplified.args
        if ("*" not in str(rule_simplified)) & ("+" not in str(rule_simplified)):
            addenda = [rule_simplified]
        if ((str(rule) == str(alg_rules[rule_number])) & (" + " in str(rule_simplified))):
            bt =  bt + " 'f(', "
        else:
            bt =  bt + " 's(', "
        for addendum in addenda:
            bt = bt + decompose_complex_addenda(str(addendum))
        action= actions[rule_number]
        bt = bt + "'" + action + "', ')', \n"
    bt = "[ 'p('," + bt + "]"
    return bt


def decompose_complex_addenda(addendum, bt = ""):
    if len(addendum)==4:
        condition = find_the_condition(addendum)
        bt = bt + "'" + condition + "',"
        return bt
        
    else:
        factors = sympify(addendum).args
        if (sorted(" + ".join([str(i) for i in factors])) == sorted(str(addendum) )):
            bt =  bt + "'f(', " 
            for sub_addendum in factors:
                bt = bt + decompose_complex_addenda(str(sub_addendum))
            bt= bt + "')',"          
        else:
            bt =  bt + "'s(', "
            for factor in factors:
                bt = bt + decompose_complex_addenda(str(factor))
            bt= bt + "')',"
        return bt  

def find_the_condition(variable):
    condition = variable
    condition = condition.replace("var", "VAR")
    condition = Variables.get(condition)
    if "at station" in condition:
        condition = condition.replace(' > 0.5', '')
        if "var" in variable:
            condition = "not " + condition
    if "var" in variable:
            condition = condition.replace('>', ' <= ')
    return condition

############################################

def combine_folder_and_working_dir(folder_name, working_directory):
    if working_directory:
        return os.fsdecode(os.path.join(working_directory, folder_name))
    return folder_name


def does_folder_exist_in_directory(folder_name, working_directory=None):
    potential_directory = combine_folder_and_working_dir(
        folder_name, working_directory)
    return os.path.isdir(potential_directory), potential_directory


def remove_folder_if_exists(folder_name, working_directory=None):
    dir_exists, dir_path = does_folder_exist_in_directory(
        folder_name, working_directory)
    if dir_exists:
        print(f"Removing prior directory {dir_path}")
        shutil.rmtree(dir_path)

#  MAIN   #

# load dataset
traces = pd.read_csv("ExecutedTracesOneHot.csv", header=0)

#split dataset in features and target variable
X = traces.iloc[:,:-1]
y = traces.Decision # Target variable

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1) # 70% training and 30% test

# Create Decision Tree classifer object
clf = DecisionTreeClassifier(random_state= None ,
                                          max_depth=decision_tree_depth)

# Train Decision Tree Classifer
clf = clf.fit(X, y)

#Predict the response for test dataset
y_pred = clf.predict(X_test)

label_encoding = ['charge!', 'idle!', 'move to CHARGE1!', 'move to CONVEYOR_HEAVY!', 'move to CONVEYOR_LIGHT!', 'move to DELIVERY!', 'pick!', 'place!']
#label_encoding = clf.classes_

# Model Accuracy, how often is the classifier correct?
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

output_path ="RE-BT-Espresso-dot-files"
#dot_pdf_header = "dot-file"

remove_folder_if_exists(output_path)

#PrunePath = add_folder_to_directory(output_path, "")

#dot_pdf_full_path = os.fsdecode(
#            os.path.join(output_path, dot_pdf_header))
#plot_decision_tree(clf, dot_pdf_full_path, X.columns)

prune_path = clf.cost_complexity_pruning_path(
        X, y)
#ccp_alphas, impurities = prune_path.ccp_alphas, prune_path.impurities


clfs = []
train_scores = []
run_alphas = set()
i = 0
ccp_alphas = k_fold_train_decision_tree_w_max_depth(
            k_fold, decision_tree_depth, output_path, X, y)
ccp_alpha_list_copy = ccp_alphas.copy()
bt_tree_filepath_list = []

BTs_RE_BT_plus_factorization = []
BTs_RE_BT_method = []
alphas = []
possible_to_improve = []

#comment to obtain different alphas everytime
ccp_alpha_list_copy = [0.0 , 0.0008702702702702704 , 0.002275761475761476 , 0.0023387234042553198 , 0.00286216824111561 , 0.004518119197364479 , 0.01613263904845741 , 0.017295262636850696 , 0.021831437125748504 , 0.028595685907316433 , 0.04565415414611293 , 0.06448135999711224 , 0.10655000496981389 , 0.11300443126357335 , 0.1220828974320117]


for ccp_alpha in ccp_alpha_list_copy:
    cur_prune_num["val"] = i
    if ccp_alpha < 0:  # bug in sklearn I think
        ccp_alpha *= -1
    if ccp_alpha in run_alphas:  # dublicate zero ccp due to low rounding float
        ccp_alphas = np.delete(ccp_alphas, i)
        train_scores = np.delete(train_scores, i)
        test_scores = np.delete(test_scores, i)
        continue
    run_alphas.add(ccp_alpha)

    clf = tree.DecisionTreeClassifier(random_state=None,
                                        max_depth=decision_tree_depth, ccp_alpha=ccp_alpha)
    clf.fit(X, y)
    score = clf.score(X, y)

    clfs.append(clf)
    train_scores.append(score)

    #newPrunePath = add_folder_to_directory(
    #    "Pruning_{0}_{1:.6g}".format(i, ccp_alpha), output_path)
    #decision_tree_path = os.fsdecode(os.path.join(
    #    newPrunePath, "{0}_kFold_{1}_maxDepth_{2}_{3:.6g}_prune".format(k_fold, decision_tree_depth, i, ccp_alpha)))
    #plot_decision_tree(clf, decision_tree_path,
    #                    X.columns)

    decision_tree_obj = clf.tree_

    full_binary_set = generate_full_binary_set()

    sym_lookup, action_to_pstring = dt_to_pstring(decision_tree_obj,X.columns, label_encoding)

    if len(sym_lookup) != 0:
        logic_expression = convert_rules_into_logic_expressions(action_to_pstring)
        actions = list(action_to_pstring.keys())
        Variables = {value:key for key, value in sym_lookup.items()}
        minimized_expression = espresso_minimazer(logic_expression)
        minimized_logic_expression = convert_expr_into_logic(minimized_expression)
        alg_rules= convert_logic_expr_into_algebraic_expr(minimized_logic_expression)

        rules = []
        factorized_rules = []
        for rule in alg_rules:
            rule= rule.replace("~VAR", "var")
            rule = sympify(str(rule), locals=v_dict)
            # if applying extra factorization step
            rule_factor = gfactor(rule)
            factorized_rules.append(rule_factor)
            rules.append(rule)
            
        bt_re_espresso_plus_factorization = algebraic_rules_to_BT(factorized_rules, alg_rules, actions)
        bt_re_espresso = algebraic_rules_to_BT(rules, alg_rules, actions)
        print("BT with RE BT Espresso\n", bt_re_espresso)
        print("BT with RE BT Espresso and factorization\n\n", bt_re_espresso_plus_factorization)
        if bt_re_espresso_plus_factorization == bt_re_espresso:
            possible_to_improve.append('False')
        else:
            possible_to_improve.append('True')
        BTs_RE_BT_plus_factorization.append(bt_re_espresso_plus_factorization)
        BTs_RE_BT_method.append(bt_re_espresso)
        alphas.append(str(ccp_alpha))
        var_cycle_count = 0


#save as a dot file, not really needed as I have it already in the re-bt-espresso-dot-files folder?
print(BTs_RE_BT_method[0])
bt_re_espresso = BTs_RE_BT_method[0].replace(' \n', '').replace("[ ", "").replace(",]", "").replace("'", "").replace(", ", ",").split(",")
print(bt_re_espresso)
BT_RE_Espresso_path = "REBTEspresso"
if not os.path.exists(BT_RE_Espresso_path):
    os.makedirs(BT_RE_Espresso_path)

with open(BT_RE_Espresso_path + '/BT.py', 'w') as fp:
        fp.write("re_bt_espresso =" + (" , ".join(BTs_RE_BT_method)).replace(" \" ", ""))
        fp.close()
with open(BT_RE_Espresso_path + '/alpha.py', 'w') as fp:
        fp.write("alphas = [" + " , ".join(alphas) + "]")
        fp.close()
with open(BT_RE_Espresso_path + '/possible_to_improve.py', 'w') as fp:
        fp.write("possible_to_improve = [" + " , ".join(possible_to_improve) + "]")
        fp.close()


environment = notebook_interface.Environment(seed=0, verbose=False)
environment.plot_individual(BT_RE_Espresso_path, 'behavior_tree', bt_re_espresso)

