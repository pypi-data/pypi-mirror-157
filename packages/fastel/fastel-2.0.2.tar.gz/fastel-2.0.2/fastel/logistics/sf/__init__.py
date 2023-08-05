import json
import time
from typing import Any, Dict, List, Optional, Tuple

from requests import Response

from fastel.collections import get_site_config
from fastel.config import SdkConfig
from fastel.exceptions import APIException
from fastel.logistics.sf.cryptor import SFCryptor
from fastel.utils import requests


def sf_url() -> str:
    # if SdkConfig.stage in ["stg", "STG"]:
    #     return "http://api-ifsp.sit.sf.global"
    return "https://api-ifsp.sf.global"


def api_token() -> str:
    url = (
        sf_url()
        + f"/openapi/api/token?appKey={SdkConfig.sf_app_key}&appSecret={SdkConfig.sf_secret}"
    )
    resp: Response = requests.get(url)
    result = resp.json()
    if result["apiResultCode"] != "0":
        return ""
    result_data: Dict[str, Any] = result["apiResultData"]
    return result_data.get("accessToken", "")


def generate_headers(method: str = "IECS_CREATE_ORDER") -> Dict[str, Any]:
    timestamp = str(int(time.time()))
    headers = {
        "appKey": SdkConfig.sf_app_key,
        "token": api_token(),
        "timestamp": timestamp,
        "nonce": timestamp,
        "msgType": method,
    }
    return headers


def encrypt_data(
    data: Dict[str, Any], method: str = "IECS_CREATE_ORDER"
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    msg = json.dumps(data)
    headers = generate_headers(method)
    cryptor = SFCryptor(
        aes_key=SdkConfig.sf_aes_key,
        app_key=SdkConfig.sf_app_key,
        access_token=api_token(),
    )
    ret_code, xtml_encrypt, signature = cryptor.encrypt_msg(
        msg=msg, nonce=headers["nonce"], timestamp=headers["timestamp"]
    )
    if ret_code != 0:
        raise APIException(status_code=400, error="SF_Encrypt_Error", detail="")
    body = {"encrypt": xtml_encrypt}
    headers = {**generate_headers(), "signature": signature}
    return headers, body


def generate_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for item in items:
        data = {
            "name": item.get("name", ""),
            "unit": "個",
            "amount": float(item.get("amount", 1.0)),
            "currency": "NTD",
            "quantity": float(item.get("config", {}).get("qty", 1.0)),
            "originCountry": "TW",
        }
        result.append(data)
    return result


def create_logistics(
    order: Dict[str, Any], extra_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    url = sf_url() + f"/openapi/api/dispatch"
    default_sender_info = dict(
        SenderName="忻旅科技",
        SenderPhone="02-77295130",
        SenderZipCode="10361",
        SenderCellPhone="0900000000",
        SenderAddress="台北市大同區民權西路136號10樓之5",
    )
    sender_info: Dict[str, Any] = get_site_config(
        key="logistics_sender_info", default=default_sender_info
    )
    data = {
        "customerCode": SdkConfig.sf_merchant_id,
        "orderOperateType": 1,
        "customerOrderNo": order["order_id"],
        "interProductCode": extra_data.get("platform_code", "INT0053"),
        # 包裹數 *
        "parcelQuantity": 1,
        # 聲明價值 * order
        "declaredValue": order.get("amount", 0),
        # 包裹总计声明价值币种
        "declaredCurrency": "NTD",
        # 寄件方式 0: 服務點自寄或自行聯繫快遞員 1: 上門收件
        "pickupType": "1",
        # 上門區間預約時間 yyyy-MM-dd HH:mm 如果pickupType 為 1 則必填
        "pickupAppointTime": extra_data.get("pickup_time"),
        # 收件時區
        "pickupAppointTimeZone": "Asia/Taipei",
        # 運單備註 *
        "remark": extra_data.get("note", ""),
        # 付款方式
        "paymentInfo": {
            # 付款方式 1 寄方付， 2 收方付， 3 第三方付
            "payMethod": "3",
        },
        # 寄件人訊息
        "senderInfo": {
            # 寄件人名字
            "contact": sender_info.get("SenderName", ""),
            # 寄件國家/地區
            "country": "TW",
            # 郵編
            "postCode": sender_info.get("SenderZipCode", ""),
            # 州/省
            "regionFirst": "台灣省",
            # 城市
            "regionSecond": sender_info.get("SenderCity", "臺北市"),
            # 區
            "regionThird": sender_info.get("SenderDistrict", "大同區"),
            "address": sender_info.get("SenderAddress", ""),
            "email": sender_info.get("SenderEmail", ""),
            "telNo": sender_info.get("SenderPhone", ""),
        },
        # 收件人訊息
        "receiverInfo": {
            # 寄件人名字
            "contact": order.get("receiver_name", ""),
            # 寄件國家/地區
            "country": "TW",
            # 郵編
            "postCode": order.get("receiver_zip", ""),
            # 州/省
            "regionFirst": "台灣省",
            # 城市
            "regionSecond": order.get("receiver_city", ""),
            # 區
            "regionThird": order.get("receiver_district", ""),
            "address": order.get("receiver_address", ""),
            "email": order.get("receiver_email", ""),
            "phoneNo": order.get("receiver_phone", ""),
        },
        # 包裹訊息
        "parcelInfoList": generate_items(order.get("items", [])),
    }
    headers, body = encrypt_data(data=data, method="IUOP_CREATE_ORDER")
    resp: Response = requests.post(url, headers=headers, json=body)
    logistics_resp: Dict[str, Any] = resp.json()

    cryptor = SFCryptor(aes_key=SdkConfig.sf_aes_key, app_key=SdkConfig.sf_app_key)
    ret, result = cryptor.decrypt_msg(post_data=logistics_resp.get("apiResultData", ""))
    return result


def query_logistics(logistics_id: str) -> Optional[Dict[str, Any]]:
    url = sf_url() + f"/openapi/api/dispatch"
    data = {"customerCode": SdkConfig.sf_merchant_id, "sfWaybillNo": logistics_id}
    headers, body = encrypt_data(data=data, method="IUOP_QUERY_TRACK")
    resp: Response = requests.post(url, headers=headers, json=body)
    logistics_resp: Dict[str, Any] = resp.json()

    cryptor = SFCryptor(aes_key=SdkConfig.sf_aes_key, app_key=SdkConfig.sf_app_key)
    ret, result = cryptor.decrypt_msg(post_data=logistics_resp.get("apiResultData", ""))
    return result
