FROM alpine:latest

RUN apk --update add privoxy tor runit tini

COPY service /etc/service/

ENTRYPOINT ["tini", "--"]
CMD ["runsvdir", "/etc/service"]
