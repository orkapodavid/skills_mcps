#!/usr/bin/env python3
"""
Reference Data Request example using //blp/refdata and ReferenceDataRequest.
Requires Bloomberg Terminal and BLPAPI Python installed.
"""
import blpapi
from blpapi import Session, SessionOptions, Name


def main():
    options = SessionOptions()
    session = Session(options)
    if not session.start():
        raise RuntimeError("Failed to start session")
    if not session.openService("//blp/refdata"):
        raise RuntimeError("Failed to open //blp/refdata")

    service = session.getService("//blp/refdata")
    request = service.createRequest("ReferenceDataRequest")

    # securities
    securities = request.getElement("securities")
    securities.appendValue("AAPL US Equity")
    securities.appendValue("MSFT US Equity")

    # fields
    fields = request.getElement("fields")
    for f in ["PX_LAST", "DS002"]:
        fields.appendValue(f)

    # send request
    cid = blpapi.CorrelationId(1001)
    session.sendRequest(request, correlationId=cid)

    # event loop
    while True:
        event = session.nextEvent()
        et = event.eventType()
        for msg in event:
            print(msg.toString())
        if et == blpapi.Event.RESPONSE:
            break

    session.stop()


if __name__ == "__main__":
    main()
