import datetime
from .vexchange_api import *
from .structs import api_struct
from .tools import azt_errors

_AllowOrderTimeSHSE_SZSE = (
    datetime.time(9, 30, 0), datetime.time(11, 30, 0),
    datetime.time(13, 0), datetime.time(20, 0),
)


class AztVeApiOld(CVexchangeTraderApi):
    def _sync_async_switch(self, sync=False, timeout=None, exec_func=None, f_args=(), f_kwargs=None):
        if sync:
            return self._queue_sync_get(frame=2, timeout=timeout, exec_func=exec_func, f_args=f_args, f_kwargs=f_kwargs)
        else:
            exec_func(*f_args, **f_kwargs)

    # ------ RegisterReq ------
    def RegisterReq(self, req: api_struct.RegisterReq, sync=False, timeout=3):
        return self._sync_async_switch(sync, timeout, super().RegisterReq, (req.__py2proto__(),))

    # ------ LoginReq ------
    def UserLoginReq(self, req: api_struct.LoginReq, sync=False, timeout=3):
        self._sender_user = req.account
        return self._sync_async_switch(sync, timeout, super().UserLoginReq, (req.__py2proto__(),))

    # ------ LogoutReq ------
    def UserLogoutReq(self, req: api_struct.LogoutReq):
        self._verify_logined()
        super().UserLogoutReq(req.__py2proto__())
        self._close()
        azt_logger.log("已退出登录，欢迎下次使用！")

    # ------ UserInfoQryReq ------
    def UserInfoQryReq(self, req: api_struct.UserInfoQryReq, sync=False, timeout=3):
        return self._sync_async_switch(sync, timeout, super().UserInfoQryReq, (req.__py2proto__(),))

    # ------ AccDepositReq ------
    def AccDepositReq(self, req: api_struct.AccDepositReq, sync=False, timeout=3):
        self._verify_logined()
        req.client_ref = self._gen_client_ref()
        req.sender_user = self._sender_user
        req.send_time = datetime.datetime.now()
        return self._sync_async_switch(sync, timeout, super().AccDepositReq, (req.__py2proto__(),))

    # ------ TradingAccQryReq ------
    def TradingAccQryReq(self, req: api_struct.TradingAccQryReq, sync=False, timeout=3):
        self._verify_logined()
        return self._sync_async_switch(sync, timeout, super().TradingAccQryReq, (req.__py2proto__(),))

    # ------ QueryOrdersReq ------
    def QueryOrdersReq(self, req: api_struct.QueryOrdersReq, sync=False, timeout=3):
        self._verify_logined()
        return self._sync_async_switch(sync, timeout, super().QueryOrdersReq, (req.__py2proto__(),))

    # ------ QueryTradesReq ------
    def QueryTradesReq(self, req: api_struct.QueryTradesReq, sync=False, timeout=3):
        self._verify_logined()
        return self._sync_async_switch(sync, timeout, super().QueryTradesReq, (req.__py2proto__(),))

    # ------ QueryPositionsReq ------
    def QueryPositionsReq(self, req: api_struct.QueryPositionsReq, sync=False, timeout=3):
        self._verify_logined()
        return self._sync_async_switch(sync, timeout, super().QueryPositionsReq, (req.__py2proto__(),))

    # ------ QueryHistoryOrdersReq ------
    def QueryHistoryOrdersReq(self, req: api_struct.QueryHistoryOrdersReq, sync=False, timeout=3):
        self._verify_logined()
        req_proto = req.__py2proto__()
        azt_logger.debug("发送参数：")
        azt_logger.debug(req_proto)
        return self._sync_async_switch(sync, timeout, super().QueryHistoryOrdersReq, (req_proto,))

    # ------ QueryHistoryTradesReq ------
    def QueryHistoryTradesReq(self, req: api_struct.QueryHistoryTradesReq, sync=False, timeout=3):
        self._verify_logined()
        return self._sync_async_switch(sync, timeout, super().QueryHistoryTradesReq, (req.__py2proto__(),))

    def QueryHistoryAccReq(self, req: api_struct.QryHisAccReq, sync=False, timeout=3):
        return self._sync_async_switch(sync, timeout, super().QueryHistoryAccReq, (req.__py2proto__(),))

    def QueryHistoryDepositReq(self, req: api_struct.QryHisDepositReq, sync=False, timeout=None):
        return self._sync_async_switch(sync, timeout, super().QueryHistoryDepositReq, (req.__py2proto__(),))

    # ------ PlaceOrder ------
    def PlaceOrder(self, req: api_struct.PlaceOrder):
        self._verify_logined()
        req.client_ref = self._gen_client_ref()
        req.sender_user = self._sender_user
        now = datetime.datetime.now()
        now_time = now.time()
        if _AllowOrderTimeSHSE_SZSE[0] <= now_time <= _AllowOrderTimeSHSE_SZSE[1] or \
                _AllowOrderTimeSHSE_SZSE[2] <= now_time <= _AllowOrderTimeSHSE_SZSE[3]:
            req.send_time = now
            super().PlaceOrder(req.__py2proto__())
        else:
            raise azt_errors.NonTradingTimeError

    # ------ CancelOrder ------
    def CancelOrder(self, req: api_struct.CancelOrder):
        self._verify_logined()
        req.client_ref = self._gen_client_ref()
        req.sender_user = self._sender_user
        req.send_time = datetime.datetime.now()
        super().CancelOrder(req.__py2proto__())

    def _verify_logined(self):
        if not self._logined:
            self._close()
            raise azt_errors.NotLoginedError
