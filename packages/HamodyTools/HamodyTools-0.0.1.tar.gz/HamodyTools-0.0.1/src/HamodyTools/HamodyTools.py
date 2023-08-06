try:
	import requests
	from user_agent import generate_user_agent
	import os
	import instaloader
except ModuleNotFoundError:
	import os
	os.system("pip install instaloader")
	os.system("pip install user_agent")
class Hamody:
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
	