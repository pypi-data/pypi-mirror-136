import websocket
import datetime
from typing import Optional, Callable
from foxbit.frame import MessageFrame


class Client(websocket.WebSocketApp):
    """Client is a simple subclass of websocket.WebSocketApp class
    (from websocket-client module), where url parameter is
    wss://api.foxbit.com.br.

    Example:
    ```python
    def on_open(ws):
        print("connected")

    def on_message(ws, msg):
        frame = MessageFrame.fromJSON(msg)
        print(frame)

    def on_error(ws, err):
        print(err)

    def on_close(ws, status, msg):
        print("closed with status {}: {}".format(status, msg))
    ```

    Parameters
    ----------
    on_open : Callable, optional
        Callback object which is called at opening websocket.
        on_open has one argument.
        The 1st argument is this class object.

    on_message : Callable, required
        Callback object which is called when received data.
        on_message has 2 arguments.
        The 1st argument is this class object.
        The 2nd argument is utf-8 data received from the server.

    on_error : Callable, optional
        Callback object which is called when we get error.
        on_error has 2 arguments.
        The 1st argument is this class object.
        The 2nd argument is exception object.

    on_close : Callable, optional
        Callback object which is called when connection is closed.
        on_close has 3 arguments.
        The 1st argument is this class object.
        The 2nd argument is close_status_code.
        The 3rd argument is close_msg.

    enableTrace : bool, optional
        Boolean object which enable websocket trace.
        Good for debbuging.
    """

    def __init__(
        self,
        on_open: Optional[Callable] = None,
        on_message: Callable = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        enableTrace: Optional[bool] = False
    ) -> None:
        websocket.enableTrace(enableTrace)
        websocket.WebSocketApp.__init__(
            self,
            'wss://api.foxbit.com.br/',
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )


class PublicClient(Client):
    """PublicClient is a simple subclass of client.Client class
    (from foxbit.client module)

    All documentation is available at
    https://foxbit.com.br/wp-content/uploads/2018/07/Documentacao-api-fox-bit.pdf
    """

    def __init__(
        self,
        on_open: Optional[Callable] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        enableTrace: Optional[bool] = False
    ) -> None:
        Client.__init__(
            self,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            enableTrace=enableTrace
        )

    def getInstrument(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1
    ) -> None:
        """Retrieves the details of a specific
        instrument from the Order Management System
        of the trading venue. An instrument is a pair
        of exchanged products (or fractions of them)
        such as US dollars and ounces of gold.

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System f
            rom where the instrument is traded
            (default is 1).

        InstrumentId : int, optional
            The ID of the instrument
            (default is 1).
        """

        frame = MessageFrame(
            endpoint='GetInstrument',
            payload={
                'OMSId': OMSId,
                'InstrumentId': InstrumentId
            }
        )
        self.send(frame.toJSON())

    def getInstruments(
        self,
        OMSId: Optional[int] = 1
    ) -> None:
        """Retrieves an array of instrument objects
        describing all instruments available on a trading
        venue to the user. An instrument is a pair of
        exchanged products (or fractions of them) such as US
        dollars and ounces of gold.

        Parameters
        ----------
        OMSId : int, optional
            The Order Management System Id
            (default is 1).
        """

        frame = MessageFrame(
            endpoint='GetInstruments',
            payload={
                'OMSId': OMSId
            }
        )
        self.send(frame.toJSON())

    def getProducts(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1
    ) -> None:
        """Returns an array of products available
        on the trading venue. A product is an asset that is
        tradable or paid out.

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System
            for which the array of available
            products and currencies will be returned
            (default is 1).

        InstrumentId : int, optional
            The ID of the product
            (often a currency) on the specified Order
            Management System
            (default is 1).
        """

        frame = MessageFrame(
            endpoint='GetProducts',
            payload={
                'OMSId': OMSId
            }
        )
        self.send(frame.toJSON())

    def getL2Snapshot(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1,
        Depth: Optional[int] = 100
    ) -> None:
        """Provides a current Level 2 snapshot
        of a specific instrument trading on an Order
        Management System to a user-determined market depth.

        The Level 2 snapshot allows the user to specify
        the level of market depth information on either side
        of the bid and ask.

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System
            where the instrument is traded
            (default is 1).

        InstrumentId : int, optional
            The ID of the instrument that is
            the subject of the snapshot
             (default is 1).

        Depth : int, optional
            Depth in this call is “depth of market”,
            the number of buyers and sellers at greater
            or lesser prices in the order book for the instrument
            (default is 100).
        """

        frame = MessageFrame(
            endpoint='GetL2Snapshot',
            payload={
                'OMSId': OMSId,
                'InstrumentId': InstrumentId,
                'Depth': Depth
            }
        )
        self.send(frame.toJSON())

    def getTickerHistory(
        self,
        InstrumentId: Optional[int] = 1,
        Interval: Optional[int] = 60,
        FromDate: datetime.datetime = None,
        ToDate: Optional[datetime.datetime] = datetime.datetime.now()
    ) -> None:
        """Requests a ticker history
        (high, low, open, close, volume, bid, ask, ID)
        of a specific instrument from a given date forward to the present.

        Parameters
        ----------
        InstrumentId : int, optional
            The ID of a specific instrument.
            The Order Management System and the default Account
            ID of the logged-in user are assumed
            (default is 1).

        Interval : int, optional
            Interval in seconds.
            Possible values are 60, 300, 900,
            1800, 3600, 21600, 43200, 86400, 604800
            (default is 60).

        FromDate : datetime.datetime, required
            Oldest date from which the ticker history will start.
            The method convert it to POSIX format and UTC time zone.
            The report moves toward the present from this point.

        ToDate : datetime.datetime, optional
            Newest date from which the ticker history will go.
            The method convert it to POSIX format and UTC time zone.
            The report moves toward the present from this point
            (default is `datetime.datetime.now()`).
        """

        _from = MessageFrame.buildValidPosixTimeString(FromDate)
        _to = MessageFrame.buildValidPosixTimeString(ToDate)

        frame = MessageFrame(
            endpoint='GetTickerHistory',
            payload={
                'InstrumentId': InstrumentId,
                'Interval': Interval,
                'FromDate': _from,
                'ToDate': _to
            }
        )
        self.send(frame.toJSON())

    def subscribeTicker(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1,
        Interval: Optional[int] = 60,
        IncludeLastCount: Optional[int] = 100
    ) -> None:
        """Subscribes a user to a Ticker Market Data Feed
        for a specific instrument and interval.
        SubscribeTicker sends a response object as described below,
        and then periodically returns a TickerDataUpdateEvent
        that matches the content of the response object.

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System
            (default is 1).

        InstrumentId : int, optional
            The ID of the instrument whose
            information you want to track
            (default is 1).

        Interval : int, optional
            Specifies in seconds how frequently
            to obtain ticker updates. Default is
            60 — one minute
            (default is 60).

        IncludeLastCount : int, optional
            The limit of records returned in
            the ticker history. The default is 100
            (default is 100).
        """

        frame = MessageFrame(
            endpoint='SubscribeTicker',
            payload={
                'OMSId': OMSId,
                'InstrumentId': InstrumentId,
                'Interval': Interval,
                'IncludeLastCount': IncludeLastCount
            }
        )
        self.send(frame.toJSON())

    def unsubscribeTicker(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1
    ) -> None:
        """Unsubscribes a user from a Ticker Market Data Feed

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System
            on which the user has subscribed to a
            ticker market data feed
            (default is 1).

        InstrumentId : int, optional
            The ID of the instrument being tracked
            by the ticker market data feed
            (default is 1).
        """

        frame = MessageFrame(
            endpoint='UnsubscribeTicker',
            payload={
                'OMSId': OMSId,
                'InstrumentId': InstrumentId
            }
        )
        self.send(frame.toJSON())

    def subscribeLevel1(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1,
        Symbol: Optional[str] = None
    ) -> None:
        """Retrieves the latest Level 1 Ticker information
        and then subscribes the user to ongoing Level 1
        market data event updates for one specific instrument.

        The SubscribeLevel1 call responds with the Level 1
        response shown below. The OMS then periodically sends
        Leve1UpdateEvent information when best bid/best offer
        issues in the same format as this response,
        until you send the UnsubscribeLevel1 call.

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System on which
            the instrument trades
            (default is 1).

        InstrumentId : int, optional
            The ID of the instrument you are tracking.
            Conditionally optional
            (default is 1).

        Symbol : str, optional
            The symbol of the instrument you are tracking
            (ex. 'BTCUSD')
            Conditionally optional.
        """

        if (Symbol is not None):
            frame = MessageFrame(
                endpoint='SubscribeLevel1',
                payload={
                    'OMSId': OMSId,
                    'Symbol': Symbol
                }
            )
        else:
            frame = MessageFrame(
                endpoint='SubscribeLevel1',
                payload={
                    'OMSId': OMSId,
                    'InstrumentId': InstrumentId
                }
            )
        self.send(frame.toJSON())

    def unsubscribeLevel1(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1
    ) -> None:
        """Unsubscribes the user from a Level 1
        Market Data Feed subscription.

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System on which
            the user has subscribed to a Level 1 market data feed
            (default is 1).

        InstrumentId: int, optional
            The ID of the instrument being tracked by
            the Level 1 market data feed
            (default is 1).
        """
        frame = MessageFrame(
            endpoint='UnsubscribeLevel1',
            payload={
                'OMSId': OMSId,
                'InstrumentId': InstrumentId
            }
        )
        self.send(frame.toJSON())

    def subscribeLevel2(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1,
        Symbol: Optional[str] = None,
        Depth: Optional[int] = 10
    ) -> None:
        """Retrieves the latest Level 2 Ticker information
        and then subscribes the user to Level 2 market data
        event updates for one specific instrument.
        Level 2 allows the user to specify the level of market depth
        information on either side of the bid and ask.

        The OMS then periodically sends Level2UpdateEvent
        information in the same format as this response
        until you send the UnsubscribeLevel2 call.

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System
            on which the instrument trades
            (default is 1).

        InstrumentId : int, optional
            The ID of the instrument you are tracking.
            Conditionally optional
            (default is 1).

        Symbol : str, optional
            The symbol of the instrument you are tracking.
            Conditionally optional

        Depth : int
            The depth of the order book.
            The example request returns 10 price
            levels on each side of the market.
            (default is 10).
        """

        if (Symbol is not None):
            frame = MessageFrame(
                endpoint='SubscribeLevel2',
                payload={
                    'OMSId': OMSId,
                    'Symbol': Symbol,
                    'Depth': Depth
                }
            )
        else:
            frame = MessageFrame(
                endpoint='SubscribeLevel2',
                payload={
                    'OMSId': OMSId,
                    'InstrumentId': InstrumentId,
                    'Depth': Depth
                }
            )
        self.send(frame.toJSON())

    def unsubscribeLevel2(
        self,
        OMSId: Optional[int] = 1,
        InstrumentId: Optional[int] = 1
    ) -> None:
        """Unsubscribes the user from a Level 2
        Market Data Feed subscription.

        Parameters
        ----------
        OMSId : int, optional
            The ID of the Order Management System on which
            the user has subscribed to a Level 1 market data feed.
            (default is 1).

        InstrumentId: int, optional
            The ID of the instrument being tracked by
            the Level 1 market data feed
            (default is 1).
        """
        frame = MessageFrame(
            endpoint='UnsubscribeLevel2',
            payload={
                'OMSId': OMSId,
                'InstrumentId': InstrumentId
            }
        )
        self.send(frame.toJSON())

    def onSubscription(
        self,
        subscription: str,
        frame: MessageFrame,
        callback: Callable
    ) -> None:
        """
        Method to be used inside `on_message` function
        after that the method `subscribe*` is used.

        Parameters
        ----------
        subscribe : str, required
            Valid values:
            * 'SubscribeLevel1',
            * 'SubscribeLevel2',
            * 'SubscribeTicker',
            * 'SubscribeTrades',
            * 'UnsubscribeLevel1',
            * 'UnsubscribeLevel2',
            * 'UnsubscribeTicker',
            * 'UnsubscribeTrades'
            * 'TickerDataUpdateEvent',
            * 'Level1UpdateEvent',
            * 'Level2UpdateEvent',
            * 'TradeDataUpdateEvent'

        frame : MessageFrame, required
            The received frame in `on_message` function

        callback : Callable, required
            The calback function to be executed when
            requirements are suitable
        """
        if (frame.endpoint == subscription):
            callback(frame)
