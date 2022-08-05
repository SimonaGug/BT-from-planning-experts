from http.client import RemoteDisconnected
import numpy as np
import sympy
from sympy import*
from pyeda.inter import *
import re
import os

import sys
import simulation.notebook_interface as notebook_interface
import simulation.behavior_tree as behavior_tree
behavior_tree.load_settings_from_file('simulation/tests/BT_TEST_SETTINGS.yaml')


# relative file paths
filename = "c50-rules.txt"

global defaul_action_and_horn_clauses 


defaul_action_and_horn_clauses = False

#create variables in sympy
X=50
V = symbols(f"VAR0:{X}")
V_dict = {f"VAR{i}": V[i] for i in range(X)}
v = symbols(f"var0:{X}")
v_dict = {f"var{i}": v[i] for i in range(X)}
v_dict.update(V_dict)

##################################################################
#Extract rukes, conditions and actions from the rule file from c50
#
def extract_rules_from_C50 (filename, verbose=0):

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
                if verbose > 0:        
                    print("\nFinal set of rules\n", Rules)
                return Rules
            elif "Rule " in current_line:
                decision = ""
                rule_line = Ln 
                if verbose >0 :
                    print("\nLine where the rule begins", Ln)               
            #action line
            elif "-> " in current_line:
                rule_line = Ln + 1
                decision = current_line.split("!")[0].replace("	->  class ", "") + "!"
                if decision in Rules.keys():
                    rule= Rules[decision] + " OR " + rule
                if verbose > 0:
                    print("Action", decision)
                rule = rule.replace("\t", "").replace ("\n", "")
                Rules [decision] = rule
                if verbose >0:
                    print("Rule", rule)
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
                if verbose >1:
                    print("Rule", rule)
    return Rules

def dictionaries_variables_conditions(Rules, verbose=0):
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
    if verbose >0:
        print("dictionary variables-coditions \n", Variables)
        print("dictionary coditions-variables \n", Conditions)

def create_actions_dictionary(rules, verbose=0):
    global Actions
    Actions = {}
    key= "A"
    for rule in rules:
        if "default" in rules.get(rule):
            Actions["default"]=rule
        else:
            Actions[key]=rule
            key= chr(ord(key) + 1)
    if verbose >0:
        print(Actions)
##################################################################


def rule_dictionary_into_logic_sentences(Rules, Conditions, verbose=0):
    logic_rules = []
    right_parentesis = False
    for rule in Rules:
        rule= Rules.get(rule)
        segments = rule.split(" ")
        if verbose >0:
            print("\nRule is \n", rule)
            print("Segments", segments)
        logic_rule =""
        if "default" in rule:
            logic_rules.append(logic_rule)
            continue
        for segment in segments:
            if verbose >0:
                print("Segment is ", segment)
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
            if verbose >0:
                print("Logic rule...\n",logic_rule)
        logic_rules.append(logic_rule)  
        if verbose >0:
            print("Logic rule is \n",logic_rule)

    if verbose>0:
        print(logic_rules)
    return logic_rules

def convert_to_horn_rules(rules, Actions, verbose = 0):
    horn_rules = []
    for r, rule in enumerate(rules):
        if rule == "":
            horn_rules.append("default")
            continue
        if verbose >0:
            print(rule)
            print(type(rule))
            print(expr(rule))
        rule = expr(rule)
        rule = rule.to_dnf()
        action= list(Actions.keys())[r] 
        rule = Implies(rule, action)
        horn_rule = rule.to_dnf()    
        if verbose>1:
            print(horn_rule)
        horn_rules.append(horn_rule)
    if verbose >0:
            print("The horn rules are \n", horn_rules)
    return horn_rules

def convert_rule_into_logic(rules, verbose = 0):
    logic_rules= []
    actions_in_order = []
    for r, rule in enumerate(rules):
        if verbose >0:
            print("\nOriginal rule", rule)
        if defaul_action_and_horn_clauses:
            logic_rule=""
            rule=str(rule)
            rule_without_action = re.sub(r'[A-Z], ', '', rule)
            rule_without_action = re.sub(r', [A-Z]\)', ')', rule_without_action)
            action = "".join(set(rule.replace("VAR", "")).difference(set(rule_without_action.replace("VAR", ""))))
            logic_rule=sympify(str(rule_without_action))
            if verbose >0:
                #print("Rule without action", rule_without_action)
                print("Logic rule", logic_rule)
                print("Only the action", action)
        else:
            action =  list(Actions.keys())[r]
            logic_rule=sympify(str(rule))
        actions_in_order.append(action)
        logic_rules.append(logic_rule)
    return logic_rules, actions_in_order

def compute_frequencies(horn_rules, verbose = 0):
    if verbose>1:
        print(horn_rules)
    frequencies = {}
    for rule in horn_rules:
        if rule == "default":
            continue
        if verbose>1:
            print("literals in the rule")
            print(rule.inputs)
        rule_str = str(rule.inputs).replace(" ","").replace("(","").replace(")","").split(",")
        for keys in rule_str:
            if "VAR" in keys:
                frequencies[keys] = frequencies.get(keys, 0) + 1
        if verbose>1:
            print(frequencies)  
    frequencies = dict(sorted(frequencies.items(), key=lambda item: item[1], reverse= True))
    if verbose >0:
        print(frequencies)
    return frequencies 

def compute_rules_points(horn_rules, frequencies, verbose =0):
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
        if verbose>0:
            print("The rule is \n", rule)
            print("The list of the points is \n", rules_point)
    if verbose>0:
        print("The final list of the points is \n" , rules_point)    
    return rules_point


def order_the_rules(horn_rules, rules_point, verbose = 0):

    keydict = dict(zip(horn_rules, rules_point))
    horn_rules.sort(key=keydict.get , reverse = True)
    
    if verbose >0:
        print("The ordered horn rules are\n", horn_rules)
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

def convert_rules_into_logic(rules, verbose = 0):
    logic_minimized_rules= []
    for rule in rules:
        logic_rule=""
        rule=str(rule)
        logic_rule=sympify(str(rule))
        if verbose >0:
            print("Rule without action", rule)
            print("Logic rule", logic_rule)
        logic_minimized_rules.append(logic_rule)  
    return logic_minimized_rules

# convert logic rules into algebraic expressions 
                
def upper_repl(match):
     return match.group(1).upper()

def convert_logic_rules_into_algebraic_expression(rules_logic, verbose = 0 ):
    algebraic_rules = []
    for logic_expression in rules_logic:
        logic_expression = str(logic_expression)
        if verbose >0:
            print("\nBefore", logic_expression)
        logic_expression = logic_expression.replace("|", "+").replace(" & ", "*")
        logic_expression = re.sub(r'~([a-z])', upper_repl, logic_expression)
        if verbose >0:
            print("After", logic_expression)
        algebraic_rules.append(logic_expression)  
    if verbose >0:
        print("\n\n Algebraic Rules\n",algebraic_rules)
    return algebraic_rules
    

#logic factorization
def gfactor(f, verbose = 0):
    if verbose == 1:
        print("\nCalling g factor on ", f)
    d = divisor(f, verbose)
    if d == "0":
        return f   
    q, r = divide(f,d, verbose)

    #if q has only one term
    if q[0] == 1:
        print("Im here and q[0] is 1")
        if verbose == 1:
            print("Q has only one term so I return ", f)
        return f
    # added by me
    if len(str(q[0])) == 1:
        print("Im here and len(str(q[0]))  is 1")
        return lf(f, q[0])   
    else:
        q = make_cube_free(q[0], verbose)
        d,r =  divide(f,q, verbose)
        if verbose == 1 :
            print("Is the result of the division", d, " cube free?", cube_free(d[0]))
        if cube_free(d[0]):
            #added by me
            if "1" not in q:
                q = gfactor(q, verbose)
            #if d!=1:
            d = gfactor(d[0], verbose)
            #added by me (but it should work even without)
            if (r != 0):
                r = gfactor(r, verbose)
            return sympify(q, locals=v_dict)*sympify(d, locals=v_dict) + sympify(r, locals=v_dict)
        else:
            c = common_cube(d, verbose)
            return lf(f,c, verbose)
    
def lf(f, c, verbose = 0):
    if verbose == 1:
        print("\nCalling lf on f = ", f, "with c=", c)
    l = best_literal (f,c, verbose)  
    q, r = divide (f,l, verbose)
    c = common_cube(q, verbose)
    q = gfactor(q[0], verbose)
    #added by me (but it should work even without)
    if (r != 0):
        r = gfactor(r, verbose)
    return sympify(l, locals=v_dict)*q + r

def common_cube(f, verbose = 0):
 
 #returns the largest common cube of Q
    if verbose == 1:
        print("Finding the common cube of function ", f)
    # one addedum
    if "+" not in str(f):
        if verbose == 1:
            print(f, " is single cube")
        return f
    cubes =  str(f).replace(" + ","+").replace("[","").replace("]","").split("+")
    c1 = cubes[0]
    c1_var = c1.split("*")
    if verbose == 1:
        print("The cubes in f are: ", cubes)
    common_chars_list = []
    for c in range(1, len(cubes)):
        common_chars = ''.join([i for i in c1_var if re.search(i, cubes[c])])
        common_chars_list.append(common_chars)
        if common_chars == [""]:
            if verbose == 1:
                print("There is no common cube")
            return ""
    if verbose == 1:
        print("The common cube is", common_chars)
    if len(common_chars) == 0:
        if verbose == 1:
            print("There is no common cube")
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
            if verbose == 1:
                print("There is no common cube")
            return ""
    common_cube= sympify(common_var, locals=v_dict) 
    return common_cube


def make_cube_free(f, verbose = 0):
    if verbose == 1:
        print("Making cube free function f =  ", f)
    if cube_free(f):
        if verbose == 1:
            print(f, " is already cube free")
        return str(f)
    cube = common_cube(f)
    if str(cube) != "":
        f_cube_free, remainder = divide(f, str(cube))
        if verbose == 1:
            print(f, "cube free is ",f_cube_free)
        return str(f_cube_free).replace("[","").replace("]","")
    else:
        if verbose ==1:
            print(f, " is already cube free")
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

def divide(f, d, verbose=0):
    q, r = reduced(f, [d])
    #Needed for a bug in the sympy library
    r = str(r)
    if verbose == 1:
        print("Dividing", f, "with \"", d, "\" the result is\n ", q, "remainder = ", r)
    if "-" in r:
        q= [0]
        r= f
        if verbose == 1:
             print("The remainder is negative. Therefore q is\n ", q, "remainder = ", r)
        return q,r
    r = sympify (r, locals=v_dict)
    return q,r

def divisor(f, verbose =0):
    frequencies = {}
    f_str = str(f).replace(" ","").replace("+","*")
    keys = f_str.split("*")
    frequencies = dict()
    for i in keys:
        frequencies[i] = frequencies.get(i, 0) + 1
    most_common_literal = max(frequencies, key=frequencies.get)
    if verbose == 1:
        print("The divisor (maximum value) is :",most_common_literal)
    if frequencies[most_common_literal]>1:
        return most_common_literal
    else:
        return "0"

def best_literal(f,c, verbose = 0):
    frequencies = {}
    f_str = str(f).replace(" ","").replace("+","*")
    keys = f_str.split("*")
    frequencies = dict()
    for i in keys:
        frequencies[i] = frequencies.get(i, 0) + 1
    best_literal = max(frequencies, key=frequencies.get)
    if verbose == 1:
        print("Best literal among", frequencies, "is: ",best_literal)
    return best_literal


    
###################### build the tree #########

def min_rules_alg_to_BT(min_alg_rules, alg_rules, actions_in_order, verbose =0, bt = ""):

    for rule_number, rule in enumerate(min_alg_rules):
        action_key = actions_in_order[rule_number]
        rule = sympify(rule)
        rule_simplified = simplify(rule)
        addenda = rule_simplified.args
        if verbose>0:
            print("\nRule", rule_simplified)
        if verbose>3:
            print("Addenda", addenda)
        if "default" in str(rule):
            default_action = action= Actions.get("default")
            continue
        if defaul_action_and_horn_clauses:
            bt =  bt + " 'f(', "
        else:
            bt =  bt + " 's(', "
        for addendum in addenda:
            bt = bt + decompose_complex_addenda_horn(str(addendum), verbose)
            if verbose>3:
                print("BT after the addendum \n", bt)
        if verbose>0:
            print("BT after this rule \n", bt)
        action= Actions.get(action_key)
        if verbose>0:
            print("Action key ", action_key)
            print("Action ", action)
        bt = bt + "'" + action + "', ')', \n"
        #bt = bt + "'" + action + "', ')', "
        if verbose>3:
                print("BT after the action \n", bt)
        #action_key= chr(ord(action_key) +1)
    if defaul_action_and_horn_clauses:
        bt = "['s('," + bt + "'" + default_action + "', ]"
    else:
        bt = "['p('," + bt + " ]" 
    return bt


def decompose_complex_addenda_horn(addendum, verbose = 0, bt = ""):
    if len(addendum)<6:
        condition = find_the_condition_horn(addendum)
        if verbose>2:
            print("Key", addendum, ", condition is ", condition)
        bt = bt + "'" + condition + "',"
        return bt
        
    else:
        factors = sympify(addendum).args
        if (sorted(" + ".join([str(i) for i in factors])) == sorted(str(addendum) )):
            bt =  bt + " 'f(', " 
            for sub_addendum in factors:
                bt = bt + decompose_complex_addenda_horn(str(sub_addendum), verbose)
            bt= bt + "')',"
            if verbose>6:
                print("bt is", bt)
        else:
            bt =  bt + " 's(', "
            for factor in factors:
                bt = bt + decompose_complex_addenda_horn(str(factor), verbose)
            bt= bt + "')',"
            if verbose>6:
                print("bt is", bt)

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
    Rules = extract_rules_from_C50(filename, verbose = 0)
    #print("Final set of rules\n\n", Rules)
    dictionaries_variables_conditions(Rules)
    #print(Variables)
    #print(Conditions)
    create_actions_dictionary(Rules)
    #print(Actions)
    logic_sentences= rule_dictionary_into_logic_sentences(Rules, Conditions, 0)
    #print("Logic rules\n", logic_sentences)
    min_rules = espresso_minimazer(logic_sentences)
    #print("Rules_minimization\n",min_rules)

    if defaul_action_and_horn_clauses:
        horn_rules= convert_to_horn_rules(min_rules, Actions, verbose = 0)
        #print("horn_rules\n",horn_rules)

        frequencies = compute_frequencies(horn_rules)
        rules_point = compute_rules_points(horn_rules, frequencies)
        #print(rules_point)
        ordered_rules = order_the_rules(horn_rules, rules_point)
        #print(ordered_rules)
        logic_rules, actions_in_order = convert_rule_into_logic(ordered_rules, 0)
        #print("logic_horn_rules\n",logic_rules)
        #print("actions_in_order",actions_in_order)
    else:
        logic_rules, actions_in_order = convert_rule_into_logic(min_rules, 0)
        #print("logic_horn_rules\n",logic_rules)
        #print("actions_in_order",actions_in_order)
    alg_horn_rules= convert_logic_rules_into_algebraic_expression(logic_rules , 0)
    min_rules_alg = []
    for i, rule in enumerate(alg_horn_rules):
        rule = rule.replace("(", "").replace(")","").replace("~VAR", "var")
        alg_horn_rules[i] = alg_horn_rules[i].replace("~VAR", "var")
        rule = sympify(rule, locals=v_dict)
        rule_factor = gfactor(rule, verbose = 0)
        rule_factor = str(rule_factor)

        min_rules_alg.append(rule_factor)

    bt = min_rules_alg_to_BT(min_rules_alg, alg_horn_rules, actions_in_order, 0)
    print("\nFINAL BT with my method\n\n", bt)


    #save as a dot file
    bt = bt.replace(' \n', '').replace("[", "").replace(", ]", "").replace("'", "").replace(", ", ",").split(",")
    print(bt)
    if defaul_action_and_horn_clauses:     
        BT_path = "BT-Factor"
        if not os.path.exists(BT_path):
            os.makedirs(BT_path)
    else:
        BT_path = "BT-Factor-DNF"
        if not os.path.exists(BT_path):
            os.makedirs(BT_path)

    environment = notebook_interface.Environment(seed=0, verbose=False)
    environment.plot_individual(BT_path, 'behavior_tree', bt)
    



if __name__ == '__main__':
    main()
