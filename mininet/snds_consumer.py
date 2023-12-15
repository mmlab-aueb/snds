from ndn.encoding   import  Name, InterestParam, FormalName, BinaryStr
from ndn.app        import  NDNApp
from ndn.types      import  InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node   import  Host
from typing         import  Optional

import random

app = NDNApp()

@app.route('/snds/Car1')
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    print("Received Interest!!!")
    app.put_data(name, content=b'Car1', freshness_period = 10000)
    print(f"Data sent: {Name.to_str(name)}")

async def main():
    try:
        nonce = str(random.randint(0, 100000000))

        data_name, meta_info, content = await app.express_interest(
            #Interest name
            '/snds/CAR/{}'.format(nonce), 
            must_be_fresh=True, 
            can_be_prefix=False, 
            #Interest lifetime in ms
            lifetime=6000
        )

        print(f'Received Data Name: {Name.to_str(data_name)}')
        print(meta_info)
        print(bytes(content) if content else None)
        riD = str(int.from_bytes(content, 'big'))
        print(riD)

        #Create the routes
        producer = Host('producer')
        producer.cmd('export HOME=/tmp/mininet/producer')
        producer.cmd('nfdc route add /snds/{} udp://10.0.0.2'.format(riD))

        forwarder = Host('forwarder')
        forwarder.cmd('export HOME=/tmp/mininet/forwarder')
        forwarder.cmd('nfdc route add /snds/{} udp://10.0.0.3'.format(riD))

        @app.route('/snds/' + riD)
        def on_interest1(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
            print("Received Interest!!!")
            app.put_data(name, content=riD.encode(), freshness_period = 10000)
            print(f"Data sent: {Name.to_str(name)}")

    except InterestNack as e:
        #A Nack is received 
        print(f'Nacked with reason={e.reason}')
    except InterestTimeout:
        #Interest times out
        print(f'Timeout')
    except InterestCanceled:
        #Connection to NFD is broken
        print(f'Canceled')
    except ValidationFailure:
        #Validation Failure
        print(f'Data failed to validate')
    #finally:
        #app.shutdown()

if __name__ == '__main__':
    app.run_forever(after_start=main())
    #app.run_forever()