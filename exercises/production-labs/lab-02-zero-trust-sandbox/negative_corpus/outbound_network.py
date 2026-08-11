import socket


connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.settimeout(1)
try:
    connection.connect(("1.1.1.1", 53))
except OSError:
    print("NETWORK_BLOCKED")
else:
    raise AssertionError("network=none allowed outbound TCP")
finally:
    connection.close()
