from ndn.app        import NDNApp
from ndn.encoding   import Name, InterestParam, BinaryStr, FormalName
from typing         import Optional
from mininet.node   import Host

import random
import base64
import sys
import subprocess

app = NDNApp()

TYPE = sys.argv[1]

subprocess.run(["nlsrc", "advertise", "/snds/{}".format(TYPE)])
subprocess.run(["nlsrc", "advertise", "/snds/{}_registry".format(TYPE)])

rID = []
    
@app.route('/snds/{}'.format(TYPE))
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    print(f"Received Interest: {Name.to_str(name)}")

    #create the rID
    r_ID = random.randint(0,200)
    while r_ID in rID:
        r_ID = random.randint(0,200)
    rID.append(r_ID)
    #print(rID[-1])
    #print(rID)

    app.put_data(name, content=(rID[-1].to_bytes(2, 'big')), freshness_period=10000)

    print(f"Data sent: {Name.to_str(name)}")

@app.route('/snds/{}_registry'.format(TYPE))
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    print(f"Received Interest: {Name.to_str(name)}")

    #print(rID)
    app.put_data(name, content=bytes(rID), freshness_period=10000)

    print(f"Data sent: {Name.to_str(name)}")

if __name__ == '__main__':
    app.run_forever()