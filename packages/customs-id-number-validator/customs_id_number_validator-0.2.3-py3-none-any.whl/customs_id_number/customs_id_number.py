# /package/customs_id_number.py
import configparser
from typing import List
import requests
import xml.etree.ElementTree as ET
from urllib import parse

config = configparser.ConfigParser()
config.read('unipass.ini')
UNIPASS_API_KEY = config['DEFAULT']['UNIPASS_API_KEY']
DEFAULT_PHONE_NUMBER = "010-0000-0000"


def removeHyphen(phoneNumber: str):
    return phoneNumber.replace("-", "")


def addHyphen(phoneNumber: str):
    if len(phoneNumber) > 9:
        phoneNumber = removeHyphen(phoneNumber)
        phoneNumWithHyphen = f"{phoneNumber[0:-8]}-{phoneNumber[-8:-4]}-{phoneNumber[-4:]}"
        # if the phone number has 10 digits and starts with 01
        if phoneNumber[0:-8] == "01":
            phoneNumWithHyphen = f"{phoneNumber[0:-7]}-{phoneNumber[-7:-4]}-{phoneNumber[-4:]}"

        return phoneNumWithHyphen
    return phoneNumber


def api_request(customsIdNumber: str, name: str, phone: str):
    errors = []
    if len(name) < 2:
        errors.append('납세의무자 성명은(는) 필수입력입니다.')
    if len(phone) < 9:
        errors.append('납세의무자 휴대전화번호은(는) 필수입력입니다.')
    if len(errors) > 0:
        return {'success': False, 'errors': errors}
    requestURL = f'https://unipass.customs.go.kr:38010/ext/rest/persEcmQry/retrievePersEcm?crkyCn={UNIPASS_API_KEY}&persEcm={customsIdNumber}&pltxNm={parse.quote(name)}&cralTelno={removeHyphen(phone)}'
    try:
        response = requests.get(requestURL)
    except Exception as e:
        str(e)
    response_element = ET.fromstring(response.text)
    resultString = response_element.find('tCnt').text
    errors = []
    if resultString == '1':
        return {'success': True, 'errors': []}
    else:
        for reason in response_element.findall(
                'persEcmQryRtnErrInfoVo'):
            errors.append(reason.find('errMsgCn').text)
        return {'success': False, 'errors': errors}


def validate(customsIdNumber: str, names: List[str], phones: List[str]):
    finalName = names[0]
    finalPhone = phones[0]
    if len(customsIdNumber) != 13:
        return {'success': False, 'customsIdNumber': customsIdNumber, 'name': finalName, 'phone': addHyphen(finalPhone), 'errors': ['납세의무자 개인통관고유부호가 존재하지 않습니다.', '납세의무자의 휴대전화번호 확인이 불가능하기 때문에 재확인이 필요 합니다.']}
    result = {}
    for name in names:
        for phone in phones:
            if phone == "":
                phone = DEFAULT_PHONE_NUMBER
                result = api_request(customsIdNumber, name,
                                     phone)
            else:
                result = api_request(customsIdNumber, name, phone)
            if result['success']:
                return {'success': True, 'customsIdNumber': customsIdNumber, 'name': name, 'phone': addHyphen(phone), 'errors': result['errors']}
            else:
                # 입력된 성명 중에 개인통관부호에 등록된 명의와 일치된 이름이 없을 경우 가장 우선으로 입력된 2글자 이상인 이름이 finalName으로 결정된다.
                if '성명' not in ' '.join(result['errors']) or len(finalName) < 2:
                    finalName = name
                # 입력된 번호 중에 개인통관부호에 등록된 번호와 일치된 휴대전화번호가 없을 경우 가장 우선으로 입력된 01로 시작하는 휴대폰 번호가 finalPhone으로 결정된다.
                if '휴대전화번호' not in ' '.join(result['errors']) or (not finalPhone.startswith('01') and phone.startswith('01')):
                    if phone is not DEFAULT_PHONE_NUMBER:
                        finalPhone = phone
    result = api_request(customsIdNumber, finalName, finalPhone)
    if finalPhone == DEFAULT_PHONE_NUMBER:
        result['errors'].append('납세의무자 휴대전화번호은(는) 필수입력입니다.')
    else:
        if '존재' in ' '.join(result['errors']):
            result['errors'].append('납세의무자의 휴대전화번호 확인이 불가능하기 때문에 재확인이 필요 합니다.')
    return {'success': False, 'customsIdNumber': customsIdNumber, 'name': finalName, 'phone': addHyphen(finalPhone), 'errors': result['errors']}
