# ansi_sender.py
import socket, atexit

_addr = ("127.0.0.1", 9999)
_timeout = None
_encoding = "utf-8"
_sock = None
_was_initted = False


def init_if_needed():
    global _was_initted
    if not _was_initted:
        init()

def init(host="127.0.0.1", port=9999, timeout=None, encoding="utf-8"):
    """Configure and open a persistent connection (no threading)."""
    global _addr, _timeout, _encoding, _was_initted
    _addr = (host, port); _timeout = timeout; _encoding = encoding
    _open()
    _was_initted = True

def _open():
    global _sock
    if _sock is None:
        _sock = socket.create_connection(_addr, timeout=_timeout)

def _reopen():
    global _sock
    if _sock:
        try: _sock.close()
        except OSError: pass
    _sock = None
    _open()

def send(msg, end="\n"):
    """Send one message; reconnects once on error. Returns True/False."""
    global _sock
    data = (msg + end).encode(_encoding, "replace")
    for _ in (0, 1):  # try once, then reconnect+retry
        if _sock is None:
            _open()
        try:
            _sock.sendall(data)
            return True
        except (BrokenPipeError, ConnectionResetError, OSError):
            _reopen()
    return False

def is_connected():
    return _sock is not None

def close():
    global _sock
    if _sock:
        try:
            _sock.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        _sock.close()
        _sock = None

atexit.register(close)
