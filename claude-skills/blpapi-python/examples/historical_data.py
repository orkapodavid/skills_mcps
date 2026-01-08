#!/usr/bin/env python3
"""
Historical Data Request example using //blp/refdata and HistoricalDataRequest.
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
    request = service.createRequest("HistoricalDataRequest")

    request.set(Name("security"), "AAPL US Equity")
    request.set(Name("startDate"), "20240101")
    request.set(Name("endDate"), "20241231")
    request.set(Name("periodicitySelection"), "DAILY")
    fields = request.getElement("fields")
    fields.appendValue("PX_LAST")

    cid = blpapi.CorrelationId(2001)
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
