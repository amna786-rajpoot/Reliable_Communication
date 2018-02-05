"""
# Aditya Sinha
# asinha25

Where solution code to HW5 should be written.  No other files should
be modified.
"""

import socket
import io
import time
import homework5
import homework5.logging


def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.
    """
    # Naive implementation where we chunk the data to be sent into
    # packets as large as the network will allow, and then send them
    # over the network, pausing half a second between sends to let the
    # network "rest" :)
    timeout = 1
    dev = 0.0
    est = 0
    packet_total = 0
    # updating the size
    size = homework5.MAX_PACKET - 4
    offsets = range(0, len(data), homework5.MAX_PACKET - 4)

    for chunk in [data[i: i + size] for i in offsets]:
        header = packet_total.to_bytes(4, byteorder='big')
        # sending header and the chunk of data
        sock.send(header + chunk)

        while True:
            try:
                # setting timeout
                sock.settimeout(timeout)
                start = time.time()
                # get data from the sock
                data = sock.recv(4)

                # check data with the header
                if data == header:
                    sam = time.time() - start

                    # is est = 0
                    if not est:
                        est = sam
                        dev = sam / 2

                    # is est not 0
                    if est:
                        delta = abs(sam - est)
                        est = 0.875 * est + 0.125 * sam
                        dev = 0.75 * dev + 0.25 * delta

                    # update timeout
                    timeout = est + 4 * dev
                    break

                # sending header with data chunk
                sock.send(header + chunk)
            except socket.timeout:
                # if timeout occurs resend
                sock.send(header + chunk)
                # update timeout by multiple of 2
                timeout = timeout * 2
                continue
        # add to packet_total
        packet_total += 1


def checker(element1, element2):
    """
    Check if two elements are the same of different

    :param element1:
    :param element2:
    :return:
    if same return True
    else False
    """
    if element1 == element2:
        return True
    return False


def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    """
    Implementation of the receiving logic for receiving data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.

    Return:
        The number of bytes written to the destination.
    """
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    number_of_bytes = 0
    previous_header = []

    # continuous loop for receiving data
    while True:
        # gets packet
        packets = sock.recv(homework5.MAX_PACKET)
        # if packet == null, exit out of loop
        if not packets:
            break
        else:
            # take out the header from the packet
            header = packets[0: 4]
            # send it back to the sender as confirmation
            sock.send(header)
            # if header is same as prev header, return to top of loop
            if checker(previous_header, header):
                continue
        length_of_packet = len(packets)
        # update total bytes received
        number_of_bytes += length_of_packet - 4
        # update prev header
        previous_header = header
        # write it into destination
        dest.write(packets[4: length_of_packet])
        dest.flush()
    return number_of_bytes
