docker run -it  \
    --volume /Users/ddavila/.globus/usercert.pem:/root/.globus/usercert.pem \
    --volume /Users/ddavila/.globus/userkey.pem:/root/.globus/userkey.pem \
    --volume $(pwd)/dasgoclient_linux:/usr/local/bin/dasgoclient \
    --volume $(pwd)/tpc_transfers:/tpc_transfers \
    --env X509_USER_CERT=/root/.globus/usercert.pem \
    --env X509_USER_KEY=/root/.globus/userkey.pem \
    tx_client:latest
