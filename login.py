from linepy import *

client = LINE()  # سيظهر لك QR Code
print("✅ تم تسجيل الدخول بنجاح!")
print("authToken:", client.authToken)
