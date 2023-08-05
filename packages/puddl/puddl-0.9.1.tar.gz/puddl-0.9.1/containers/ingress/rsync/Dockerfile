FROM alpine:3

LABEL puddl=0
LABEL puddl.ingress=rsync
EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-eD"]

RUN apk add --no-cache bash git openssh rsync
COPY entrypoint.sh /
COPY sshd_config /etc/ssh/

# this is created by the entrypoint
WORKDIR /home/rsync
