# /bin/bash

openssl genrsa -out server.key 2048
openssl req -nodes -new -sha256 -newkey rsa:2048 -key server.key -subj "/CN=ab-test-service.ab-service-dir.example.com" -out server.csr
openssl x509 -req -days 3650 -sha256 -in server.csr -signkey server.key -out server.crt -extfile <(printf "\nsubjectAltName='DNS:ab-test-service.ab-service-dir.example.com'")

openssl x509 -in server.crt -out server.der -outform DERzt