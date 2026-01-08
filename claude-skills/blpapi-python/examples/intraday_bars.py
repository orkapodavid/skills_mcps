#!/usr/bin/env python3
"""
Intraday Bars example using //blp/intraday and IntradayBarRequest.
"""
import blpapi
from blpapi import Session, SessionOptions, Name, Datetime


def main():
    options = SessionOptions()
    session = Session(options)
    if not session.start():
        raise RuntimeError("Failed to start session")
    if not session.openService("//blp/intraday"):
        raise RuntimeError("Failed to open //blp/intraday")

    service = session.getService("//blp/intraday")
    request = service.createRequest("IntradayBarRequest")

    request.set(Name("security"), "AAPL US Equity" )
    request.set(Name("eventType"), "TRADE")
    request.set(Name("interval"), 5)
    request.set(Name("startDateTime"), Datetime(2024, 1, 2, 9, 30))
    request.set(Name("endDateTime"), Datetime(2024, 1, 2, 16, 0))
    request.set(Name("gapFillInitialBar"), True)

    cid = blpapi.CorrelationId(3001)
    session.sendRequest(request, correlationId=cid)

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
