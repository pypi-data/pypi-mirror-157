from collections import defaultdict
from typing import Dict, List, Set
import json
import os
import socket
import contextlib

import pymongo
from pymongo import MongoClient
import re

from lightning.classes import Node, Channel

CHANNELS_DIR = 'C:/temp/' if os.name == 'nt' else \
        '/home/saart/Downloads/' if socket.gethostname() == 'ubuntu' else \
        '/cs/labs/avivz/saart/lightning_ddos/dr/'
CHANNELS_PATH = CHANNELS_DIR + ('describegraph.json' if os.path.exists(CHANNELS_DIR+'describegraph.json') else 'LN.json')

_nodes = None
_list_nodes = None
_db = None


def db():
    global _db
    if not _db:
        _db = MongoClient().best_paths.paths
    return _db


def load_from_disk(path=CHANNELS_PATH) -> Dict[str, Node]:
    global _nodes, _list_nodes
    if _nodes:
        return _nodes
    channels_json = json.load(open(path, 'rb'))
    nodes = {}
    if "edges" in channels_json:
        # lnd format
        for channel in channels_json['edges']:
            # if re.match('.*[^abc]$', channel['node1_pub']) or re.match('.*[^abc]$', channel['node2_pub']):
            #     continue
            if not channel["node1_policy"] and not channel["node2_policy"]:
                continue
            if channel['node1_pub'] not in nodes: nodes[channel['node1_pub']] = Node(name=channel['node1_pub'])
            if channel['node2_pub'] not in nodes: nodes[channel['node2_pub']] = Node(name=channel['node2_pub'])
            if channel["node1_policy"]:
                Channel.create_channel(node1=nodes[channel['node1_pub']],
                                       node2=nodes[channel['node2_pub']],
                                       base_fee=int(channel["node1_policy"]['fee_base_msat']),
                                       proportional_fee=int(channel["node1_policy"]['fee_rate_milli_msat']) / 1000.,
                                       delay=int(channel["node1_policy"]['time_lock_delta']),
                                       capacity=int(channel['capacity']),
                                       height=int(channel['channel_id']) >> 40,
                                       scid=channel['channel_id'].encode())
            if channel["node2_policy"]:
                Channel.create_channel(node1=nodes[channel['node1_pub']],
                                       node2=nodes[channel['node2_pub']],
                                       base_fee=int(channel["node2_policy"]['fee_base_msat']),
                                       proportional_fee=int(channel["node2_policy"]['fee_rate_milli_msat']) / 1000.,
                                       delay=int(channel["node2_policy"]['time_lock_delta']),
                                       capacity=int(channel['capacity']),
                                       height=int(channel['channel_id']) >> 40,
                                       scid=channel['channel_id'].encode())
    else:
        # old format
        print('Using the old json data')
        for channel in channels_json['channels']:
            # if re.match('.*[^abc]$', channel['source']) or re.match('.*[^abc]$', channel['destination']):
            #     continue
            if channel['source'] not in nodes: nodes[channel['source']] = Node(name=channel['source'])
            if channel['destination'] not in nodes: nodes[channel['destination']] = Node(name=channel['destination'])
            Channel.create_channel(node1=nodes[channel['source']],
                                   node2=nodes[channel['destination']],
                                   base_fee=channel['base_fee_millisatoshi'],
                                   proportional_fee=channel['fee_per_millionth'] / 1000.,
                                   delay=channel['delay'],
                                   capacity=channel['satoshis'],
                                   height=int(channel['short_channel_id'].split(':')[0]),
                                   scid=channel['short_channel_id'].encode())
    _nodes = nodes
    _list_nodes = list(nodes.values())
    print('number of nodes:', len(_list_nodes))
    return nodes


def load_list_from_disk(path=CHANNELS_PATH) -> List[Node]:
    global _list_nodes
    if not _list_nodes:
        load_from_disk(path)
    return _list_nodes


def get_channels() -> Set[Channel]:
    nodes = load_list_from_disk()
    channels = set()
    for n in nodes:
        channels.update(n.channels)
    return channels


def mongo_indexes():
    db().create_index([('src', pymongo.ASCENDING), ('dst', pymongo.ASCENDING), ('transaction_size', pymongo.ASCENDING)])
    db().create_index([('src', pymongo.ASCENDING), ('transaction_size', pymongo.ASCENDING)])
    db().create_index([('dst', pymongo.ASCENDING), ('transaction_size', pymongo.ASCENDING)])
    db().create_index([('src', pymongo.ASCENDING)])
    db().create_index([('dst', pymongo.ASCENDING)])
    keys = ['lnd', 'eclair_*', 'c_no_fuzz', 'suggested_no_fuzz', 'aviv_suggested'] + [f'c{i}' for i in range(5)] + [f'suggested{i}' for i in range(5)] + [f'eclair_{i}' for i in range(3)]
    for key in keys:
        db().create_index([(f'{key}.path', pymongo.ASCENDING)])
        db().create_index([(f'{key}.length', pymongo.ASCENDING)])


def plot_dict(d, plot_type='plot', truncate_highests=True, width_mul=30, min_bin_size=0.058, highest_multiplyer=1.9, bin_size=None):
    """
    This function plot the given dict.

    If `truncate_highests` is set to true (default), we will put all the highest results in a single bin,
        until the value of the bin reaches the value 0.1, and adjust the x-labels.
    """
    from matplotlib import pyplot
    sorted_keys = sorted(d.keys())
    sorted_values = [d[k] for k in sorted_keys]
    bin_size = bin_size or width_mul

    if not truncate_highests:
        getattr(pyplot, plot_type)(sorted_keys, sorted_values)
        pyplot.show()
        return

    highest = 0
    for i in range(len(sorted_values) - 1, 0, -1):
        if sum(sorted_values[i:]) >= min_bin_size:
            highest = sorted_keys[i] * highest_multiplyer
            sorted_keys = sorted_keys[:i + 1] + [highest]
            sorted_values = sorted_values[:i + 1] + [sum(sorted_values[i + 1:])]
            break
    if plot_type == 'plot':
        ax, = pyplot.plot(sorted_keys, sorted_values)
        labels = [x for x in ax.axes.get_xticks() if 0 <= x < highest]
        pyplot.xticks(labels + ([highest] if min_bin_size else []), labels + (['more'] if min_bin_size else []))
    else:
        cells = defaultdict(lambda: 0)
        for i, (k, v) in enumerate(zip(sorted_keys, sorted_values)):
            cells[(k // bin_size) * bin_size] += v
        pyplot.bar(list(cells.keys()), list(cells.values()), width=highest / width_mul)
        # pyplot.bar(sorted_keys, sorted_values, width=highest / width_mul)
        labels = [x.round(2) for x in pyplot.axes().get_xticks() if 0 <= x < highest]
        pyplot.xticks(labels + ([highest] if min_bin_size else []), labels + (['more'] if min_bin_size else []))

    pyplot.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in pyplot.gca().get_yticks()])


@contextlib.contextmanager
def profiler():
    import cProfile, pstats, io

    pr = cProfile.Profile()
    pr.enable()

    try:
        yield
    finally:
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
        ps.print_stats()
        print(s.getvalue())


if __name__ == '__main__':
    mongo_indexes()
