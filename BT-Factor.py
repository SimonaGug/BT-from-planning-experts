import numpy as np
#import sympy
from sympy import*
from pyeda.inter import *
import re
import os

import simulation.notebook_interface as notebook_interface
import simulation.behavior_tree as behavior_tree
behavior_tree.load_settings_from_file('simulation/tests/BT_TEST_SETTINGS.yaml')


# relative file paths
filename = "c50-rules.txt"

global defaul_action_and_horn_clauses 


defaul_action_and_horn_clauses = True

#create variables in sympy
X=50
V = symbols(f"VAR0:{X}")
V_dict = {f"VAR{i}": 
    V[i] for i in range(X)}
v = symbols(f"var0:{X}")
v_dict = {f"var{i}": 
    v[i] for i in range(X)}
v_dict.update(V_dict)

##################################################################
#Extract rules, conditions and actions from the rule file from c50
#
def extract_rules_from_C50 (filename):

    Rules = {}
    rule_line = 10000
    decision = ""
    rule = ""
    with open (filename, 'rt') as myfile:
        for Ln, current_line in enumerate(myfile,1):      
            #line where the rule begins
            if defaul_action_and_horn_clauses and "Default class" in current_line:
                default_action = current_line.replace("Default class: ", "").replace("\n", "") 
                #This overwrite the default action's rule
                Rules [default_action] = "default"
                return Rules
            elif "Rule " in current_line:
                decision = ""
                rule_line = Ln              
            #action line
            elif "-> " in current_line:
                rule_line = Ln + 1
                decision = current_line.split("!")[0].replace("	->  class ", "") + "!"
                if decision in Rules.keys():
                    rule= Rules[decision] + " OR " + rule
                rule = rule.replace("\t", "").replace ("\n", "")
                Rules [decision] = rule
                rule =""
                continue       
            #Rule conditions
            elif Ln > rule_line:  
                if rule == "":
                    first_condition = True
                if "{" in current_line:
                    stations = current_line.replace("}","").replace(" in ", " ").replace("\t", "").replace("\n", "").split("{")
                    stations_set = stations[1].split(",")
                    for idx, station in enumerate(stations_set):
                        if idx==0:
                            rule = rule + "(" +  stations[0].replace(" ", "") + "=" + station
                        else:
                            rule = rule + " OR " + stations[0].replace(" ", "") + "=" + station.replace(" ", "")
                    rule= rule + ")"
                elif first_condition:
                    rule = rule + current_line.replace(" ", "")
                else:
                    rule = rule + " AND " + current_line.replace(" ", "")
                first_condition = False
    return Rules

def dictionaries_variables_conditions(Rules):
    global Variables
    global Conditions

    Variables = {}
    Conditions = {}
    key= "VAR1"
    i=2
    for rule in Rules:
        variables = Rules[rule].replace('<=', '>').replace(' AND', ',').replace(' OR', ',').replace('(', "").replace(")", "")
        variables = variables.split(", ")
        for var in variables:
            if var not in Conditions and "default" not in var:
                Conditions[var] = key
                Variables[key] = var
                key= "VAR" + str(i) 
                i+= 1

def create_actions_dictionary(rules):
    global Actions
    Actions = {}
    key= "A"
    for rule in rules:
        if "default" in rules.get(rule):
            Actions["default"]=rule
        else:
            Actions[key]=rule
            key= chr(ord(key) + 1)
##################################################################


def rule_dictionary_into_logic_sentences(Rules, Conditions):
    logic_rules = []
    right_parentesis = False
    for rule in Rules:
        rule= Rules.get(rule)
        segments = rule.split(" ")
        logic_rule =""
        if "default" in rule:
            logic_rules.append(logic_rule)
            continue
        for segment in segments:
            if "(" in segment:
                segment= segment.replace("(", "")
                logic_rule= logic_rule + "("
            if ")" in segment:
                right_parentesis = True
                segment=segment.replace(")", "")
            if segment == "AND" :
                logic_rule = logic_rule + " & "
            elif segment == "OR" : 
                logic_rule = logic_rule + " | "
            else:
                if "<=" in segment:
                    segment = segment.replace('<=', '>')
                    #rule = rule + Conditions.get(segment).upper()
                    logic_rule = logic_rule + "~" + Conditions.get(segment)
                else:
                    logic_rule = logic_rule + Conditions.get(segment) 
            if right_parentesis:
                logic_rule= logic_rule + ")"
                right_parentesis = False
        logic_rules.append(logic_rule)  
    return logic_rules

def convert_to_horn_rules(rules, Actions):
    horn_rules = []
    for r, rule in enumerate(rules):
        if rule == "":
            horn_rules.append("default")
            continue
        rule = expr(rule)
        rule = rule.to_dnf()
        action= list(Actions.keys())[r] 
        rule = Implies(rule, action)
        horn_rule = rule.to_dnf()    
        horn_rules.append(horn_rule)
    return horn_rules

def convert_rule_into_logic(rules):
    logic_rules= []
    actions_in_order = []
    for r, rule in enumerate(rules):
        if defaul_action_and_horn_clauses:
            logic_rule=""
            rule=str(rule)
            rule_without_action = re.sub(r'[A-Z], ', '', rule)
            rule_without_action = re.sub(r', [A-Z]\)', ')', rule_without_action)
            action = "".join(set(rule.replace("VAR", "")).difference(set(rule_without_action.replace("VAR", ""))))
            logic_rule=sympify(str(rule_without_action))
        else:
            action =  list(Actions.keys())[r]
            logic_rule=sympify(str(rule))
        actions_in_order.append(action)
        logic_rules.append(logic_rule)
    return logic_rules, actions_in_order

def compute_frequencies(horn_rules):
    frequencies = {}
    for rule in horn_rules:
        if rule == "default":
            continue
        rule_str = str(rule.inputs).replace(" ","").replace("(","").replace(")","").split(",")
        for keys in rule_str:
            if "VAR" in keys:
                frequencies[keys] = frequencies.get(keys, 0) + 1
    frequencies = dict(sorted(frequencies.items(), key=lambda item: item[1], reverse= True))
    return frequencies 

def compute_rules_points(horn_rules, frequencies):
    rules_point = []
    rule_point =0
    for i, rule in enumerate(horn_rules):
        if rule == "default":
            rules_point = np.append(rules_point,-100)
            continue
        rule= expr(rule)
        rule_str = str(rule.inputs).replace("(","").replace(")","").replace(",","")
        variables = rule_str.split(" ")
        for v in variables:
            if "VAR" in v:
                rule_point =  rule_point + frequencies.get(v)
        rules_point = np.append(rules_point, rule_point/(len(variables)-1))       
        rule_point=0  
    return rules_point


def order_the_rules(horn_rules, rules_point):

    keydict = dict(zip(horn_rules, rules_point))
    horn_rules.sort(key=keydict.get , reverse = True)
    return horn_rules
    
            
########################
#Espresso minimizer

def espresso_minimazer(Rules):
    rule_dnfs = []
    for idx, rule in enumerate(Rules):
        if rule == "":
            rule_dnfs.append("")
            continue
        else:
            f = expr(rule)
            f = expr(rule).to_dnf()
            fm, = espresso_exprs(f)
            rule_dnfs.append(str(fm))
    return rule_dnfs


#convert the rules

def convert_rules_into_logic(rules):
    logic_minimized_rules= []
    for rule in rules:
        logic_rule=""
        rule=str(rule)
        logic_rule=sympify(str(rule))
        logic_minimized_rules.append(logic_rule)  
    return logic_minimized_rules

# convert logic rules into algebraic expressions 
                
def upper_repl(match):
     return match.group(1).upper()

def convert_logic_rules_into_algebraic_expression(rules_logic):
    algebraic_rules = []
    for logic_expression in rules_logic:
        logic_expression = str(logic_expression)
        logic_expression = logic_expression.replace("|", "+").replace(" & ", "*")
        logic_expression = re.sub(r'~([a-z])', upper_repl, logic_expression)
        algebraic_rules.append(logic_expression)  
    return algebraic_rules
    

def gfactor(f):
    d = divisor(f)
    if d == "0":
        return f   
    q, r = divide(f,d)
    #if q has only one term
    if len(str(q[0])) < 8:
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
            #is this necessary?
            if (r != 0):
                r = gfactor(r)
            return sympify(q, locals=v_dict)*sympify(d, locals=v_dict) + sympify(r, locals=v_dict)
        else:
            c = common_cube(d)
            return lf(f,c)
    
def lf(f, l):
    l= str(l).replace("[","").replace("]","")
    q, r = divide (f,l)
    q = gfactor(q[0])
    #it should work even without
    if (r != 0):
        r = gfactor(r)
    return sympify(l, locals=v_dict)*q + r

def common_cube(f):
    # if single cube
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
        f_cube_free = divide(f, str(cube))
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

    
###################### build the tree #########

def min_rules_alg_to_BT(min_alg_rules, actions_in_order, bt = ""):

    for rule_number, rule in enumerate(min_alg_rules):
        action_key = actions_in_order[rule_number]
        rule = sympify(rule)
        rule_simplified = simplify(rule)
        addenda = rule_simplified.args
        if "default" in str(rule):
            default_action = action= Actions.get("default")
            continue
        if defaul_action_and_horn_clauses:
            bt =  bt + " 'f(', "
        else:
            bt =  bt + " 's(', "
        for addendum in addenda:
            bt = bt + decompose_complex_addenda_horn(str(addendum))
        action= Actions.get(action_key)
        bt = bt + "'" + action + "', ')', \n"
        #bt = bt + "'" + action + "', ')', "
        #action_key= chr(ord(action_key) +1)
    if defaul_action_and_horn_clauses:
        bt = "['s('," + bt + "'" + default_action + "', ]"
    else:
        bt = "['p('," + bt + " ]" 
    return bt


def decompose_complex_addenda_horn(addendum, bt = ""):
    if len(addendum)<6:
        condition = find_the_condition_horn(addendum)
        bt = bt + "'" + condition + "',"
        return bt
        
    else:
        factors = sympify(addendum).args
        if (sorted(" + ".join([str(i) for i in factors])) == sorted(str(addendum) )):
            bt =  bt + " 'f(', " 
            for sub_addendum in factors:
                bt = bt + decompose_complex_addenda_horn(str(sub_addendum))
            bt= bt + "')',"
        else:
            bt =  bt + " 's(', "
            for factor in factors:
                bt = bt + decompose_complex_addenda_horn(str(factor))
            bt= bt + "')',"
        return bt  

def find_the_condition_horn(variable):
    condition=variable
    if variable[0].islower():
        condition = variable.replace("var", "VAR")
    condition = Variables.get(condition)
    if "at.station" in condition:
        condition = condition.replace('=', ' ').replace(".", " ")
        if variable.islower():
            condition = "not " + condition 
    elif variable.islower():
            condition = condition.replace('>', ' <= ').replace(".", " ")
    else: 
        condition = condition.replace('>', ' > ').replace(".", " ")
    return condition

#############################################


def main():
    '''Runs the full pipeline end to end'''
    Rules = extract_rules_from_C50(filename)
    dictionaries_variables_conditions(Rules)
    create_actions_dictionary(Rules)
    logic_sentences= rule_dictionary_into_logic_sentences(Rules, Conditions)
    min_rules = espresso_minimazer(logic_sentences)
    if defaul_action_and_horn_clauses:
        horn_rules= convert_to_horn_rules(min_rules, Actions)
        frequencies = compute_frequencies(horn_rules)
        rules_point = compute_rules_points(horn_rules, frequencies)
        ordered_rules = order_the_rules(horn_rules, rules_point)
        logic_rules, actions_in_order = convert_rule_into_logic(ordered_rules)
    else:
        logic_rules, actions_in_order = convert_rule_into_logic(min_rules)
    alg_horn_rules= convert_logic_rules_into_algebraic_expression(logic_rules)
    min_rules_alg = []
    for i, rule in enumerate(alg_horn_rules):
        rule = rule.replace("(", "").replace(")","").replace("~VAR", "var")
        alg_horn_rules[i] = alg_horn_rules[i].replace("~VAR", "var")
        rule = sympify(rule, locals=v_dict)
        rule_factor = gfactor(rule)
        rule_factor = str(rule_factor)

        min_rules_alg.append(rule_factor)

    bt = min_rules_alg_to_BT(min_rules_alg, actions_in_order)
    print("\nFINAL BT with BT-Factor and",defaul_action_and_horn_clauses ,"Horn Clauses flag\n\n", bt)


    #save as a dot file
    bt = bt.replace(' \n', '').replace("[", "").replace(", ]", "").replace("'", "").replace(", ", ",").split(",")

    if defaul_action_and_horn_clauses:     
        BT_path = "BTFactor"
        if not os.path.exists(BT_path):
            os.makedirs(BT_path)
    else:
        BT_path = "BTFactor_DNF"
        if not os.path.exists(BT_path):
            os.makedirs(BT_path)

    environment = notebook_interface.Environment(seed=0, verbose=False)
    environment.plot_individual(BT_path, 'behavior_tree', bt)

    with open(BT_path + '/BT.py', 'w') as fp:
        fp.write("bt_factor = " + str(bt))

if __name__ == '__main__':
    main()
