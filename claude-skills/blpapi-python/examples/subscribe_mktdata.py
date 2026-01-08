#!/usr/bin/env python3
"""
Market Data subscription example using //blp/mktdata.
"""
import blpapi
from blpapi import Session, SessionOptions


def main():
    options = SessionOptions()
    session = Session(options)
    if not session.start():
        raise RuntimeError("Failed to start session")
    if not session.openService("//blp/mktdata"):
        raise RuntimeError("Failed to open //blp/mktdata")

    subs = blpapi.SubscriptionList()
    subs.add(topic="/AAPL US Equity", fields=["BID", "ASK", "LAST_PRICE"], options=["interval=1"], correlationId=blpapi.CorrelationId(4001))
    session.subscribe(subs)

    try:
        while True:
            event = session.nextEvent()
            if event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
                for msg in event:
                    print(msg.toString())
            elif event.eventType() == blpapi.Event.SUBSCRIPTION_STATUS:
                for msg in event:
                    print("STATUS:", msg.toString())
    except KeyboardInterrupt:
        session.unsubscribe(subs)
        session.stop()


if __name__ == "__main__":
    main()
