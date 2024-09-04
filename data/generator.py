from utils import merenje
from cpp_module import *
#import time
import pickle
from data.parse_files import load_comments, load_statuses

#from simplejson import dumps
#from memory_profiler import profile

#@profile
def load_and_create_data():
    '''returns affinity_graph, popularity_map, statuses'''
    comments = load_comments("data/dataset/original_comments.csv")
    statuses = load_statuses("data/dataset/original_statuses.csv")
    graph = generate_affinity_graph(comments, statuses, "data/dataset/original_shares.csv", "data/dataset/original_reactions.csv", "data/dataset/friends.csv", {})
    map = generate_popularity_map(statuses, {})
    statuses_dict = {status[0]: (status[1], status[4], status[5], status[7], status[8], status[9], status[10], status[11], status[12], status[13], status[14]) for status in statuses}
    return graph, map, statuses_dict

def add_test_data(old_graph, old_map, old_statuses_dict):
    '''returns affinity_graph, popularity_map, statuses'''
    comments = load_comments("data/dataset/test_comments.csv")
    statuses = load_statuses("data/dataset/test_statuses.csv")
    graph = generate_affinity_graph(comments, statuses, "data/dataset/test_shares.csv", "data/dataset/test_reactions.csv", "", old_graph)
    map = generate_popularity_map(statuses, old_map)
    statuses_dict = {status[0]: (status[1], status[4], status[5], status[7], status[8], status[9], status[10], status[11], status[12], status[13], status[14]) for status in statuses}
    old_statuses_dict.update(statuses_dict)
    return graph, map, old_statuses_dict

def load_premade(): 
    '''returns affinity_graph, popularity_map, statuses'''
    try:
        with open('graph.pickle', 'rb') as handle:
            graph = pickle.load(handle)
        with open('map.pickle', 'rb') as handle:
            map = pickle.load(handle)
        with open('statuses.pickle', 'rb') as handle:
            statuses = pickle.load(handle)
    except FileNotFoundError as e:
        raise e
    return graph, map, statuses

def save_data(graph, map, statuses):
    with open('graph.pickle', 'wb') as handle:
        pickle.dump(graph, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('map.pickle', 'wb') as handle:
        pickle.dump(map, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('statuses.pickle', 'wb') as handle:
        pickle.dump(statuses, handle, protocol=pickle.HIGHEST_PROTOCOL)
