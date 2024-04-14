:<<!
使用platform.pk8、platform.x509.pem生成.keystore
windows 上换行注意 只用LF，不能使用CR

命令详解:
./keytool-importkeypair -k system.keystore -p 123456 -pk8 platform.pk8 -cert platform.x509.pem -alias test
-k 表示要生成的 keystore 文件的名字，这里为 system.keystore
-p 表示要生成的 keystore 的密码，这里为 123456
-pk8 表示要导入的 platform.pk8 文件
-cert 表示要导入的platform.x509.pem
-alias 表示给生成的 keystore 取一个别名，这是命名为 test

!

# read -p "Please input password >>>: " password
# read -p "Please keystore name >>>: " keystore_name
# read -p "Please alias name >>>: " alias_name

#./keytool-importkeypair -k ./$keystore_name -p $password -pk8 platform.pk8 -cert platform.x509.pem -alias $alias_name


# name: platform.keystore or platform.jks
# password: android
# alias: android
./keytool-importkeypair -k platform.keystore -p android -pk8 platform.pk8 -cert platform.x509.pem -alias android