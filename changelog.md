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