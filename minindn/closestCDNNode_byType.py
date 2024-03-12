from ndn.encoding   import Name, InterestParam, FormalName, BinaryStr
from ndn.app        import NDNApp
from ndn.types      import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node   import Host
from typing         import Optional

import sys 
import json

app = NDNApp()

async def express_interest(interest_name):
    try:
        data_name, meta_info, content = await app.express_interest (
            interest_name,
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )
        return data_name, meta_info, content
    except InterestNack as e:
        print(f'Nacked with reason={e.reason}')
    except InterestTimeout:
        print(f'Timeout')
    except InterestCanceled:
        print(f'Canceled')
    except ValidationFailure:
        print(f'Data failed to validate')

async def run():
    requested_type = sys.argv[1]
    interest_name = '/snds/{}_registry'.format(requested_type)
    #print('interest name ' + interest_name )
    data_name, meta_info, content = await express_interest(interest_name)

    print(f"Received Data Name: {Name.to_str(data_name)}")
    #print(meta_info)
    rIDs = list(content)
    #print(rIDs)

    interest_name = '/snds/{}'.format(rIDs[-1])
    #print('interest name ' + interest_name )

    data_name, meta_info, content = await express_interest(interest_name)

    print(f"Received Data Name: {Name.to_str(data_name)}")
    #print(meta_info)
    data = bytes(content)
    json_data = json.loads(data.decode())
    print(json_data)

    json_ld_name = "{}.jsonld".format(json_data["@id"].split(":")[-1])

    with open(json_ld_name, "w") as json_ld:
        json.dump(json_data, json_ld, indent=2)

    app.shutdown()

if __name__ == '__main__':
    app.run_forever(after_start=run())