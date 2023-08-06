import os , sys , random 
try:
	import requests , user_agent , json , secrets , hashlib , urllib , uuid , re , mechanize , instaloader 
	from TSMRS import check
	from time import sleep
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
	os.system('pip install TSMRS')
class Dark():

		

	def Create(username,password,name):
		hosturl = "https://www.instagram.com/"
		createurl = "https://www.instagram.com/accounts/web_create_ajax/attempt/"
		ageurl = "https://www.instagram.com/web/consent/check_age_eligibility/"
		sendurl = "https://i.instagram.com/api/v1/accounts/send_verify_email/"
		checkcodeurl = "https://i.instagram.com/api/v1/accounts/check_confirmation_code/"
		createacc = "https://www.instagram.com/accounts/web_create_ajax/"
		session = requests.Session()
		session.headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36', 'Referer': hosturl}
		session.proxies = {'http': requests.get("https://gimmeproxy.com/api/getProxy").json()['curl']}
		reqB = session.get(hosturl)
		session.headers.update({'X-CSRFToken': reqB.cookies['csrftoken']})
		rem = requests.get("https://10minutemail.net/address.api.php")
		qwe=rem.json()['mail_get_mail'],rem.cookies['PHPSESSID']
		maile=qwe[0]
		mailss=qwe[1]
		
		data = {'enc_password':'#PWD_INSTAGRAM_BROWSER:0:&:'+password,'email':maile,'username':username,'first_name':name,'client_id':'','seamless_login_enabled':'1','opt_into_one_tap':'false',}
		reg1 = session.post(url=createurl,data=data,allow_redirects=True)
		if(reg1.json()['status'] == 'ok'):
			True
		else:
			
			return {"status": "username or password Error"}
		data2 = {'day':'2','month':'2','year':'1983',}
		reqA = session.post(url=ageurl,data=data2,allow_redirects=True)
		if(reqA.json()['status'] == 'ok'):
			True
		else:
			return {"status": "Error Send Date"}
		sendcode = session.post(url=sendurl,data={'device_id': '','email': maile},allow_redirects=True)
		if(sendcode.json()['status'] == 'ok'):
			True
		else:
			return {"status": "Error Send Code"}
		while 1:
			rei = requests.get("https://10minutemail.net/address.api.php",cookies={"PHPSESSID":mailss})
			inbox=rei.json()['mail_list'][0]['subject']
			if "Instagram" in inbox:
				code = inbox.split(" is")[0]
				True
				break	 
			else:
				True
				continue
		confirmation = session.post(url=checkcodeurl,data={'code': code,'device_id': '','email': maile})
		if confirmation.json()['status'] == "ok":
			signup_code = confirmation.json()['signup_code']
			True
			create = session.post(
				url=createacc,
				data={
'enc_password': '#PWD_INSTAGRAM_BROWSER:0:&:'+password,
'email': maile,
'username': username,
'first_name': name,
'month': '4',
'day': '4',
'year': '1963',
'client_id': '',
'seamless_login_enabled': '1',
'tos_version': 'row',
'force_sign_up_code': signup_code})
			if '"account_created": false' in create.text:
				return {"status": "Error Create Account"}
			else:
				return {"status": "Successful Create" , "username": username , "password": password , "name": name , "email": maile , "LibBY": "@J_W_2"}
		else:
			return {"status": "Error Get SignUp Code"}
	def email(domi):
		s = ["@gmail.com","@yahoo.com","@hotmail.com","@aol.com","@outlook.com"]
		domin="@"+domi+".com"
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
		data = req.replace('[','').replace(']','').split(',')
		for i in data:
			eail = i.replace('"','')
			ema = eail.split("@")[0]
			email = ema + domin
			return email
	def Login(username: str, password: str) -> str:
		header = {"User-Agent": "Mozilla/5.0 (Linux; Android 11; RMX3191) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36"}
		with requests.Session() as max:
			url_scrap = "https://www.instagram.com/"
			data = max.get(url_scrap, headers=header).content
			token = re.findall('{"config":{"csrf_token":"(.*)","viewer"', str(data))[0]
		
		headers = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
			"Host": "www.instagram.com",
			"X-CSRFToken": token,
			"X-Requested-With": "XMLHttpRequest",
			"Referer": "https://www.instagram.com/accounts/login/",
			"User-Agent": generate_user_agent(),}
		data = {
			"username": str(username),
			"enc_password": "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format(random.randint(1000000000, 9999999999), str(password)),
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
				return {'status':'Success','login':'true','sessionid':str(session)}
				
			elif ("checkpoint_url") in str(login):
				return {'status':'error','login':'checkpoint'}
				
			elif ("Please wait") in str(login):
				return {'status':'error','login':'blocked'}
				
			else:
				return {'status':'error','login':'error.username_or_password'}			
class check():
	def visa(card):
		url = "https://checker.visatk.com/ccn1/alien07.php"		
		headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
		'Connection':'keep-alive',
		'Content-Length': '57',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Cookie':'__gads=ID=42ac6c196f03a9b4-2279e5ef3fcd001d:T=1645035753:RT=1645035753:S=ALNI_MZL7kDSE4lwgNP0MHtSLy_PyyPW3w; PHPSESSID=tdsh3u2p5niangsvip3gvvbc12',
		'Host':'checker.visatk.com',
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
		'ajax':'1',
		'do':'check',
		'cclist':card}
		req = requests.post(url, headers=headers, data=data).text
		if '"error":0' in req:
		  	many = req.split("[Charge :<font color=green>")[1].split("</font>] [BIN:")[0]
		  	message = {'status':'Success','many':str(many),'Card':str(card)}
		  	return message

		else:
			return {"status": "error" , "Card": False}
	def gmail(email: str) -> str:
		url = 'https://android.clients.google.com/setup/checkavail'
		headers = {
		'Content-Length':'98',
		'Content-Type':'text/plain; charset=UTF-8',
		'Host':'android.clients.google.com',
		'Connection':'Keep-Alive',
		'user-agent':'GoogleLoginService/1.3(m0 JSS15J)',}
		data = json.dumps({
		'username':str(email),
		'version':'3',
		'firstName':'GDO_0',
		'lastName':'GDOTools' })
		res = requests.post(url,data=data,headers=headers)
		if res.json()['status'] == 'SUCCESS':
			return {'status':'Success','email':True}		

		else:			
			return {'status':'error','email':False}			
		
			
	def hotmail(email: str) -> str:
		url = "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=0&emailAddress="+str(email)+"&_=1604288577990"	
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
			return {'status':'Success','email':True}
		
		else:			
			return {'status':'error','email':False}
 
    
	def outlook(email: str) -> str:
		url = "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=0&emailAddress="+str(email)+"&_=1604288577990"	
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
			return {'status':'Success','email':True}
		
		else:
			return {'status':'error','email':False}
		
		
			
	def mailru(email: str) -> str:
		url = "https://account.mail.ru/api/v1/user/exists"		
		headers = {
		"User-Agent": str(generate_user_agent())}
		data = {'email': str(email)}
		res = requests.post(url, data=data, headers=headers)		
		if str(res.json()['body']['exists']) == False:
			return True
		
		else:
			return {'status':'error','email':False}		
		
		
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
		'user-agent': str(generate_user_agent()),}		
		data = {
	    'browser-fp-data': '{"language":"ar","colorDepth":24,"deviceMemory":4,"pixelRatio":1,"hardwareConcurrency":4,"timezoneOffset":-180,"timezone":"Asia/Riyadh","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"unknown","plugins":{"count":5,"hash":"2c14024bf8584c3f7f63f24ea490e812"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc. (Intel)~ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":48,"hash":"62d5bbf307ed9e959ad3d5ad6ccd3951"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1652192386973,"render":1652192386434}}',
	    'specId': 'yidregsimplified',
	    'crumb': 'IHW88p4nwpv',
	    'acrumb': 'Cgvhb3Xg',
	    'userid-domain': 'yahoo',
	    'userId': str(email),
	    'password': '@GDOTools',}		
		res = requests.post(url,headers=headers,data=data).text 	
		if ("userId") in res:	
			return {'status':'error','email':False}
		
		else:		
			return {'status':'Success','email':True}




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
		'x-requested-with': 'XMLHttpRequest',}
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
		res = requests.post(url,headers=headers,data=data).text 	
		if ('"yid"') in res:			
			return {'status':'error','email':False}
			
		else:			
			return {'status':'Success','email':True}
			


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
        'email' :str(email),
        'username':str(email),
        'first_name': '@GDOTools',
        'opt_into_one_tap': 'false'}		
		try:
			res = requests.post(url, data=data, headers=headers).json()["errors"]["email"]	
			return {'status':'Success','email':True}
		
		except: 
			return {'status':'error','email':False}
				
	
	
	def facebook(email: str) -> str:
		br = mechanize.Browser()
		br.set_handle_robots(False)
		br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
		br.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2821.96 Safari/537.36')]
		br.open("https://mbasic.facebook.com/login/identify/?ctx=recover&search_attempts=0&ars=facebook_login&alternate_search=0&toggle_search_mode=1") 	
		br._factory.is_html= True
		br.select_form(nr=0)
		br.form["email"] = email
		br.submit()
		res = br.geturl()
		if "https://mbasic.facebook.com/login/device-based/ar/login/?ldata=" in res:
			return {'status':'Success','email':True}
		
		else:
			return {'status':'error','email':False}


	def twiter(email: str) -> str:
		rs = requests.Session()
		url = f"https://api.twitter.com/i/users/email_available.json?email={email}"
		rs.headers = {
		'User-Agent': generate_user_agent(),
		'Host':"api.twitter.com",
		'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",}
		res = rs.get(url).json()
		if res['valid'] == True:
			return  {'status':'Success','email':True}
			
		else:
			return {'status':'error','email':False}

	
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
		data = {"email":email}
		req = requests.post(url,headers=headers,data=data)
		if "Sent successfully" in req.text:
			return {'status':'Success','email':True}
			
		else:
			return {'status':'error','email':False}
	
		
	
			
			



