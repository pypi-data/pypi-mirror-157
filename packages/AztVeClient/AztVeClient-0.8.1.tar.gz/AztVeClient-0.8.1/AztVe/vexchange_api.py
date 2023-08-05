#!/bin/env python
# -*- coding: UTF-8 -*-
import queue, threading, zmq, uuid
import sys
import time
from abc import ABC, ABCMeta
from .protobufs import MsgType_pb2 as MsgTypeProto, Message_pb2 as MsgProto, EnumType_pb2 as EnumProto
from .protobufs import UnitedMessage_pb2 as UnitMsgProto
from .structs import spi_struct
from .tools import azt_logger, azt_errors


class CVexchangeTraderSpi(ABC):
    api = None

    def onRegisterReq(self, msg):
        pass

    def onUserLoginReq(self, msg):
        pass

    def onUserInfoQryReq(self, msg):
        pass

    def onAccDepositReq(self, msg):
        pass

    def onTradingAccQryReq(self, msg):
        pass

    def onQueryOrdersReq(self, msg):
        pass

    def onQueryTradesReq(self, msg):
        pass

    def onQueryPositionsReq(self, msg):
        pass

    def onQueryHistoryOrdersReq(self, msg):
        pass

    def onQueryHistoryTradesReq(self, msg):
        pass

    def onOrderReport(self, msg):
        pass

    def onTradeReport(self, msg):
        pass

    def onCancelOrderReject(self, msg):
        pass

    def onQueryHistoryAccReq(self, msg):
        pass

    def onQueryHistoryDepositReq(self, msg):
        pass


class CVexchangeTraderApi:
    def __init__(self):
        # 服务器地址
        self._server_addr = None
        # 设置默认的spi
        self.spi = CVexchangeTraderSpi()
        # 设置zmq
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.DEALER)
        # 设置接收线程
        self.__thread_report_recv = threading.Thread(target=self.__report_recv)
        self.__thread_report_recv.setDaemon(True)
        # 设置心跳线程
        self.__thread_heart_beat = threading.Thread(target=self.__heart_beat)
        self.__thread_heart_beat.setDaemon(True)
        # 设置信号
        self._logined = False
        self.__closed = False
        # 保存登录信息
        # self._login_info = None
        # 同步管道
        self._queue_map = dict()
        # # 设置client_ref标识
        # self._client_ref = str(uuid.uuid4())
        # 设置策略ID
        self._sender_user = None
        # 心跳
        self._heart_beat_times = 3  # 心跳次数
        self._heart_beat_count = self._heart_beat_times  # 心跳倒数
        self._heart_beat_interval = 5  # 心跳间隔时间，5秒
        self._heart_beat_req = self.__init_heart_beat_req()  # 心跳请求

    def Init(self, server_addr: str, spi=None, hb_times: int = None, hb_interval: int = None):
        # 设置服务器地址
        if not server_addr.startswith("tcp"):
            server_addr = f"tcp://{server_addr}"
        self._server_addr = server_addr
        # 设置spi
        if spi is not None:
            if spi.__class__ is ABCMeta:
                spi = spi()
            self.spi = spi
            self.spi.api = self
        if hb_times is not None:
            self._heart_beat_times = hb_times
            self._heart_beat_count = hb_times
        if hb_interval is not None and hb_interval >= 3:
            self._heart_beat_interval = hb_interval

        # 连接服务器
        azt_logger.log(f"开始连接服务器 - {self._server_addr}")
        self.__socket.connect(self._server_addr)
        # 启动监听线程
        self.__thread_report_recv.start()

        # 发送心跳请求，确认服务器已连接
        # self.__queue_subscribe("heart_beat")  # 建立临时心跳接收队列
        self.__send_heart_beat()  # 发送一次心跳请求
        ret_heart_beat = self._queue_sync_get(name="heart_beat", timeout=self._heart_beat_interval)
        if ret_heart_beat is None:
            return azt_errors.ConnectedFailed(f"服务器 - {self._server_addr} - 连接失败！")
        azt_logger.log(f"已成功连接服务器 - {self._server_addr}!")
        # 开启心跳线程
        self.__thread_heart_beat.start()

    # ----------------------------------------------------------------------------------------
    def Join(self, timeout: int = None):
        self.__thread_report_recv.join(timeout=timeout)

    # ------ RegisterReq ------
    def RegisterReq(self, req_msg: MsgProto.RegisterReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KVexchangeMsgID_RegisterReq))

    # ------ LoginReq ------
    def UserLoginReq(self, req_msg: MsgProto.LoginReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KVexchangeMsgID_LoginReq))

    # ------ LogoutReq ------
    def UserLogoutReq(self, req_msg: MsgProto.LogoutReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KVexchangeMsgID_LogoutReq))

    # ------ UserInfoQryReq ------
    def UserInfoQryReq(self, req_msg: MsgProto.UserInfoQryReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KVexchangeMsgID_UserInfoQryReq))

    # ------ AccDepositReq ------
    def AccDepositReq(self, req_msg: MsgProto.AccDepositReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KTradeReqType_AccDepositReq))

    # ------ TradingAccQryReq ------
    def TradingAccQryReq(self, req_msg: MsgProto.TradingAccQryReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KTradeReqType_TradingAccQryReq))

    # ------ QueryOrdersReq ------
    def QueryOrdersReq(self, req_msg: MsgProto.QueryOrdersReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KQueryOrdersReq))

    # ------ QueryTradesReq ------
    def QueryTradesReq(self, req_msg: MsgProto.QueryTradesReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KQueryTradesReq))

    # ------ QueryPositionsReq ------
    def QueryPositionsReq(self, req_msg: MsgProto.QueryPositionsReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KQueryPositionsReq))

    # ------ QueryHistoryOrdersReq ------
    def QueryHistoryOrdersReq(self, req_msg: MsgProto.QueryHistoryOrdersReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KQueryHistoryOrdersReq))

    # ------ QueryHistoryTradesReq ------
    def QueryHistoryTradesReq(self, req_msg: MsgProto.QueryHistoryTradesReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KQueryHistoryTradesReq))

    def QueryHistoryAccReq(self, req_msg: MsgProto.QryHisAccReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KTradeReqType_QryHisAccReq))

    def QueryHistoryDepositReq(self, req_msg: MsgProto.QryHisDepositReq):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KTradeReqType_QryHisDepositReq))

    # ------ PlaceOrder ------
    def PlaceOrder(self, req_msg: MsgProto.PlaceOrder):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KTradeReqType_PlaceOrder))

    # ------ CancelOrder ------
    def CancelOrder(self, req_msg: MsgProto.CancelOrder):
        self.__socket.send(self.__gen_unit_msg(req_msg, EnumProto.KTradeReqType_CancelOrder))

    def _close(self):
        self.__closed = True
        try:
            self.__socket.close()
            self.__context.destroy()
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            raise e

    @staticmethod
    def _gen_client_ref():
        return str(uuid.uuid4())

    def _queue_sync_get(self, frame=1, name=None, timeout=None, exec_func=None, f_args=(), f_kwargs: dict = None):
        f_name = name or ("on" + sys._getframe(frame).f_code.co_name)
        self.__queue_subscribe(f_name)
        if exec_func is not None:
            if f_kwargs is None:
                f_kwargs = {}
            exec_func(*f_args, **f_kwargs)
        ret = None
        try:
            ret = self._queue_map[f_name].get(timeout=timeout)
        except queue.Empty:
            pass
        self.__queue_unsubscribe(f_name)
        return ret

    @staticmethod
    def __init_heart_beat_req():
        unit_msg = UnitMsgProto.UnitedMessage()
        unit_msg.msg_type = MsgTypeProto.KMsgType_Exchange_Req
        unit_msg.msg_id = EnumProto.KVexchangeMsgID_HeartBeatReq
        unit_msg.msg_body.Pack(MsgProto.HeartBeatReq())
        return unit_msg

    @staticmethod
    def __gen_unit_msg(msg, msg_id, msg_type=MsgTypeProto.KMsgType_Exchange_Req):
        unit_msg = UnitMsgProto.UnitedMessage(msg_type=msg_type, msg_id=msg_id)
        unit_msg.msg_body.Pack(msg)
        return unit_msg.SerializeToString()

    def __queue_subscribe(self, spi_name):
        # azt_logger.debug("注册回调：", spi_name)
        self._queue_map[spi_name] = queue.Queue()

    def __queue_unsubscribe(self, spi_name):
        if spi_name in self._queue_map:
            self._queue_map.pop(spi_name)
            # azt_logger.debug("注销回调：", spi_name)

    def __send_heart_beat(self):
        self.__socket.send(self._heart_beat_req.SerializeToString())

    def __heart_beat(self):
        azt_logger.log("心跳线程启动成功！")
        time.sleep(self._heart_beat_interval)
        while self._heart_beat_count > 0:
            self._heart_beat_count -= 1
            self.__send_heart_beat()
            time.sleep(self._heart_beat_interval)
            if self._heart_beat_count < self._heart_beat_times:
                azt_logger.warning(
                    f"心跳接收异常！正在确认心跳...{self._heart_beat_times - self._heart_beat_count + 1}/{self._heart_beat_times}")
        # if not self.__closed:

        azt_logger.error("与服务器连接已中断！")
        self._close()
        # raise azt_errors.ConnectedBroken

    def __report_recv(self):  # 加__作为私有方法
        poller = zmq.Poller()
        poller.register(self.__socket, zmq.POLLIN)
        while True:
            try:
                events = poller.poll()  # poll模式是用于多个socket场景的,可以避免某个socket的接收阻塞问题,这里用不用都行
            except zmq.error.ZMQError as zmqerror:
                if self.__closed:
                    break
                raise zmqerror
            except Exception as e:
                raise e

            if self.__socket in dict(events):
                recv_msg = self.__socket.recv()
                unit_msg = UnitMsgProto.UnitedMessage()
                unit_msg.ParseFromString(recv_msg)
                self.__report_handel(unit_msg)

    def __report_handel(self, unit_msg):
        azt_logger.debug(f"收到消息：{unit_msg.msg_type}-{unit_msg.msg_id}")
        if unit_msg.msg_type != MsgTypeProto.KMsgType_Exchange_Rsp:
            return

        if unit_msg.msg_id == EnumProto.KVexchangeMsgID_RegisterAck:
            msg = MsgProto.RegisterAck()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            cbmsg = spi_struct.RegisterAck.__proto2py__(msg)
            self.spi.onRegisterReq(cbmsg)
            if "onRegisterReq" in self._queue_map:
                self._queue_map["onRegisterReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KVexchangeMsgID_LoginAck:
            self._logined = True
            msg = MsgProto.LoginAck()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            cbmsg = spi_struct.LoginAck.__proto2py__(msg)
            # self._login_info = cbmsg
            self.spi.onUserLoginReq(cbmsg)
            if "onUserLoginReq" in self._queue_map:
                self._queue_map["onUserLoginReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KVexchangeMsgID_UserInfoQryAck:
            msg = MsgProto.UserRegisterInfo()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            cbmsg = spi_struct.UserRegisterInfo.__proto2py__(msg)
            self.spi.onUserInfoQryReq(cbmsg)
            if "onUserInfoQryReq" in self._queue_map:
                self._queue_map["onUserInfoQryReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KTradeReqType_AccDepositAck:
            msg = MsgProto.AccDepositAck()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            cbmsg = spi_struct.AccDepositAck.__proto2py__(msg)
            self.spi.onAccDepositReq(cbmsg)
            if "onAccDepositReq" in self._queue_map:
                self._queue_map["onAccDepositReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KTradeReqType_TradingAccQryAck:
            msg = MsgProto.AccMargin()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            cbmsg = spi_struct.AccMargin.__proto2py__(msg)
            self.spi.onTradingAccQryReq(cbmsg)
            if "onTradingAccQryReq" in self._queue_map:
                self._queue_map["onTradingAccQryReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KQueryOrdersAck:
            msg = MsgProto.QueryOrdersAck()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug("unit_msg_proto：")
            # azt_logger.debug(unit_msg)
            # azt_logger.debug("QueryOrdersAck_proto:")
            #
            # azt_logger.debug(msg)
            cbmsg = spi_struct.QueryOrdersAck.__proto2py__(msg)
            self.spi.onQueryOrdersReq(cbmsg)
            if "onQueryOrdersReq" in self._queue_map:
                self._queue_map["onQueryOrdersReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KQueryTradesAck:
            msg = MsgProto.QueryTradesAck()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            cbmsg = spi_struct.QueryTradesAck.__proto2py__(msg)
            self.spi.onQueryTradesReq(cbmsg)
            if "onQueryTradesReq" in self._queue_map:
                self._queue_map["onQueryTradesReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KQueryPositionsAck:
            msg = MsgProto.QueryPositionsAck()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            cbmsg = spi_struct.QueryPositionsAck.__proto2py__(msg)
            self.spi.onQueryPositionsReq(cbmsg)
            if "onQueryPositionsReq" in self._queue_map:
                self._queue_map["onQueryPositionsReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KQueryHistoryOrdersAck:
            msg = MsgProto.QueryOrdersAck()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(unit_msg, msg)
            cbmsg = spi_struct.QueryOrdersAck.__proto2py__(msg)
            self.spi.onQueryHistoryOrdersReq(cbmsg)
            if "onQueryHistoryOrdersReq" in self._queue_map:
                self._queue_map["onQueryHistoryOrdersReq"].put(cbmsg, block=False)

        elif unit_msg.msg_id == EnumProto.KQueryHistoryTradesAck:
            msg = MsgProto.QueryTradesAck()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(unit_msg, msg)
            cbmsg = spi_struct.QueryTradesAck.__proto2py__(msg)
            self.spi.onQueryHistoryTradesReq(cbmsg)
            if "onQueryHistoryTradesReq" in self._queue_map:
                self._queue_map["onQueryHistoryTradesReq"].put(cbmsg, block=False)
        elif unit_msg.msg_id == EnumProto.KTradeReqType_QryHisAccAck:
            msg = MsgProto.QryHisAccAck()
            unit_msg.msg_body.Unpack(msg)
            cbmsg = spi_struct.QryHisAccAck.__proto2py__(msg)
            self.spi.onQueryHistoryAccReq(cbmsg)
            if "onQueryHistoryAccReq" in self._queue_map:
                self._queue_map["onQueryHistoryAccReq"].put(cbmsg, block=False)
        elif unit_msg.msg_id == EnumProto.KTradeReqType_QryHisDepositAck:
            msg = MsgProto.QryHisDepositAck()
            unit_msg.msg_body.Unpack(msg)
            cbmsg = spi_struct.QryHisDepositAck.__proto2py__(msg)
            self.spi.onQueryHistoryDepositReq(cbmsg)
            if "onQueryHistoryDepositReq" in self._queue_map:
                self._queue_map["onQueryHistoryDepositReq"].put(cbmsg, block=False)
        # ----------------------------------------------------------
        elif unit_msg.msg_id == EnumProto.KTradeRspType_OrdStatusReport:
            msg = MsgProto.OrdReport()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            self.spi.onOrderReport(spi_struct.OrdReport.__proto2py__(msg))

        elif unit_msg.msg_id == EnumProto.KTradeReqType_ExecReport:
            msg = MsgProto.TradeReport()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            self.spi.onTradeReport(spi_struct.TradeReport.__proto2py__(msg))

        elif unit_msg.msg_id == EnumProto.KTradeReqType_RejectCancelReport:
            msg = MsgProto.CancelOrderReject()
            unit_msg.msg_body.Unpack(msg)
            # azt_logger.debug(msg)
            self.spi.onCancelOrderReject(spi_struct.CancelOrderReject.__proto2py__(msg))
        elif unit_msg.msg_id == EnumProto.KVexchangeMsgID_HeartBeatAck:
            self._heart_beat_count = self._heart_beat_times
            if "heart_beat" in self._queue_map:
                self._queue_map["heart_beat"].put(True, block=False)
        else:
            azt_logger.warning("Unkown recv msg msg_id!")
