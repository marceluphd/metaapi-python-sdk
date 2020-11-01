from datetime import datetime
from typing_extensions import TypedDict
from typing import List, Optional
import iso8601
import random
import string
import pytz


def date(date_time: str) -> datetime:
    """Parses a date string into a datetime object."""
    return iso8601.parse_date(date_time)


def format_date(date: datetime) -> str:
    """Converts date to format compatible with JS"""
    return date.astimezone(pytz.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def random_id(length: int = 32) -> str:
    """Generates a random id of 32 symbols."""
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


class MetatraderAccountInformation(TypedDict):
    """MetaTrader account information (see https://metaapi.cloud/docs/client/models/metatraderAccountInformation/)"""

    platform: str
    """Platform id (mt4 or mt5)"""
    broker: str
    """Broker name."""
    currency: str
    """Account base currency ISO code."""
    server: str
    """Broker server name."""
    balance: float
    """Account balance."""
    equity: float
    """Account liquidation value."""
    margin: float
    """Used margin."""
    freeMargin: float
    """Free margin."""
    leverage: float
    """Account leverage coefficient."""
    marginLevel: float
    """Margin level calculated as % of equity/margin."""


class MetatraderPosition(TypedDict):
    """MetaTrader position"""

    id: int
    """Position id (ticket number)."""
    type: str
    """Position type (one of POSITION_TYPE_BUY, POSITION_TYPE_SELL)."""
    symbol: str
    """Position symbol."""
    magic: int
    """Position magic number, identifies the EA which opened the position."""
    time: datetime
    """Time position was opened at."""
    brokerTime: str
    """Time position was opened at, in broker timezone, YYYY-MM-DD HH:mm:ss.SSS format."""
    updateTime: datetime
    """Last position modification time."""
    openPrice: float
    """Position open price."""
    currentPrice: float
    """Current price."""
    currentTickValue: float
    """Current tick value."""
    stopLoss: Optional[float]
    """Optional position stop loss price."""
    takeProfit: Optional[float]
    """Optional position take profit price."""
    volume: float
    """Position volume."""
    swap: float
    """Position cumulative swap."""
    profit: float
    """Position cumulative profit."""
    comment: Optional[str]
    """Optional position comment. The sum of the line lengths of the comment and the clientId
    must be less than or equal to 26. For more information see https://metaapi.cloud/docs/client/clientIdUsage/"""
    clientId: Optional[str]
    """Optional client-assigned id. The id value can be assigned when submitting a trade and
    will be present on position, history orders and history deals related to the trade. You can use this field to bind
    your trades to objects in your application and then track trade progress. The sum of the line lengths of the
    comment and the clientId must be less than or equal to 26. For more information see
    https://metaapi.cloud/docs/client/clientIdUsage/"""
    unrealizedProfit: float
    """Profit of the part of the position which is not yet closed, including swap."""
    realizedProfit: float
    """Profit of the already closed part, including commissions and swap."""
    commission: Optional[float]
    """Optional position commission."""
    reason: str
    """Position opening reason. One of POSITION_REASON_CLIENT, POSITION_REASON_EXPERT, POSITION_REASON_MOBILE,
    POSITION_REASON_WEB, POSITION_REASON_UNKNOWN. See
    https://www.mql5.com/en/docs/constants/tradingconstants/positionproperties#enum_position_reason"""
    accountCurrencyExchangeRate: Optional[float]
    """Current exchange rate of account currency into USD."""
    originalComment: Optional[str]
    """Position original comment (present if possible to restore from history)."""
    updatePending: Optional[bool]
    """Flag indicating that position original comment and clientId was not identified yet and will be
    updated in a future packet"""


class MetatraderOrder(TypedDict):
    """MetaTrader order"""

    id: int
    """Order id (ticket number)."""
    type: str
    """Order type (one of ORDER_TYPE_SELL, ORDER_TYPE_BUY, ORDER_TYPE_BUY_LIMIT,
    ORDER_TYPE_SELL_LIMIT, ORDER_TYPE_BUY_STOP, ORDER_TYPE_SELL_STOP). See
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type"""
    state: str
    """Order state one of (ORDER_STATE_STARTED, ORDER_STATE_PLACED, ORDER_STATE_CANCELED,
    ORDER_STATE_PARTIAL, ORDER_STATE_FILLED, ORDER_STATE_REJECTED, ORDER_STATE_EXPIRED, ORDER_STATE_REQUEST_ADD,
    ORDER_STATE_REQUEST_MODIFY, ORDER_STATE_REQUEST_CANCEL). See
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_state"""
    magic: int
    """Order magic number, identifies the EA which created the order."""
    time: datetime
    """Time order was created at."""
    brokerTime: str
    """Time position was opened at, in broker timezone, YYYY-MM-DD HH:mm:ss.SSS format."""
    doneTime: Optional[datetime]
    """Optional time order was executed or canceled at. Will be specified for completed orders only."""
    doneBrokerTime: Optional[str]
    """Time order was executed or canceled at, in broker timezone, YYYY-MM-DD HH:mm:ss.SSS format. Will be specified
    for completed orders only"""
    symbol: str
    """Order symbol."""
    openPrice: float
    """Order open price (market price for market orders, limit price for limit orders or stop price for stop orders)."""
    currentPrice: float
    """Current price."""
    stopLoss: Optional[float]
    """Optional order stop loss price."""
    takeProfit: Optional[float]
    """Optional order take profit price."""
    volume: float
    """Order requested quantity."""
    currentVolume: float
    """Order remaining quantity, i.e. requested quantity - filled quantity."""
    positionId: str
    """Order position id. Present only if the order has a position attached to it."""
    comment: Optional[str]
    """Optional order comment. The sum of the line lengths of the comment and the clientId
    must be less than or equal to 26. For more information see https://metaapi.cloud/docs/client/clientIdUsage/"""
    originalComment: Optional[str]
    """Optional order original comment (present if possible to restore original comment from history)"""
    clientId: Optional[str]
    """Optional client-assigned id. The id value can be assigned when submitting a trade and
    will be present on position, history orders and history deals related to the trade. You can use this field to bind
    your trades to objects in your application and then track trade progress. The sum of the line lengths of the
    comment and the clientId must be less than or equal to 26. For more information see
    https://metaapi.cloud/docs/client/clientIdUsage/"""
    platform: str
    """Platform id (mt4 or mt5)."""
    updatePending: Optional[bool]
    """Optional flag indicating that order client id and original comment was not
    identified yet and will be updated in a future synchronization packet."""
    reason: str
    """Order opening reason. One of ORDER_REASON_CLIENT, ORDER_REASON_MOBILE, ORDER_REASON_WEB,
    ORDER_REASON_EXPERT, ORDER_REASON_SL, ORDER_REASON_TP, ORDER_REASON_SO, ORDER_REASON_UNKNOWN. See
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_reason."""
    fillingMode: str
    """Order filling mode. One of ORDER_FILLING_FOK, ORDER_FILLING_IOC, ORDER_FILLING_RETURN. See
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type_filling."""
    expirationType: str
    """Order expiration type. One of ORDER_TIME_GTC, ORDER_TIME_DAY, ORDER_TIME_SPECIFIED, ORDER_TIME_SPECIFIED_DAY.
    See https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type_time"""
    expirationTime: datetime
    """Optional order expiration time."""
    accountCurrencyExchangeRate: Optional[float]
    """Current exchange rate of account currency into USD."""


class MetatraderHistoryOrders(TypedDict):
    """MetaTrader history orders search query response."""

    historyOrders: List[MetatraderOrder]
    """Array of history orders returned."""
    synchronizing: bool
    """Flag indicating that history order initial synchronization is still in progress
    and thus search results may be incomplete"""


class MetatraderDeal(TypedDict):
    """MetaTrader deal"""

    id: str
    """Deal id (ticket number)"""
    type: str
    """Deal type (one of DEAL_TYPE_BUY, DEAL_TYPE_SELL, DEAL_TYPE_BALANCE, DEAL_TYPE_CREDIT,
    DEAL_TYPE_CHARGE, DEAL_TYPE_CORRECTION, DEAL_TYPE_BONUS, DEAL_TYPE_COMMISSION, DEAL_TYPE_COMMISSION_DAILY,
    DEAL_TYPE_COMMISSION_MONTHLY, DEAL_TYPE_COMMISSION_AGENT_DAILY, DEAL_TYPE_COMMISSION_AGENT_MONTHLY,
    DEAL_TYPE_INTEREST, DEAL_TYPE_BUY_CANCELED, DEAL_TYPE_SELL_CANCELED, DEAL_DIVIDEND, DEAL_DIVIDEND_FRANKED,
    DEAL_TAX). See https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties#enum_deal_type"""
    entryType: str
    """Deal entry type (one of DEAL_ENTRY_IN, DEAL_ENTRY_OUT, DEAL_ENTRY_INOUT,
    DEAL_ENTRY_OUT_BY). See https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties#enum_deal_entry"""
    symbol: Optional[str]
    """Optional symbol deal relates to."""
    magic: Optional[int]
    """Optional deal magic number, identifies the EA which initiated the deal."""
    time: datetime
    """Time the deal was conducted at."""
    brokerTime: str
    """Time the deal was conducted at, in broker timezone, YYYY-MM-DD HH:mm:ss.SSS format."""
    volume: Optional[float]
    """Optional deal volume."""
    price: Optional[float]
    """Optional, the price the deal was conducted at."""
    commission: Optional[float]
    """Optional deal commission."""
    swap: Optional[float]
    """Optional deal swap."""
    profit: float
    """Deal profit."""
    positionId: Optional[str]
    """Optional id of position the deal relates to."""
    orderId: Optional[str]
    """Optional id of order the deal relates to."""
    comment: Optional[str]
    """Optional deal comment. The sum of the line lengths of the comment and the clientId
    must be less than or equal to 26. For more information see https://metaapi.cloud/docs/client/clientIdUsage/"""
    originalComment: Optional[str]
    """Optional deal original comment (present if possible to restore original comment from history)."""
    clientId: Optional[str]
    """Optional client-assigned id. The id value can be assigned when submitting a trade and will be present on
    position, history orders and history deals related to the trade. You can use this field to bind your trades
    to objects in your application and then track trade progress. The sum of the line lengths of the comment and
    the clientId must be less than or equal to 26. For more information see
    https://metaapi.cloud/docs/client/clientIdUsage/"""
    platform: str
    """Platform id (mt4 or mt5)."""
    updatePending: Optional[bool]
    """Optional flag indicating that deal client id and original comment was not
    identified yet and will be updated in a future synchronization packet"""
    reason: Optional[str]
    """Optional deal execution reason. One of DEAL_REASON_CLIENT, DEAL_REASON_MOBILE, DEAL_REASON_WEB,
    DEAL_REASON_EXPERT, DEAL_REASON_SL, DEAL_REASON_TP, DEAL_REASON_SO, DEAL_REASON_ROLLOVER, DEAL_REASON_VMARGIN,
    DEAL_REASON_SPLIT, DEAL_REASON_UNKNOWN. See
    https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties#enum_deal_reason."""
    accountCurrencyExchangeRate: Optional[float]
    """Current exchange rate of account currency into USD."""


class MetatraderDeals(TypedDict):
    """MetaTrader history deals search query response"""

    deals: List[MetatraderDeal]
    """Array of history deals returned."""
    synchronizing: bool
    """Flag indicating that deal initial synchronization is still in progress
    and thus search results may be incomplete."""


MetatraderSession = TypedDict(
    "MetatraderSession",
    {
        "from": str,  # Session start time, in hh.mm.ss.SSS format.
        "to": str  # Session end time, in hh.mm.ss.SSS format.
    }
)
"""Metatrader trade or quote session"""


class MetatraderSessions(TypedDict):
    """Metatrader trade or quote session container, indexed by weekday."""
    SUNDAY: Optional[List[MetatraderSession]]
    """Array of sessions for SUNDAY."""
    MONDAY: Optional[List[MetatraderSession]]
    """Array of sessions for MONDAY."""
    TUESDAY: Optional[List[MetatraderSession]]
    """Array of sessions for TUESDAY."""
    WEDNESDAY: Optional[List[MetatraderSession]]
    """Array of sessions for WEDNESDAY."""
    THURSDAY: Optional[List[MetatraderSession]]
    """Array of sessions for THURSDAY."""
    FRIDAY: Optional[List[MetatraderSession]]
    """Array of sessions for FRIDAY."""
    SATURDAY: Optional[List[MetatraderSession]]
    """Array of sessions for SATURDAY."""


class MetatraderSymbolSpecification(TypedDict):
    """MetaTrader symbol specification. Contains symbol specification (see
    https://metaapi.cloud/docs/client/models/metatraderSymbolSpecification/)"""

    symbol: str
    """Symbol (e.g. a currency pair or an index)."""
    tickSize: float
    """Tick size"""
    minVolume: float
    """Minimum order volume for the symbol."""
    maxVolume: float
    """Maximum order volume for the symbol."""
    volumeStep: float
    """Order volume step for the symbol."""
    fillingModes: List[str]
    """List of allowed order filling modes. Can contain ORDER_FILLING_FOK, ORDER_FILLING_IOC or both.
    See https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#symbol_filling_mode for more
    details."""
    executionMode: str
    """Deal execution mode. Possible values are SYMBOL_TRADE_EXECUTION_REQUEST, SYMBOL_TRADE_EXECUTION_INSTANT,
    SYMBOL_TRADE_EXECUTION_MARKET, SYMBOL_TRADE_EXECUTION_EXCHANGE. See
    https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#enum_symbol_trade_execution for more
    details."""
    contractSize: float
    """Trade contract size."""
    quoteSessions: MetatraderSessions
    """Quote sessions, indexed by day of week."""
    tradeSessions: MetatraderSessions
    """Trade sessions, indexed by day of week."""
    tradeMode: Optional[str]
    """Order execution type. Possible values are SYMBOL_TRADE_MODE_DISABLED, SYMBOL_TRADE_MODE_LONGONLY,
    SYMBOL_TRADE_MODE_SHORTONLY, SYMBOL_TRADE_MODE_CLOSEONLY, SYMBOL_TRADE_MODE_FULL. See
    https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#enum_symbol_trade_mode for more
    details."""
    bondAccruedInterest: Optional[float]
    """Accrued interest – accumulated coupon interest, i.e. part of the coupon interest calculated in proportion to
    the number of days since the coupon bond issuance or the last coupon interest payment."""
    bondFaceValue: Optional[float]
    """Face value – initial bond value set by the issuer."""
    optionStrike: Optional[float]
    """The strike price of an option. The price at which an option buyer can buy (in a Call option) or sell (in a
    Put option) the underlying asset, and the option seller is obliged to sell or buy the appropriate amount of the
    underlying asset."""
    optionPriceSensivity: Optional[float]
    """Option/warrant sensitivity shows by how many points the price of the option's underlying asset should change so
    that the price of the option changes by one point."""
    liquidityRate: Optional[float]
    """Liquidity Rate is the share of the asset that can be used for the margin."""
    initialMargin: float
    """Initial margin means the amount in the margin currency required for opening a position with the volume of one
    lot. It is used for checking a client's assets when he or she enters the market."""
    maintenanceMargin: float
    """The maintenance margin. If it is set, it sets the margin amount in the margin currency of the symbol, charged
    from one lot. It is used for checking a client's assets when his/her account state changes. If the maintenance
    margin is equal to 0, the initial margin is used."""
    hedgedMargin: float
    """Contract size or margin value per one lot of hedged positions (oppositely directed positions of one symbol).
    Two margin calculation methods are possible for hedged positions. The calculation method is defined by the broker"""
    hedgedMarginUsesLargerLeg: Optional[bool]
    """Calculating hedging margin using the larger leg (Buy or Sell)."""
    marginCurrency: str
    """Margin currency."""
    priceCalculationMode: str
    """Contract price calculation mode. One of SYMBOL_CALC_MODE_UNKNOWN, SYMBOL_CALC_MODE_FOREX,
    SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE, SYMBOL_CALC_MODE_FUTURES, SYMBOL_CALC_MODE_CFD, SYMBOL_CALC_MODE_CFDINDEX,
    SYMBOL_CALC_MODE_CFDLEVERAGE, SYMBOL_CALC_MODE_EXCH_STOCKS, SYMBOL_CALC_MODE_EXCH_FUTURES,
    SYMBOL_CALC_MODE_EXCH_FUTURES_FORTS, SYMBOL_CALC_MODE_EXCH_BONDS, SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX,
    SYMBOL_CALC_MODE_EXCH_BONDS_MOEX, SYMBOL_CALC_MODE_SERV_COLLATERAL. See
    https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#enum_symbol_calc_mode for more
    details."""
    baseCurrency: str
    """Base currency."""
    profitCurrency: Optional[str]
    """Profit currency."""
    swapMode: str
    """Swap calculation model. Allowed values are SYMBOL_SWAP_MODE_DISABLED,
    SYMBOL_SWAP_MODE_POINTS, SYMBOL_SWAP_MODE_CURRENCY_SYMBOL, SYMBOL_SWAP_MODE_CURRENCY_MARGIN,
    SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT, SYMBOL_SWAP_MODE_INTEREST_CURRENT, SYMBOL_SWAP_MODE_INTEREST_OPEN,
    SYMBOL_SWAP_MODE_REOPEN_CURRENT, SYMBOL_SWAP_MODE_REOPEN_BID. See
    https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#enum_symbol_swap_mode for more
    details."""
    swapLong: Optional[float]
    """Long swap value."""
    swapShort: Optional[float]
    """Short swap value."""
    swapRollover3Days: str
    """Day of week to charge 3 days swap rollover. Allowed values are SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURDAY,
    FRIDAY, SATURDAY."""
    allowedExpirationModes: List[str]
    """Allowed order expiration modes. Allowed values are SYMBOL_EXPIRATION_GTC, SYMBOL_EXPIRATION_DAY,
    SYMBOL_EXPIRATION_SPECIFIED, SYMBOL_EXPIRATION_SPECIFIED_DAY.
    See https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#symbol_expiration_mode for more
    details."""
    allowedOrderTypes: List[str]
    """Allowed order types. Allowed values are SYMBOL_ORDER_MARKET, SYMBOL_ORDER_LIMIT, SYMBOL_ORDER_STOP,
    SYMBOL_ORDER_STOP_LIMIT, SYMBOL_ORDER_SL, SYMBOL_ORDER_TP, SYMBOL_ORDER_CLOSEBY. See
    https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#symbol_order_mode for more details."""
    orderGTCMode: str
    """If the expirationMode property is set to SYMBOL_EXPIRATION_GTC (good till canceled), the expiration of pending
    orders, as well as of Stop Loss/Take Profit orders should be additionally set using this enumeration. Allowed
    values are SYMBOL_ORDERS_GTC, SYMBOL_ORDERS_DAILY, SYMBOL_ORDERS_DAILY_EXCLUDING_STOPS. See
    https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#enum_symbol_order_gtc_mode for more
    details."""
    digits: int
    """Digits after a decimal point."""
    path: Optional[str]
    """Path in the symbol tree."""
    description: str
    """Symbol description."""
    startTime: Optional[datetime]
    """Date of the symbol trade beginning (usually used for futures)."""
    expirationTime: Optional[datetime]
    """Date of the symbol trade end (usually used for futures)."""


class MetatraderSymbolPrice(TypedDict):
    """MetaTrader symbol price. Contains current price for a symbol (see
    https://metaapi.cloud/docs/client/models/metatraderSymbolPrice/)"""

    symbol: str
    """Symbol (e.g. a currency pair or an index)."""
    bid: float
    """Bid price."""
    ask: float
    """Ask price."""
    profitTickValue: float
    """Tick value for a profitable position."""
    lossTickValue: float
    """Tick value for a loosing position."""
    accountCurrencyExchangeRate: float
    """Current exchange rate of account currency into USD."""
    time: str
    """Quote time, in ISO format"""
    brokerTime: str
    """Quote time, in broker timezone, YYYY-MM-DD HH:mm:ss.SSS format."""


class MetatraderTradeResponse(TypedDict):
    """MetaTrader trade response."""

    numericCode: int
    """Numeric response code, see https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes and
    https://book.mql4.com/appendix/errors. Response codes which indicate success are 0, 10008-10010, 10025. The rest
    codes are errors."""
    stringCode: str
    """String response code, see https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes and
    https://book.mql4.com/appendix/errors. Response codes which indicate success are ERR_NO_ERROR,
    TRADE_RETCODE_PLACED, TRADE_RETCODE_DONE, TRADE_RETCODE_DONE_PARTIAL, TRADE_RETCODE_NO_CHANGES. The rest codes are
    errors."""
    message: str
    """Human-readable response message."""
    orderId: str
    """Order id which was created/modified during the trade."""
    positionId: str
    """Position id which was modified during the trade."""


class TradeOptions(TypedDict):
    """Common trade options."""

    comment: Optional[str]
    """Optional order comment. The sum of the line lengths of the comment and the clientId must be less than or equal
    to 26. For more information see https://metaapi.cloud/docs/client/clientIdUsage/"""
    clientId: Optional[str]
    """Optional client-assigned id. The id value can be assigned when submitting a trade and will be present on
    position, history orders and history deals related to the trade. You can use this field to bind your trades to
    objects in your application and then track trade progress. The sum of the line lengths of the comment and the
    clientId must be less than or equal to 26. For more information see
    https://metaapi.cloud/docs/client/clientIdUsage/"""
    magic: Optional[str]
    """Magic (expert id) number. If not set default value specified in account entity will be used."""
    slippage: Optional[int]
    """Optional slippage in points. Should be greater or equal to zero. In not set, default value specified in
    account entity will be used. Slippage is ignored if execution mode set to SYMBOL_TRADE_EXECUTION_MARKET in
    symbol specification."""


class MarketTradeOptions(TradeOptions):
    """Market trade options."""

    fillingModes: Optional[List[str]]
    """Optional allowed filling modes in the order of priority. Default is to allow all filling modes and prefer
    ORDER_FILLING_FOK over ORDER_FILLING_IOC. See
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type_filling for extra
    explanation."""


class ExpirationOptions(TypedDict):
    """Pending order expiration settings."""

    type: str
    """Pending order expiration type. See
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type_time for the list of
    possible options. MetaTrader4 platform supports only ORDER_TIME_SPECIFIED expiration type. One of ORDER_TIME_GTC,
    ORDER_TIME_DAY, ORDER_TIME_SPECIFIED, ORDER_TIME_SPECIFIED_DAY."""
    time: Optional[datetime]
    """Optional pending order expiration time. Ignored if expiration type is not one of ORDER_TIME_DAY or
    ORDER_TIME_SPECIFIED."""


class PendingTradeOptions(TradeOptions):
    """Pending order trade options."""

    expiration: Optional[ExpirationOptions]
    """Optional pending order expiration settings. See Pending order expiration settings section."""


class ValidationDetails(TypedDict):
    """Object to supply additional information for validation exceptions."""
    parameter: str
    """Name of invalid parameter."""
    value: Optional[str]
    """Entered invalid value."""
    message: str
    """Error message."""


class ExceptionMessage(TypedDict):
    """A REST API response that contains an exception message"""
    id: int
    """Error id"""
    error: str
    """Error name"""
    numericCode: Optional[int]
    """Numeric error code"""
    stringCode: Optional[str]
    """String error code"""
    message: str
    """Human-readable error message"""
    details: Optional[List[ValidationDetails]]
    """Additional information about error. Used to supply validation error details."""
