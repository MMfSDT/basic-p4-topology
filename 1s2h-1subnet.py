#!/usr/bin/env python2

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from router.p4_mininet import P4Switch, P4Host

import argparse
from time import sleep
import os
import subprocess

class SingleSwitchTopo(Topo):
    "Single switch connected to n (< 256) hosts."
    def __init__(self, n, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        switch = self.addSwitch('s1',
                                sw_path = './router/simple_router',
                                json_path = './router/simple_router.json',
                                thrift_port = 9090,
                                pcap_dump = False)

        for h in xrange(n):
            host = self.addHost('h%d' % (h + 1),
                                ip = "10.0.0.%d/24" % (h + 2),
                                mac = '00:04:00:00:00:%02x' %h)
            self.addLink(host, switch)

def main():
    num_hosts = 2

    topo = SingleSwitchTopo(num_hosts)

    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4Switch,
                  controller = None)
    net.start()

    sw_mac = ["00:aa:bb:00:00:%02x" % n for n in xrange(num_hosts)]

    for n in xrange(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.setARP('10.0.0.1', "00:aa:bb:00:00:%02x" % n)
        h.setARP('10.0.0.%d' % (int(not bool(n)) + 2), "00:aa:bb:00:00:%02x" % int(not bool(n)))
        h.setDefaultRoute("dev eth0 via %s" % '10.0.0.1')

    for n in xrange(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.describe()


    cmd = ['./tools/runtime_CLI.py', '--json', './router/simple_router.json', '--thrift-port', '9090']
    commands = ['table_set_default send_frame _drop', 'table_set_default forward _drop', 'table_set_default ipv4_lpm _drop', 'table_add send_frame rewrite_mac 1 => 00:aa:bb:00:00:00', 'table_add send_frame rewrite_mac 2 => 00:aa:bb:00:00:01', 'table_add forward set_dmac 10.0.0.2 => 00:04:00:00:00:00', 'table_add forward set_dmac 10.0.0.3 => 00:04:00:00:00:01', 'table_add ipv4_lpm set_nhop 10.0.0.2/32 => 10.0.0.2 1', 'table_add ipv4_lpm set_nhop 10.0.0.3/32 => 10.0.0.3 2']

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    din, derr = p.communicate('\n'.join(commands))
    print din, derr

    # for command in commands:
    #     try:
    #         output = subprocess.check_output(cmd + [command])
    #         print output
    #     except subprocess.CalledProcessError as e:
    #         print e
    #         print e.output

    sleep(1)

    print "Ready!"
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()