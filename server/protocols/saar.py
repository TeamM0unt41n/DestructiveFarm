import socket
import logging
import time

from models import Flag_Status, SubmitResult, Config_Model, Flag_Model

logger = logging.getLogger(__name__)

RESPONSES = {
    Flag_Status.QUEUED: [
        '[OFFLINE] CTF not running'
    ],
    Flag_Status.ACCEPTED: [
        '[OK]',
    ],
    Flag_Status.REJECTED: [
        '[ERR] Invalid format',
        '[ERR] Invalid flag',
        '[ERR] Expired',
        '[ERR] Already submitted',
        '[ERR] Can\'t submit flag from NOP team',
        '[ERR] This is your own flag'
    ],
}

READ_TIMEOUT = 5
APPEND_TIMEOUT = 0.05
BUFSIZE = 4096


def recvall(sock:socket.socket):
    sock.settimeout(READ_TIMEOUT)
    chunks = [sock.recv(BUFSIZE)]

    sock.settimeout(APPEND_TIMEOUT)
    while True:
        try:
            chunk = sock.recv(BUFSIZE)
            if not chunk:
                break

            chunks.append(chunk)
        except socket.timeout:
            break

    sock.settimeout(READ_TIMEOUT)
    return b''.join(chunks)


def submit_flags(flags:list[Flag_Model], config:Config_Model):
    sock = socket.create_connection((config.SYSTEM_HOST, config.SYSTEM_PORT),
                                    READ_TIMEOUT)
    
    unknown_responses = set()
    sock.sendall(b'\n'.join(item.flag.encode() for item in flags) + b'\n')

    while len(flags) > 0:
        response = recvall(sock).decode().strip()
        if not response:
            break

        response = response.splitlines()
        for line in response:
            flag = flags[0]

            for status, substrings in RESPONSES.items():
                if any(s in line for s in substrings):
                    found_status = status
                    break
            else:
                found_status = Flag_Status.QUEUED
                if line not in unknown_responses:
                    unknown_responses.add(line)
                    logger.warning('Unknown checksystem response (flag will be resent): %s', line)

            if found_status == Flag_Status.QUEUED and time.time() - flag.time > 10:
                found_status = Flag_Status.REJECTED
                line = f'was response {line}, but inv flag too old'

            yield SubmitResult(flag.flag, found_status, line)

            flags = flags[1:]

    sock.close()