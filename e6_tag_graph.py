
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


tags_to_explore = ['mammal']

current_tag = tags_to_explore.pop()

implication_data = [{'id': 12831, 'consequent_id': 12054, 'predicate_id': 633522, 'pending': True, 'name': 'afrosoricid'}, {'id': 10128, 'consequent_id': 12054, 'predicate_id': 486038, 'pending': True, 'name': 'elephantidae'}, {'id': 10572, 'consequent_id': 12054, 'predicate_id': 14751, 'pending': True, 'name': 'shrew'}, {'id': 5036, 'consequent_id': 12054, 'predicate_id': 6103, 'pending': False, 'name': 'aardvark'}, {'id': 5035, 'consequent_id': 12054, 'predicate_id': 11504, 'pending': False, 'name': 'anteater'}, {'id': 3370, 'consequent_id': 12054, 'predicate_id': 3391, 'pending': False, 'name': 'antelope'}, {'id': 3307, 'consequent_id': 12054, 'predicate_id': 3487, 'pending': False, 'name': 'armadillo'}, {'id': 2808, 'consequent_id': 12054, 'predicate_id': 830, 'pending': False, 'name': 'bat'}, {'id': 2899, 'consequent_id': 12054, 'predicate_id': 265, 'pending': False, 'name': 'bear'}, {'id': 2738, 'consequent_id': 12054, 'predicate_id': 18297, 'pending': False, 'name': 'bovine'}, {'id': 4346, 'consequent_id': 12054, 'predicate_id': 39306, 'pending': False, 'name': 'camelid'}, {'id': 2645, 'consequent_id': 12054, 'predicate_id': 1068, 'pending': False, 'name': 'canine'}, {'id': 2904, 'consequent_id': 12054, 'predicate_id': 64042, 'pending': False, 'name': 'caprine'}, {'id': 2830, 'consequent_id': 12054, 'predicate_id': 3695, 'pending': False, 'name': 'cervine'}, {'id': 2860, 'consequent_id': 12054, 'predicate_id': 20050, 'pending': False, 'name': 'cetacean'}, {'id': 3189, 'consequent_id': 12054, 'predicate_id': 1258, 'pending': False, 'name': 'elephant'}, {'id': 2648, 'consequent_id': 12054, 'predicate_id': 3085, 'pending': False, 'name': 'equine'}, {'id': 12572, 'consequent_id': 12054, 'predicate_id': 618952, 'pending': False, 'name': 'euplerid'}, {'id': 2647, 'consequent_id': 12054, 'predicate_id': 180, 'pending': False, 'name': 'feline'}, {'id': 3227, 'consequent_id': 12054, 'predicate_id': 462, 'pending': False, 'name': 'giraffe'}, {'id': 12530, 'consequent_id': 12054, 'predicate_id': 503284, 'pending': False, 'name': 'giraffid'}, {'id': 7113, 'consequent_id': 12054, 'predicate_id': 9109, 'pending': False, 'name': 'gnoll'}, {'id': 2901, 'consequent_id': 12054, 'predicate_id': 1985, 'pending': False, 'name': 'hedgehog'}, {'id': 12058, 'consequent_id': 12054, 'predicate_id': 181786, 'pending': False, 'name': 'herpestid'}, {'id': 4595, 'consequent_id': 12054, 'predicate_id': 140257, 'pending': False, 'name': 'hippopotamus'}, {'id': 2898, 'consequent_id': 12054, 'predicate_id': 411, 'pending': False, 'name': 'human'}, {'id': 2905, 'consequent_id': 12054, 'predicate_id': 490, 'pending': False, 'name': 'hyena'}, {'id': 2646, 'consequent_id': 12054, 'predicate_id': 17459, 'pending': False, 'name': 'lagomorph'}, {'id': 5032, 'consequent_id': 12054, 'predicate_id': 114540, 'pending': False, 'name': 'manatee'}, {'id': 2903, 'consequent_id': 12054, 'predicate_id': 3112, 'pending': False, 'name': 'marsupial'}, {'id': 12520, 'consequent_id': 12054, 'predicate_id': 618306, 'pending': False, 'name': 'mephitid'}, {'id': 4010, 'consequent_id': 12054, 'predicate_id': 9859, 'pending': False, 'name': 'mole'}, {'id': 4349, 'consequent_id': 12054, 'predicate_id': 5557, 'pending': False, 'name': 'monotreme'}, {'id': 2900, 'consequent_id': 12054, 'predicate_id': 4993, 'pending': False, 'name': 'mustelid'}, {'id': 4966, 'consequent_id': 12054, 'predicate_id': 162470, 'pending': False, 'name': 'nimbat'}, {'id': 4515, 'consequent_id': 12054, 'predicate_id': 11180, 'pending': False, 'name': 'okapi'}, {'id': 5034, 'consequent_id': 12054, 'predicate_id': 316, 'pending': False, 'name': 'pangolin'}, {'id': 7529, 'consequent_id': 12054, 'predicate_id': 167452, 'pending': False, 'name': 'pinniped'}, {'id': 2907, 'consequent_id': 12054, 'predicate_id': 64397, 'pending': False, 'name': 'porcine'}, {'id': 2906, 'consequent_id': 12054, 'predicate_id': 21794, 'pending': False, 'name': 'primate'}, {'id': 12529, 'consequent_id': 12054, 'predicate_id': 602261, 'pending': False, 'name': 'proboscidean'}, {'id': 12067, 'consequent_id': 12054, 'predicate_id': 167951, 'pending': False, 'name': 'procyonid'}, {'id': 6367, 'consequent_id': 12054, 'predicate_id': 65815, 'pending': False, 'name': 'pronghorn'}, {'id': 2908, 'consequent_id': 12054, 'predicate_id': 919, 'pending': False, 'name': 'red_panda'}, {'id': 3206, 'consequent_id': 12054, 'predicate_id': 66300, 'pending': False, 'name': 'rhinoceros'}, {'id': 2818, 'consequent_id': 12054, 'predicate_id': 3661, 'pending': False, 'name': 'rodent'}, {'id': 4960, 'consequent_id': 12054, 'predicate_id': 4668, 'pending': False, 'name': 'sloth'}, {'id': 4225, 'consequent_id': 12054, 'predicate_id': 3178, 'pending': False, 'name': 'tanuki'}, {'id': 4670, 'consequent_id': 12054, 'predicate_id': 4127, 'pending': False, 'name': 'tapir'}, {'id': 5037, 'consequent_id': 12054, 'predicate_id': 153348, 'pending': False, 'name': 'viverrid'}]

g = Digraph('G', filename='cluster.gv')

for tag in implication_data:
    tags_to_explore.append(tag['name'])

    alias_data = get_aliases_for_tag(tag['name'])

    with g.subgraph(name='cluster_{}'.format(tag['name'])) as c:
        c.attr(style='filled')

        c.node_attr.update(style='filled', color='lightgrey')

        c.node(tag['name'], style='filled', color="white")
        
        for aliased_tag in alias_data:
            c.edge(aliased_tag['name'], tag['name'], style='invis')

    g.edge(tag['name'], current_tag)

g.view()
