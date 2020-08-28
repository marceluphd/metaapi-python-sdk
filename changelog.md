6.1.0
  - added ability to select filling mode when placing a market order, in trade options
  - added ability to set expiration options when placing a pending order, in trade options
  - added reason field to position, order and deal
  - added fillingMode field to MetaTraderOrder model
  - added order expiration time and type
  
6.0.2
  - added code sample download video to readme
  
6.0.1
  - update readme.md

6.0.0
  - breaking change: moved comment and clientId arguments from MetaApiConnection trade methods to options argument
  - added magic trade option to let you specify distinct magic number (expert advisor id) on each trade
  - added manualTrades field to account model so that it is possible to configure if MetaApi should place manual trades on the account
  - prepare MetatraderAccountApi class for upcoming breaking change in the API
  - added pagination and more filters to getAccounts API
  - added slippage option to trades
  - breaking change: rename close_position_by_symbol -> close_position**s**_by_symbol
  - added fillingModes to symbol specification
  - added executionMode to symbol specification
  - added logic to throw an exception if streaming API is invoked in automatic synchronization mode
  - added code samples for created account
  - save history on disk

4.0.0
  - add fields to trade result to match upcoming MetaApi contract
  - breaking change: throw TradeException in case of trade error
  - rename trade response fields so that they are more meaningful

3.0.0
  - improved account connection stability
  - added platform field to MetatraderAccountInformation model
  - breaking change: changed synchronize and waitSynchronized API to allow for unique synchronization id to be able to track when the synchronization is complete in situation when other clients have also requested a concurrent synchronization on the account
  - breaking change: changed default wait interval to 1s in wait* methods
2.0.0
  - breaking change: removed volume as an argument from a modifyOrder function
  - mark account as disconnected if there is no status notification for a long time
  - increased websocket client stability
  - added websocket and http client timeouts
  - improved account connection stability
1.1.4
  - increased synchronization speed
  - fixed connection stability issue during initial synchronization
1.1.3
  - initial release, version is set to be in sync with other SDKs