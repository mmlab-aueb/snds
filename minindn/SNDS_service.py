from ndn.encoding   import Name, InterestParam, FormalName, BinaryStr
from ndn.app        import NDNApp
from ndn.types      import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node   import Host
from typing         import Optional

import random 
import json
import sys
import subprocess

app = NDNApp()

OBJECT = sys.argv[1]
TYPE = sys.argv[2]

subprocess.run(["nlsrc", "advertise", "/snds/{}".format(OBJECT)])

@app.route('/snds/{}'.format(OBJECT))
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    print(f"Received Interest: {Name.to_str(name)}")
    
    with open("{}.jsonld".format(OBJECT), "r") as json_file:
        json_content = json.load(json_file)

    app.put_data(name, content=json.dumps(json_content).encode(), freshness_period=10000)

    print(f"Data sent: {Name.to_str(name)}")


async def main():
    try:
        nonce = str(random.randint(0,100000000))

        data_name, meta_info, content = await app.express_interest (
            '/snds/{}/{}'.format(TYPE, nonce),
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )
        print(f"Received Data Name: {Name.to_str(data_name)}")
        #print(meta_info)
        print(bytes(content) if content else None)

        riD = str(int.from_bytes(content, 'big'))
        #print(riD)

        subprocess.run(["nlsrc", "advertise", "/snds/{}".format(riD)])

        @app.route('/snds/' + riD)
        def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
            print(f"Received Interest: {Name.to_str(name)}")

            with open("{}.jsonld".format(OBJECT), "r") as json_file:
                json_content = json.load(json_file)

            app.put_data(name, content=json.dumps(json_content).encode(), freshness_period=10000)

            print(f"Data sent: {Name.to_str(name)}")

    except InterestNack as e:
        print(f'Nacked with reason={e.reason}')
    except InterestTimeout:
        print(f'Timeout')
    except InterestCanceled:
        print(f'Canceled')
    except ValidationFailure:
        print(f'Data failed to validate')

if __name__ == '__main__':
    app.run_forever(after_start=main())