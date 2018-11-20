
import sys
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

def get_aliases_for_tag(tagname):
    page_num = 1
    alias_data = []

    while True:
        partial_alias_data = get_aliases_page(tagname, page_num)
        
        if len(partial_alias_data) == 0:
            break
        
        alias_data.extend(partial_alias_data)
        page_num += 1
        
    tag_id = get_tag_id_by_name(tagname)
    alias_data = list(filter(lambda alias: alias['alias_id'] == tag_id, alias_data))

    return alias_data

@sleep_and_retry
@limits(calls=1, period=1)
def get_aliases_page(tagname, page):
    print("Aliases for {}, page {}".format(tagname, page))
    r = requests.get('https://e621.net/tag_alias/index.json', params={'aliased_to':tagname, 'page': page}, headers=headers)
    return r.json()

def get_implications_for_tag(tagname):
    page_num = 1
    impl_data = []

    while True:
        partial_impl_data = get_implications_page(tagname, page_num)
        if len(partial_impl_data) == 0:
            break
        
        impl_data.extend(partial_impl_data)
        page_num += 1

    tag_id = get_tag_id_by_name(tagname)
    impl_data = list(filter(lambda alias: alias['consequent_id'] == tag_id, impl_data))

    for nameless_tag in impl_data:
        nameless_tag['name'] = get_tag_name_by_id(nameless_tag['predicate_id'])

    return impl_data

@sleep_and_retry
@limits(calls=1, period=1)
def get_implications_page(tagname, page):
    print("Implications for {}, page {}".format(tagname, page))
    r = requests.get('https://e621.net/tag_implication/index.json', params={'implied_to':tagname, 'page': page}, headers=headers)
    return r.json()

@sleep_and_retry
@limits(calls=1, period=1)
def fetch_tag_data(tag_id=None, tagname=None):
    print("Tag data for {}".format(tagname) if tagname else "Tag data for #{}".format(tag_id))
    r = requests.get('https://e621.net/tag/show.json', params={'id':tag_id, 'name':tagname}, headers=headers)
    
    tag_data = r.json()
    tag_lookup_tbl.append(tag_data)
    return tag_data

def graph_tag_impl_chain(initial_tag:str):
    tags_to_explore = [initial_tag]

    g = Digraph(name=initial_tag, format='png', strict=True)

    while(len(tags_to_explore) != 0):
        current_tag = tags_to_explore.pop()

        implication_data = get_implications_for_tag(current_tag)

        for tag in implication_data:
            tags_to_explore.append(tag['name'])

            alias_data = get_aliases_for_tag(tag['name'])

            with g.subgraph(name='cluster_{}'.format(tag['name'])) as c:
                c.attr(style='filled')

                c.node_attr.update(style='solid,setlinewidth(0)')

                c.node(tag['name'], style='filled', color="white")
                
                for aliased_tag in alias_data:
                    alias_color = 'red' if aliased_tag['pending'] else 'black'
                    c.node(aliased_tag['name'], fontcolor=alias_color)
                    c.edge(aliased_tag['name'], tag['name'], style='invis')

            edge_style = 'dotted' if tag['pending'] else 'solid'
            g.edge(tag['name'], current_tag, style=edge_style)

    return g

if __name__ == "__main__":
    if len(sys.argv) == 2:
        initial_tag = sys.argv[1]
        print("Initial tag: {}".format(initial_tag))
        g = graph_tag_impl_chain(initial_tag)
        g.view()
    else:
        print("You must provide exactly one initial tag as argument")
        sys.exit(1)
