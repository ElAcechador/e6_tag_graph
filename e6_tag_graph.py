
from graphviz import Digraph
import requests
from ratelimit import limits, sleep_and_retry

headers = {'user-agent': 'Fifteen\'s Tag Tree Grapher/0.0.0'}

# Neither of those APIs guarantee exact name match or to->from direction

tag_lookup_tbl = []

def get_tag_id_by_name(tagname):
    try:
        lookup_result = next(el for el in tag_lookup_tbl if el['name'] == tagname)
        return lookup_result['id']
    except StopIteration:
        return fetch_tag_data(tagname=tagname)['id']        

def get_tag_name_by_id(tag_id):
    try:
        lookup_result = next(el for el in tag_lookup_tbl if el['id'] == tag_id)
        return lookup_result['name']
    except StopIteration:
        return fetch_tag_data(tag_id=tag_id)['name']

@sleep_and_retry
@limits(calls=1, period=1)
def get_aliases_for_tag(tagname):
    r = requests.get('https://e621.net/tag_alias/index.json', params={'aliased_to':tagname}, headers=headers)
    alias_data = r.json()

    tag_id = get_tag_id_by_name(tagname)
    print(tag_id)
    alias_data = list(filter(lambda alias: alias['alias_id'] == tag_id, alias_data))

    return alias_data

@sleep_and_retry
@limits(calls=1, period=1)
def get_implications_for_tag(tagname):
    r = requests.get('https://e621.net/tag_implication/index.json', params={'implied_to':tagname}, headers=headers)
    impl_data = r.json()

    tag_id = get_tag_id_by_name(tagname)
    print(tag_id)
    impl_data = list(filter(lambda alias: alias['consequent_id'] == tag_id, impl_data))

    for nameless_tag in impl_data:
        nameless_tag['name'] = get_tag_name_by_id(nameless_tag['predicate_id'])

    return impl_data

@sleep_and_retry
@limits(calls=1, period=1)
def fetch_tag_data(tag_id=None, tagname=None):
    r = requests.get('https://e621.net/tag/show.json', params={'id':tag_id, 'name':tagname}, headers=headers)
    
    tag_data = r.json()
    tag_lookup_tbl.append(tag_data)
    return tag_data


g = Digraph('G', filename='cluster.gv')

tags_to_explore = ['mammal']

current_tag = tags_to_explore.pop()

print(get_implications_for_tag(current_tag))

"""
implication_data = get_implications_for_tag(current_tag)

for tag in implication_data:
    tags_to_explore.append(tag['name'])

    alias_data = get_aliases_for_tag(tag['name'])

    with g.subgraph(name='cluster_{}'.format(tag['name'])) as c:
        c.attr(style='filled')

        c.node_attr.update(style='filled', color='lightgrey')

        c.node(tag['name'], style='filled', color="white")
        
        for aliased_tag in alias_data:
            c.edge(aliased_tag['name'], tag['name'], style='invis')

    g.edge(tag['name'], current_tag['name'])

"""

"""
alias_data = get_aliases_for_tag(current_tag)

with g.subgraph(name='cluster_{}'.format(current_tag)) as c:
    c.attr(style='filled')

    c.node_attr.update(style='filled', color='lightgrey')

    c.node('mammal', style='filled', color="white")
    
    for aliased_tag in alias_data:
        c.edge(aliased_tag['name'], 'mammal', style='invis')

g.view()
"""