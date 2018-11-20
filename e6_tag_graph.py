
from graphviz import Digraph
import requests
from ratelimit import limits, sleep_and_retry

headers = {'user-agent': 'Fifteen\'s Tag Tree Grapher/0.0.0'}

@sleep_and_retry
@limits(calls=1, period=1)
def get_aliases_for_tag(tagname):
    r = requests.get('https://e621.net/tag_alias/index.json', params={'aliased_to':tagname}, headers=headers)
    return r.json()

@sleep_and_retry
@limits(calls=1, period=1)
def get_implications_for_tag(tagname):
    r = requests.get('https://e621.net/tag_implication/index.json', params={'implied_to':tagname}, headers=headers)
    alias_data = r.json()

    print("Fetching tag names for {}'s {} children".format(tagname, len(alias_data)))

    for nameless_tag in alias_data:
        nameless_tag['name'] = get_tag_name_by_id(nameless_tag['predicate_id'])

    return alias_data

@sleep_and_retry
@limits(calls=1, period=1)
def get_tag_name_by_id(tag_id):
    # Because the tag name isn't part of the implication API for reasons
    r = requests.get('https://e621.net/tag/show.json', params={'id':tag_id}, headers=headers)
    return r.json()['name']

print(get_implications_for_tag('vore'))

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
"""