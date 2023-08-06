def is_valid_json_rpc(data):
    return (
        all(map(lambda key: key in data.keys(), ["jsonrpc", "id"])) if data else False
    )
