import json

import find_neighborhood


def handle_request(request):
    address = request.args.get("address", "")
    data = find_neighborhood.db.find(address)
    return json.dumps(data)
