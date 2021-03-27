from web3.datastructures import AttributeDict


def flatten_tx_pool(queue_dict: AttributeDict):
    d = {}
    for i in queue_dict.items():
        k, v = i
        f = list(v.values()).pop()
        d[k] = f
    return d
