# 生成platform.pem文件
openssl pkcs8 -inform DER -nocrypt -in platform.pk8 -out platform.pem
# 生成platform.p12文件，需要设置别名和密码
openssl pkcs12 -export -in platform.x509.pem -out platform.p12 -inkey platform.pem -password pass:android -name key
# 生成platform.jks文件， -srcstorepass 设置jks文件的密码
keytool -importkeystore -deststorepass android -destkeystore ./platform.jks -srckeystore ./platform.p12 -srcstoretype PKCS12 -srcstorepass android
# 别名、密码、jks文件密码需要记下来，用于在Android Studio进行签名
