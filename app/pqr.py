from monstr.relay.relay import Relay
from monstr.relay.exceptions import NostrCommandException, NostrNoticeException, NostrNotAuthenticatedException
from monstr.event.event import Event
from monstr.event.persist import RelayEventStoreInterface, ARelayEventStoreInterface

import logging, json
from typing import Union

from nqsafe import PQEvent



class PQRelay(Relay):
    pq: bool = True

    async def _do_event(self, req_json, ws):
        if len(req_json) <= 1:
            raise NostrNoticeException('EVENT command missing event data')
        
        len_pubkey = len(req_json[1]['pubkey'])
        print(f"len pubkey is: {len_pubkey}")

        if len_pubkey > 64:
            evt = PQEvent.load(req_json[1])   
        else:
            evt = Event.load(req_json[1])
            
            
            
        if not evt.is_valid():
            raise NostrCommandException(event_id=evt.id,
                                       success=False,
                                       message='invalid: signature validation failed')
        



        # check against any acceptors we've been handed
        # acceptors may throw NostrCommandException, NostrNoticeException, NostrNotAuthenticatedException
        for c_accept in self._accept_req:
            c_accept.accept_post(ws, evt)

        try:
            saved = False
            if self._store:
                if isinstance(self._store, ARelayEventStoreInterface):
                    await self._store.add_event(evt)
                else:
                    self._store.add_event(evt)
                logging.debug('Relay::_do_event event sent to store %s ' % evt)
                saved = True
        except Exception as e:
            logging.debug('Relay::store event failed - %s' % e)

        # do the subs
        await self._check_subs(evt)

        raise NostrCommandException(event_id=evt.id,
                                    success=saved,
                                    message='')
    
