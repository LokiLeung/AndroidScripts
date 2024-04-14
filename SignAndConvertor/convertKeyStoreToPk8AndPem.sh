#!/bin/bash

# 检查命令是否存在
command -v keytool >/dev/null 2>&1 || { echo >&2 "keytool 工具未找到，请确保 JDK 已安装"; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo >&2 "openssl 工具未找到，请确保已安装 OpenSSL"; exit 1; }

# 检查参数
if [ $# -ne 1 ]; then
  echo "用法: $0 <your_keystore_file>"
  exit 1
fi

# 检查 keystore 文件是否存在
if [ ! -f "$1" ]; then
  echo "指定的 keystore 文件不存在: $1"
  exit 1
fi

# 1. 将 keystore 文件转换为 PKCS12 格式
echo "正在将 keystore 文件转换为 PKCS12 格式..."
keytool -importkeystore -srckeystore "$1" -destkeystore tmp.p12 -srcstoretype JKS -deststoretype PKCS12 || { echo "转换失败"; exit 1; }
echo "转换完成"

# 2. 将 PKCS12 文件转换为 PEM 格式
echo "正在将 PKCS12 文件转换为 PEM 格式..."
openssl pkcs12 -in tmp.p12 -nodes -out tmp.rsa.pem || { echo "转换失败"; exit 1; }
echo "转换完成"

# 3. 提取证书和私钥
echo "正在提取证书和私钥..."
awk '/BEGIN PRIVATE KEY/,/END PRIVATE KEY/' tmp.rsa.pem > private.rsa.pem
awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/' tmp.rsa.pem > cert.x509.pem
echo "提取完成"

# 4. 生成 PKCS8 格式的私钥
echo "正在生成 PKCS8 格式的私钥..."
openssl pkcs8 -topk8 -outform DER -in private.rsa.pem -inform PEM -out private.pk8 -nocrypt || { echo "转换失败"; exit 1; }
echo "转换完成"

# 清理临时文件
echo "清理临时文件..."
rm tmp.p12 tmp.rsa.pem private.rsa.pem
echo "清理完成"

echo "生成的 cert.x509.pem 和 private.pk8 文件即为转换后的结果"