from ndn.encoding   import Name, InterestParam, FormalName, BinaryStr
from ndn.app        import NDNApp
from ndn.types      import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node   import Host
from typing         import Optional

import random 
import json

app = NDNApp()

snds_service = Host('consumer')
snds_service.cmd('nlsrc advertise /snds/Car1')

@app.route('/snds/Car1')
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    print(f"Received Interest: {Name.to_str(name)}")

    with open("car1.jsonld", "r") as json_file:
        json_content = json.load(json_file)

    app.put_data(name, content=json.dumps(json_content).encode(), freshness_period=10000)

    print(f"Data sent: {Name.to_str(name)}")


async def main():
    try:
        nonce = str(random.randint(0,100000000))

        data_name, meta_info, content = await app.express_interest (
            '/snds/CAR/{}'.format(nonce),
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )
        print(f"Received Data Name: {Name.to_str(data_name)}")
        #print(meta_info)
        print(bytes(content) if content else None)

        riD = str(int.from_bytes(content, 'big'))
        #print(riD)

        snds_service.cmd('nlsrc advertise /snds/' + riD)

        @app.route('/snds/' + riD)
        def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
            print(f"Received Interest: {Name.to_str(name)}")

            with open("car1.jsonld", "r") as json_file:
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