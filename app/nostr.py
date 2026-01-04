from monstr.event.event import Event
from monstr.encrypt import Keys
from monstr.client.client import Client, ClientPool

import asyncio, json

from nqsafe import PQEvent
import oqs

async def publish(event: Event):
    relay_pool = ["ws://localhost:8735"]
    async with ClientPool(relay_pool) as c:
        print(f"publish regular event is valid {event.is_valid()}")
        
        c.publish(evt=event)

async def pqc_publish(event: PQEvent):
    relay_pool = ["ws://localhost:8735"]
    async with ClientPool(relay_pool) as c:
        print(f"publish pqc event is valid {event.is_valid()}")
        c.publish(evt=event)



if __name__ == "__main__":

    sigalg = "ML-DSA-44"
    signer = oqs.Signature(sigalg)
    signer_public_key = signer.generate_keypair()
    signer_public_key_hex = signer_public_key.hex()

    secret_key = signer.export_secret_key()

    content = "This is a quantum safe event I hope. to be or not to be."
    tags = ["t", "quantum_safe"]
    pq_event = PQEvent( pub_key=signer_public_key_hex,
                       content=content,
                       tags = tags,
                       kind = 100001
                       
                       
                       )

    pq_event._get_id()
    pq_event.id = pq_event._id

    signer_public_key_bytes = bytes.fromhex(signer_public_key_hex)
   
    
    

    pq_event.sign(priv_key=secret_key.hex())
    print(f"nostr pqevent {pq_event.data()}")
    print(f"is valid: {pq_event.is_valid()}")

    #Let's try a regular event
    regular_keys = Keys()

    regular_event: Event = Event(   pub_key=regular_keys.public_key_hex(),
                                    kind = 100001,
                                    content="regular event")
    
    regular_event.sign(priv_key=regular_keys.private_key_hex())
    print(f"check to see if reqular event is valid {regular_event.is_valid()}")

    asyncio.run(publish(regular_event))
    print("regular event published!")

    asyncio.run(pqc_publish(pq_event))
    print(f"check to see if pqc event is valid {pq_event.is_valid()}")

    # print("pq event published!")

    event_data = pq_event.data()
    print(f"event data: {event_data}")
    new_pqc_event = PQEvent.load(event_data=event_data)
    print(f"new pqc event {new_pqc_event.is_valid()}")
