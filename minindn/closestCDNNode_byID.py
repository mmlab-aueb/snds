from ndn.encoding   import Name, InterestParam, FormalName, BinaryStr
from ndn.app        import NDNApp
from ndn.types      import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node   import Host
from typing         import Optional

import sys 
import json

app = NDNApp()

async def main():
    try:
        id = sys.argv[1]

        data_name, meta_info, content = await app.express_interest (
            '/snds/{}'.format(id),
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )

        print(f"Received Data Name: {Name.to_str(data_name)}")
        
        #print(meta_info)
        data = bytes(content)
        json_data = json.loads(data.decode())
        print(json_data)

        json_ld_name = "{}.jsonld".format(id)

        with open(json_ld_name, "w") as json_ld:
            json.dump(json_data, json_ld, indent=2)

    except InterestNack as e:
        print(f'Nacked with reason={e.reason}')
    except InterestTimeout:
        print(f'Timeout')
    except InterestCanceled:
        print(f'Canceled')
    except ValidationFailure:
        print(f'Data failed to validate')
    finally:
        app.shutdown()

if __name__ == '__main__':
    app.run_forever(after_start=main())