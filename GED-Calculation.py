import re
import networkx as nx
import copy
import pydot
import os

SEQUENCE = "Sequence"
FALLBACK = "Fallback"
PARALLEL = "Parallel"
ACTION = "Action"
CONDITION = "Condition"
RE_NOTHINGORWHITESPACESTART = "(?<!\S)"
RE_NOTHINGORWHITESPACEEND = "(?!\S)"
RE_ANY = "*"

# hard coded 
regex_dict = {
    # must be before Sequence
    RE_NOTHINGORWHITESPACESTART + SEQUENCE + RE_ANY: SEQUENCE,
    # must be before || and Selector
    RE_NOTHINGORWHITESPACESTART + FALLBACK + RE_ANY: FALLBACK,
    RE_NOTHINGORWHITESPACESTART + PARALLEL + RE_ANY: PARALLEL,
    RE_NOTHINGORWHITESPACESTART + "action" + RE_ANY : ACTION,
    "*": CONDITION,  # catch all, needs to stay in this order as conditions do not have a good identifier
}

def find_graph_sim(generated_graph, sim_graph):
    gen_root = get_root_node(generated_graph)
    sim_root = get_root_node(sim_graph)

    gen_subtrees = [get_subtree_graph(
        generated_graph, edges[1]) for edges in generated_graph.out_edges(gen_root)]
    sim_subtrees = [get_subtree_graph(sim_graph, edges[1])
                    for edges in sim_graph.out_edges(sim_root)]

    max_iters = 1  # tunable, possibly look at timeouts

    add_label_to_gen_trees(gen_subtrees)
    add_label_to_gen_trees(sim_subtrees)
    final_score_list = []
    for i, sim_tree in enumerate(sim_subtrees):
        min_score_list = []
        gen_min_edit_distance_for_all_subtrees(sim_tree, gen_subtrees, max_iters, min_score_list)

        final_score_list.append({
            "sim_tree_num": i,
            "num_nodes_in_subtree": total_num_nodes(sim_tree),
            "score": min_score_list[-1] if len(min_score_list) > 0 else -1
        }
        )
    return final_score_list

def num_unique_nodes(graph):
    return sum(x > 0 for x in get_freq_unique_node_dict(graph).values())


def total_num_nodes(graph):
    return len(graph.nodes)


def get_root_node(graph):
    return [n for n, d in graph.in_degree() if d == 0][0]


def get_num_subtrees_from_root(graph):
    return len(graph.edges(get_root_node(graph)))


def get_subtree_graph(graph, sub_tree_node):
    return copy.deepcopy(nx.bfs_tree(graph, source=sub_tree_node, reverse=False))


def add_label_to_gen_trees(gen_subtrees):
    for tree in gen_subtrees:
        name_dict = dict(zip(tree.nodes, tree.nodes))
        nx.set_node_attributes(tree, name_dict, 'label')

# removes all everything except[alphanumeric, '|']
pattern = re.compile('[^A-Za-z0-9\|]+')

def custom_node_match(gen_node, sim_node):
    return pattern.sub("", sim_node['label']) in gen_node['label']        


def gen_min_edit_distance_for_all_subtrees(sim_graph, gen_subtrees, max_iters, min_score_list):
    min_score = None
    for j, g_tree in enumerate(gen_subtrees):
        i = 0
        for score in nx.optimize_graph_edit_distance(g_tree, sim_graph, node_match=custom_node_match, upper_bound=30):
            if min_score == None or score < min_score:
                min_score = score
                min_score_list.append(min_score)
            i += 1
            if i == max_iters:
                break
    return min_score

def get_node_regex_dict():
    return regex_dict


def unique_node_set():
    return get_node_regex_dict().values()


def unique_node_freq_counter():
    return dict.fromkeys(unique_node_set(), 0)

def get_freq_unique_node_dict(graph):
    freq_dict = unique_node_freq_counter()
    node_regex = get_node_regex_dict()
    nodes_number = len(graph.nodes)
    for i, node in enumerate(graph.nodes):
        if i== nodes_number-1:
            break
        if "!" in node:
            node ="action"
        for reg_pat, node_type in node_regex.items():
            if reg_pat == "*" or re.search(reg_pat, node):
                freq_dict[node_type] += 1
                break  # go to next node
    return freq_dict

path_to_tree_dot_file_input =  "BT-input/behavior_tree.dot"
path_to_tree_dot_file_bt_factor =  "BTFactor/behavior_tree.dot"
path_to_tree_dot_file_re_bt =  "REBTEspresso/behavior_tree.dot"
path_to_tree_dot_file_bt_factor_dnf =  "BTFactor_DNF/behavior_tree.dot"

G_input = nx.nx_pydot.from_pydot(
        pydot.graph_from_dot_file(path_to_tree_dot_file_input)[0])
G_bt_factor = nx.nx_pydot.from_pydot(
        pydot.graph_from_dot_file(path_to_tree_dot_file_bt_factor)[0])
G_re_bt = nx.nx_pydot.from_pydot(
        pydot.graph_from_dot_file(path_to_tree_dot_file_re_bt)[0])
G_bt_factor_dnf = nx.nx_pydot.from_pydot(
        pydot.graph_from_dot_file(path_to_tree_dot_file_bt_factor_dnf)[0])

print("Starting..")
properties_input_graph = get_freq_unique_node_dict(G_input)

print("Running BT factor")
properties_G_bt_factor = get_freq_unique_node_dict(G_bt_factor)
final_score_bt_factor = find_graph_sim(G_bt_factor,G_input)

properties_G_bt_factor_dnf = get_freq_unique_node_dict(G_bt_factor_dnf)
final_score_bt_factor_dnf = find_graph_sim(G_bt_factor_dnf,G_input)


print("Running RE BT")
properties_G_re_bt=get_freq_unique_node_dict(G_re_bt)
final_score_re_bt = find_graph_sim(G_re_bt,G_input)


result_path = "results" 
if not os.path.exists(result_path):
    os.makedirs(result_path)
output = open(result_path + "/GED.txt","w+")

output.write("Input graph:\n")
output.write("Number of nodes: %d\r" % (len(list(G_input.nodes))-1))
output.write(str(properties_input_graph))

output.write("\n\n\nRE-BT graph:\n")
output.write("Number of nodes: %d\r" % (len(list(G_re_bt.nodes))-1))
output.write(str(properties_G_re_bt))
output.write("\nFinal score list with re-bt-espresso:\n")
output.write(str(final_score_re_bt))


output.write("\n\n\nBT Factor:\n")
output.write("Number of nodes: %d\r" % (len(list(G_bt_factor.nodes))-1))
output.write(str(properties_G_bt_factor))
output.write("\nFinal score list with BT factor:\n")
output.write(str(final_score_bt_factor))
output.write("\n\n..only dnf:\n")
output.write("Number of nodes: %d\r" % len(list(G_bt_factor_dnf.nodes)))
output.write(str(properties_G_bt_factor_dnf))
output.write("\nFinal score list with BT factor DNF:\n")
output.write(str(final_score_bt_factor_dnf))

output.close()


