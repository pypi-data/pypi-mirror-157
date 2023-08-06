#!/usr/bin/env pypy3
#
#
# Copyright (c) 2022, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: __init__.py,v 1.11 2022/07/02 19:09:33 ohsaki Exp ohsaki $
#

import collections

from perlcompat import die, warn, getopts
import tbdump

class Scheduler:
    def __init__(self, time=0., delta=.01, max_time=100):
        self.time = time
        self.delta = delta
        self.max_time = max_time
        self.nodes = []

    def advance(self):
        self.time += self.delta

    def is_running(self):
        return self.time <= self.max_time

class Message:
    def __init__(self,
                 src=None,
                 dst=None,
                 tstamp=None,
                 ack=False,
                 w=1.,
                 p=0.,
                 valid_since=0.,
                 rate=0.):
        self.src = src
        self.dst = dst
        self.tstamp = tstamp
        self.ack = ack
        self.w = w
        self.p = p
        self.valid_since = valid_since
        self.rate = rate

    def __repr__(self):
        return f'Message(src={self.src.id_}, dst={self.dst.id_}, tstamp={self.tstamp:.3f}, ack={self.ack}, w={self.w:.3f}, p={self.p:.3f}, valid_since={self.valid_since:.3f}, rate={self.rate:.3f})'

node_ids = 0

class Node:
    def __init__(self, scheduler=None):
        global node_ids
        node_ids += 1
        self.id_ = node_ids
        self.scheduler = scheduler
        self.neighbors = []
        self.queue = collections.deque()

    def __repr__(self):
        return f'Node(id_={self.id_}, #queue={len(self.queue)})'

    def connect(self, other, delay=0.):
        self.neighbors.append((other, delay))
        other.neighbors.append((self, delay))

    def enqueue(self, msg):
        self.queue.append(msg)

    def dequeue(self):
        if self.msg_ready():
            return self.queue.popleft()
        return None

    def msg_ready(self):
        if self.queue:
            msg = self.queue[0]
            # FIXME: sometimes scheduler.time goes smaller?
            if msg.valid_since <= self.scheduler.time + 1e-4:
                return True
        return False

    def next_node(self, dst):
        # FIXME: Should build a routing table for every destination.
        for v, delay in self.neighbors:
            if v == dst:
                return v, delay
        # Return the first entry as a last resort.
        return self.neighbors[0]

class Sender(Node):
    def __init__(self, scheduler):
        super().__init__(scheduler)
        self.src = self
        self.dst = None
        self.w = 1.
        self.rtt = 0.
        self.p = 0.
        self.last_w = self.w

    def __repr__(self):
        return f'{self.scheduler.time:.3f} Sender(src={self.src.id_}, dst={self.dst.id_}, w={self.w:.3f}, rtt={self.rtt:.3f}, p={self.p:.3f}, #queue={len(self.queue)})'

    def advance(self):
        # Process all messages.
        while self.msg_ready():
            msg = self.dequeue()
            # Update the current RTT and loss rate estimates.
            self.rtt = self.scheduler.time - msg.tstamp
            self.p = msg.p
            self.last_w = self.w

        # Enable only after the initial feedback reception.
        if self.rtt > 0:
            dw = (1 - self.p ) / self.rtt - self.p * 2 / 3 * self.last_w / self.rtt
            self.w += dw * self.scheduler.delta
            rate = self.w / self.rtt
        else:
            rate = 0.

        # forward a message corresponding Data packets.
        msg = Message(src=self.src,
                      dst=self.dst,
                      tstamp=self.scheduler.time,
                      w=self.w,
                      rate=rate)
        # Forward the message to the neighbor.
        node, delay = self.next_node(self.dst)
        # Activate the message after the link delay.
        msg.valid_since = self.scheduler.time + delay
        node.enqueue(msg)

class Receiver(Node):
    def __init__(self, scheduler):
        super().__init__(scheduler)

    def __repr__(self):
        return f'{self.scheduler.time:.3f} Receiver(#queue={len(self.queue)})'

    def advance(self):
        # Process all available messages.
        while self.msg_ready():
            msg = self.dequeue()
            # Compose ACK message will be sent back to the source.
            src, dst = msg.src, msg.dst
            msg.src, msg.dst = dst, src
            msg.ack = True
            # Forward the message to the neighbor.
            node, delay = self.next_node(msg.dst)
            # Activate the message after the link delay.
            msg.valid_since = self.scheduler.time + delay
            node.enqueue(msg)

class Router(Node):
    def __init__(self, scheduler, bandwidth=1., qsize=10):
        super().__init__(scheduler)
        self.q = 0
        self.p = 0.
        self.in_rate = 0.
        self.bandwidth = bandwidth
        self.qsize = qsize

    def __repr__(self):
        return f'{self.scheduler.time:.3f} Router(q={self.q}, p={self.p:.3f}, in_rate={self.in_rate:.3f}, #queue={len(self.queue)})'

    def advance(self):
        rate_from = collections.defaultdict(float)
        msgs = []
        while self.msg_ready():
            msg = self.dequeue()
            msgs.append(msg)
            # Assume the size of ACK packets are negligible.
            if not msg.ack:
                # FIXME: Must discremenate incoming links rather than source.
                rate_from[msg.src] += msg.rate
        # Total arrival rate.
        self.in_rate = sum(rate_from.values())

        # Update the queue length.
        dq = self.in_rate - self.bandwidth
        self.q += dq * self.scheduler.delta
        self.q = min(max(self.q, 0), self.qsize)
        # Detect the loss rate and outgoing rate.
        if self.q >= self.qsize:
            self.p = min(max(dq / self.in_rate, 0.), 1.)
            rate = self.bandwidth
        else:
            self.p = 0.
            rate = self.in_rate

        for msg in msgs:
            # Overwrite the loss rate and sending rate.
            msg.p = min(max(msg.p + self.p, 0.), 1.)
            msg.rate = rate

            # Forward the message to the neighbor.
            node, delay = self.next_node(msg.dst)
            # Activate the message after the link delay plus queueing delay.
            msg.valid_since = self.scheduler.time + self.q / self.bandwidth + delay
            node.enqueue(msg)

class Monitor:
    def __init__(self, scheduler=None):
        self.scheduler = scheduler

    def display(self, nodes):
        t = self.scheduler.time
        values = [f't={t:.3f}']
        for node in nodes:
            n = node.id_
            if type(node) == Sender:
                values.append(f'w{n}={node.w:.3f}')
                values.append(f'r{n}={node.rtt:.3f}')
            if type(node) == Router:
                values.append(f'q{n}={node.q:.3f}')
                values.append(f'p{n}={node.p:.3f}')
        print('\t'.join(values))
