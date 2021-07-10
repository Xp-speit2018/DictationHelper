# -*- coding:utf-8 -*-
#
# 
#
# author : hantjscnxp@outlook.com
#
# Requirements:
# |      name       |       version      |
# |     ffmpeg      |  20200603-b6d7c4c  |
# |    websocket    |       0.2.1        |
#
# Reference Document:  
#   https://www.xfyun.cn/doc/asr/voicedictation/API.html#%E6%8E%A5%E5%8F%A3%E8%B0%83%E7%94%A8%E6%B5%81%E7%A8%8B
#   http://xfyun-doc.ufile.ucloud.com.cn/1567133454542862/iat_ws_python3_demo.zip
#   https://www.xfyun.cn/doc/asr/voicedictation/Audio.html
#   https://ffmpeg.org/ffmpeg.html#Main-options
#   
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
import base64
import datetime
import hashlib
import hmac
import json
import logging
import os
import re
import time
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websocket

import _thread as thread

APPID      = '5ed70bb6'
APIKEY     = '52eaabd1ae9eceeb2e924ef961cc5270'
APISECRET  = 'acc594bbdd6b600eb9442483e8d77b2f'
STREAMPATH = r'test.mp4'
LANGUAGE   = 'fr_fr' # zh_cn, en_us, fr_fr



class WebSocketParam:
    def __init__(self,APPID,APIKey,APISecret,AudioFile,language):
        self.APPID     = APPID
        self.APIKey    = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile
        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {
            "language" : language, 
            "domain"   : "iat",    # iat(日常用语), medical(医疗领域)
            "accent"  : "mandarin"
        }
        
        # 接口鉴权
        self.signature = {
            "host"          : None,
            "date"          : None,
            "authorization" : None
        }

            # host
        if language == "zh_cn" or language == "en_us":
            self.url = "wss://iat-api.xfyun.cn/v2/iat"
            self.signature["host"] = "ws-api.xfyun.cn"
        else:
            self.url = "wss://iat-niche-api.xfyun.cn/v2/iat"
            self.signature["host"] = "iat-niche-api.xfyun.cn"

            # date, RFC1123-formatted
        now  = datetime.datetime.now()
        date = format_date_time(mktime(now.timetuple())) 
        self.signature["date"] = date

            # authorizaiton, base64-encoded
        signature_origin =  "host: " + self.signature["host"] + "\n"
        signature_origin += "date: " + self.signature["date"] + "\n"
        signature_origin += "GET "   + "/v2/iat "             + "HTTP/1.1"
        signature_sha    =  hmac.new(
            self.APISecret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
            ).digest()
        signature_sha    =  base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorizaiton_origin = 'api_key="{}",'.format(self.APIKey) \
                             + 'algorithm="hmac-sha256",' \
                             + 'headers="host date request-line",' \
                             + 'signature="{}"'.format(signature_sha)
        authorization    =  base64.b64encode(authorizaiton_origin.encode('utf-8')).decode(encoding='utf-8')
        self.signature["authorization"] = authorization

        self.url += '?'
        self.url += urlencode(self.signature)
def ffCommand(exe=r'ffmpeg',input=None,output=None,params={}):
    '''
    生成ffmpeg命令行命令。
    exe   : ffmpeg, ffprobe
    input : test.pcm 
    可选关键字参数（本脚本使用的部分）：
        ffprobe:
                Key     :      Example Value
            loglevel    : quiet, error, fatal, debug, verbose
            show_format : ''
            
        ffmpeg:
                Key :  Example Value
            y       :  ''                    #直接覆盖输出文件
            acodec  :  pcm_s16le, copy       #解码器
            f       :  s16le                 #文件格式
            ac      :  1                     #通道数
            ar      :  16000                 #采样率
            ss      :  00:00:00              #开始时间
            t       ： 00:01:00              #持续时间
            vn      :  ''                    #禁用视频
    '''
    command  = r''
    command += exe + r' '

    if exe == r'ffprobe':
        for key,value in params.items():
            command += r'-{} {} '.format(key,value)
        command += input
    elif exe == r'ffmpeg':
        if not output:
            raise ValueError('ffmpeg需要输出文件')
        command += r'-i {} '.format(input)
        for key,value in params.items():
            command += r'-{} {} '.format(key,value)
        command += output
    else:
        raise KeyError('程序名错误')
    
    return command

def split(inputFile):
    '''
    将输入流剪切为时长1min的片段并转码为合适格式
    '''
    def timeFormatter(duration):
        '''
        example: 70(s) ==> 00:01:10
        '''
        second = duration
        minute = 0
        hour   = 0
        while second >= 60:
            second -= 60
            minute += 1
        while minute >= 60:
            minute -= 60
            hour   += 1
        if hour >= 60:
            raise ValueError('stream duration exceeds maximum')
        return(r'{}:{}:{}'.format(hour,minute,second))

    command = ffCommand(
        exe    = 'ffprobe',
        input  = inputFile,
        params = {
            'loglevel'    : 'quiet',
            'show_format' : ''
        }
    )
    f = os.popen(command)
    pattern = r'duration=(.+)'
    for line in f.readlines():
        line = line.strip('\n')
        print(line)
        matchObj = re.match(pattern,line)
        if matchObj:
            duration = float(matchObj.group(1))
    episodeNumber  = int(duration // 60)
    episodeNumber += 1

    res = []        
    for n in range(episodeNumber):
        command = ffCommand(
            exe    = 'ffmpeg',
            input  = inputFile,
            output = r'./tmp/temp{}.pcm'.format(n),
            params = {
                'y'      : '',
                'acodec' : 'pcm_s16le',
                'f'      : 's16le',
                'ac'     : '1',
                'ar'     : '16000',
                'ss'     : timeFormatter(n*60),
                't'      : '00:01:00',
                'vn'     : ''
            }
        )
        f = os.popen(command).read() 
        #print(f)
        res.append(r'./tmp/temp{}.pcm'.format(n))

    return res 

# WebSocketApp的四个参数on_message, on_error, on_close, on_open
def on_message(ws,message):
    '''
    收到websocket消息的处理
    '''
    try:
        code = json.loads(message)["code"]
        if code == 0:
            data = json.loads(message)["data"]["result"]["ws"]
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            print(result)
        else:
            errMsg = json.loads(message)["message"]
            print('WEBSOCKET MESSAGE : return code {},\n{}'.format(code,errMsg))
    except Exception as e:
        print("WEBSOCKET MESSAGE: "+e)

def on_error(ws,error):
    '''
    收到websocket错误的处理
    '''
    print('WEBSOCKET ERROR : '+error)

def on_close(ws):
    '''
    收到websocket关闭的处理
    '''
    #print('WEBSOCKET CLOSE : WebSocket closed.')
    pass

def on_open(ws):
    '''
    收到websocket连接建立的处理 
    '''
    FIRST_FRAME     = 0
    CONTINUE_FRAME  = 1
    LAST_FRAME      = 2

    frameSize = 8000
    intervel  = 0.04
    wsParam   = ws.param
    def run(*args):
        status    = FIRST_FRAME

        with open(wsParam.AudioFile,'rb') as fp:
            while True:
                buffer = fp.read(frameSize)
                if not buffer:
                    status = LAST_FRAME

                if status == FIRST_FRAME:
                    request = {
                        "common"   : wsParam.CommonArgs,
                        "business" : wsParam.BusinessArgs,
                        "data"     : {
                            "status"  : FIRST_FRAME,
                            "format"  : "audio/L16;rate=16000",
                            "audio"   : str(base64.b64encode(buffer),'utf-8'),
                            "encoding": "raw"
                        }
                    }
                    ws.send(json.dumps(request))
                    status = CONTINUE_FRAME

                elif status == CONTINUE_FRAME:
                    request = {
                        "data"    : {
                            "status"  : CONTINUE_FRAME,
                            "format"  : "audio/L16;rate=16000",
                            "audio"   : str(base64.b64encode(buffer),'utf-8'),
                            "encoding": "raw"
                        }
                    }
                    ws.send(json.dumps(request))
                    
                elif status == LAST_FRAME:
                    request = {
                        "data"    : {
                            "status"  : LAST_FRAME,
                            "format"  : "audio/L16;rate=16000",
                            "audio"   : str(base64.b64encode(buffer),'utf-8'),
                            "encoding": "raw"
                        }
                    }
                    ws.send(json.dumps(request))
                    time.sleep(1)
                    break
                time.sleep(intervel)
        ws.close()
    
    thread.start_new_thread(run,())

def main():
    audios = split(STREAMPATH)
    for audio in audios:
        wsParam = WebSocketParam(
            APPID     = APPID,
            APIKey    = APIKEY,
            APISecret = APISECRET,
            AudioFile = audio,
            language  = LANGUAGE
        )
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(
            wsParam.url,
            on_message = on_message,
            on_error   = on_error,
            on_close   = on_close,
            on_open    = on_open
        )
        ws.param = wsParam
        ws.run_forever()

if __name__ == "__main__":
    main()
