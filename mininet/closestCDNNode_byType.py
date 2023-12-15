from ndn.encoding   import  Name, InterestParam, FormalName, BinaryStr
from ndn.app        import  NDNApp
from ndn.types      import  InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node   import  Host

app = NDNApp()

async def express_interest(interest_name):
    try:
        data_name, meta_info, content = await app.express_interest(
            interest_name, 
            must_be_fresh=True, 
            can_be_prefix=False, 
            lifetime=6000
        )
        return data_name, meta_info, content
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
        
async def run():
    host = Host('closest')
    host.cmd('export HOME=/tmp/mininet/closest')
    host.cmd('nfdc route add /snds/CAR_registry udp://10.0.0.2')

    interest_name = '/snds/CAR_registry'
    data_name, meta_info, content = await express_interest(interest_name)
    print(f'Received Data Name: {Name.to_str(data_name)}')
    print(meta_info)
    rIDs = list(content)
    print(rIDs)
        
    host.cmd('nfdc route add /snds/{} udp://10.0.0.2'.format(rIDs[-1]))

    interest_name= '/snds/{}'.format(rIDs[-1])
    data_name, meta_info, content = await express_interest(interest_name)
    print(f'Received Data Name: {Name.to_str(data_name)}')
    print(meta_info)
    print(bytes(content) if content else None)

    app.shutdown()

if __name__ == '__main__':
    app.run_forever(after_start=run())