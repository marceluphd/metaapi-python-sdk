from .metatraderAccountModel import MetatraderAccountModel


class InvalidSynchronizationModeException(Exception):
    """Exception which indicates that MetaApi MetaTrader account was created with synchronization mode which does not
    support streaming API. See https://metaapi.cloud/docs/client/websocket/synchronizationMode/ for more details."""

    def __init__(self, account: MetatraderAccountModel):
        """Inits the exception

        Args:
            account: MetaTrader account.
        """
        super().__init__(f'Your account {account.name} ({account.id}) was created with {account.synchronization_mode} '
                         f'synchronization mode which does not support the streaming API. Thus please update your '
                         f'account to \'user\' synchronization mode if to invoke this method. See '
                         f'https://metaapi.cloud/docs/client/websocket/synchronizationMode/ for more details.')
