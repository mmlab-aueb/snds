from ndn.encoding   import  Name, InterestParam, FormalName, BinaryStr
from ndn.app        import  NDNApp
from ndn.types      import  InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node   import  Host
from typing         import  Optional

import struct

app = NDNApp()

async def main():
    host = Host('closest')
    host.cmd('export HOME=/tmp/mininet/closest')
    host.cmd('nfdc route add /snds/CAR_registry udp://10.0.0.2')

    try:
        data_name, meta_info, content = await app.express_interest(
            #Interest name
            '/snds/CAR_registry', 
            must_be_fresh=True, 
            can_be_prefix=False, 
            #Interest lifetime in ms
            lifetime=6000
        )

        print(f'Received Data Name: {Name.to_str(data_name)}')
        print(meta_info)
        rIDs = list(content)
        print(rIDs)
        
        host.cmd('nfdc route add /snds/{} udp://10.0.0.2'.format(rIDs[-1]))

        try:
            data_name, meta_info, content = await app.express_interest(
                #Interest name
                '/snds/{}'.format(rIDs[-1]), 
                must_be_fresh=True, 
                can_be_prefix=False, 
                #Interest lifetime in ms
                lifetime=6000
            )

            print(f'Received Data Name: {Name.to_str(data_name)}')
            print(meta_info)
            print(bytes(content) if content else None)

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
    finally:
        app.shutdown()
        
    

if __name__ == '__main__':
    app.run_forever(after_start=main())