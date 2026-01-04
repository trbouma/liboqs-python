from monstr.event.event import Event
from typing import Union
import json

import oqs


class PQEvent(Event):
    test: str
    sigalg: str = "ML-DSA-44"

    def sign(self, priv_key):
        
        signer = oqs.Signature(self.sigalg,secret_key=bytes.fromhex(priv_key))
        # print(f"sign with {priv_key}")
        self._get_id()
        id_bytes = (bytes(bytearray.fromhex(self._id)))
       
        signature = signer.sign(id_bytes)
        self.sig = signature.hex()

    def is_valid(self):
        is_valid = False
        verifier = oqs.Signature(self.sigalg)

        id_bytes = (bytes(bytearray.fromhex(self.id)))
        sig_bytes = (bytes(bytearray.fromhex(self.sig)))
        pub_key_bytes = (bytes(bytearray.fromhex(self.pub_key)))

        is_valid = verifier.verify(id_bytes, sig_bytes, pub_key_bytes)

        return is_valid
    
    @staticmethod    
    def load(event_data: Union[str, dict], validate=False) -> 'PQEvent':
        """
            return a Event object either from a dict or json str this replaces the old from_JSON method
            that was actually just from a string...
            if validate is set True will test the event sig, if it's not None will be returned

        """
        if isinstance(event_data, str):
            try:
                event_data = json.loads(event_data)
            except Exception as e:
                event_data = {}

        id = None
        if 'id' in event_data:
            id = event_data['id']

        sig = None
        if 'sig' in event_data:
            sig = event_data['sig']

        kind = None
        if 'kind' in event_data:
            kind = event_data['kind']

        content = None
        if 'content' in  event_data:
            content = event_data['content']

        tags = None
        if 'tags' in event_data:
            tags = event_data['tags']

        pub_key = None
        if 'pubkey' in event_data:
            pub_key = event_data['pubkey']

        created_at = None
        if 'created_at' in event_data:
            created_at = event_data['created_at']

        ret = PQEvent(
            id=id,
            sig=sig,
            kind=kind,
            content=content,
            tags=tags,
            pub_key=pub_key,
            created_at=created_at
        )

        # None ret if validating and the evnt is not valid
        if validate is True and ret.is_valid() is False:
            ret = None

        return ret


if __name__ == "main":
    print("nostr nqsafe")