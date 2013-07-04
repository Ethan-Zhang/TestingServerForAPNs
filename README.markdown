# TestingServerForAPNsFeedBack

A TCP server for testing the APNS Push service

## Sample usage

```shell
./test-server -c apns-dev-cert.pem -k apns-dev.pem
```

Client must use the same cert or key file as server end.


## Further Info

[iOS Reference Library: Local and Push Notification Programming Guide][a1]

[a1]:http://developer.apple.com/iphone/library/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Introduction/Introduction.html#//apple_ref/doc/uid/TP40008194-CH1-SW1
