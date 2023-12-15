from ndn.app        import  NDNApp
from ndn.encoding   import  Name, InterestParam, FormalName, BinaryStr
from typing         import  Optional

import random
import base64

app = NDNApp()

rID = []

@app.route('/snds/CAR')
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    print("Received Interest!!!")

    #Create the rID
    r_ID = random.randint(0,200)
    while r_ID in rID:
        r_ID = random.randint(0,10000)
    rID.append(r_ID)
    #print(rID[-1])
    #print(len(rID))
    
    app.put_data(name, content=(rID[-1].to_bytes(2, 'big')), freshness_period = 10000)
    print(f"Data sent: {Name.to_str(name)}")

@app.route('/snds/CAR_registry')
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    print("Received Interest!!!")
    app.put_data(name, content=bytes(rID), freshness_period = 10000)
    print(f"Data sent: {Name.to_str(name)}")


if __name__ == '__main__':
    app.run_forever()


