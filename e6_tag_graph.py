
from graphviz import Digraph
import requests

headers = {'user-agent': 'Fifteen\'s Tag Tree Grapher/0.0.0'}

def get_aliases_for_tag(tagname):
    r = requests.get('https://e621.net/tag_alias/index.json', params={'aliased_to':tagname}, headers=headers)
    return r.json()

"""
def get_implications_for_tag(tagname):
    requests.get('https://e621.net/tag_implication/index.json', params={'implied_to':tagname})
"""

g = Digraph('G', filename='cluster.gv')

alias_data = get_aliases_for_tag('mammal')

with g.subgraph(name='cluster_0') as c:
    c.attr(style='filled')

    c.node_attr.update(style='filled', color='lightgrey')

    c.node('mammal', style='filled', color="white")
    
    for aliased_tag in alias_data:
        c.edge(aliased_tag['name'], 'mammal', style='invis')

g.view()
