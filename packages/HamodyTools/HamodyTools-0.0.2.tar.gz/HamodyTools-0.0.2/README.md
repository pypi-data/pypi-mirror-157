<h1 align="center">HamodyToola</h1>
<p align="center">It's a Usefull Project for Developers ... It checkers Emails Found Or Not Found</p>

<p align="center"> • DevVlopered The Lib BY Hamody • </p>


## Installing :
```
pip install HamodyTools

```
## • Get Email instagram •

```
from HamodyTools import Hamody
sessionid = "239237472%3AOgNczUIlUfx1VB%3A4"
user = "m.salimi6666"
check = Hamody.get(user,sessionid)
print(check)

```
## • Login Instagram •

```
from HamodyTools import *
username = "******"
password = "******"
login = Hamody.Instagram(username,password)
if login==True:
	print("GooD")
if login==False:
	print("challenge")
if login==None:
	print("Error Email & Password")
```
## • Login Twitter •
```
from HamodyTools import *
username = "******"
password = "******"
login = Hamody.Twitter(username,password)
if login==True:
	print("• Done Login •")
else:
	print("• Error Login •")
```
## • Login Facebook •
```
from HamodyTools import *
username = "******"
password = "******"
login = Hamody.Facebook(username,password)
if login==True:
	print("• Done Login •")
else:
	print("• Error Login •")
```
## • Check Yahoo •
```
from HamodyTools import *
email = "********@yahoo.com"
check = Hamody.Yahoo(email)
if check==True:
	print("• Available •")
else:
	print("• Unavailable •")
```
## • Check Instagram •

```
from HamodyTools import *
email = "********@yahoo.com"
check = Hamody.Check_Instagram(email)
if check==True:
	print("• Linked Instagram •")
else:
	print("• Not Linked Instagram •")
```
## • Reset Instagram •
```
from HamodyTools import *
email = "********@yahoo.com"
check = Hamody.Reset(email)
if check==True:
	print("• Done Reset •")
else:
	print("• Error Send Reset •")
```
## • Check Visa •
```
from HamodyTools import *
visa = "*******|****|***"
check = Hamody.Visa(visa)
if check==False:
	print("• Dead Visa")
else:
	print(check)
```