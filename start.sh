#!/bin/sh

tor &&
polipo \
  proxyAddress="0.0.0.0" \
  proxyPort=8123 \
  socksParentProxy="localhost:9050" \
  daemonise=true \
  socksProxyType=socks5
