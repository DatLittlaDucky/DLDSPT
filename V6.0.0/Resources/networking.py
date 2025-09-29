# networking.py
import socket
import threading
import json
import requests
import hmac
import hashlib

# Basic server
class DLDSPTServer:
    def __init__(self, host="0.0.0.0", port=5000, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[Server] Hosting on {self.host}:{self.port}")
        self.running = True
        # Accept loop runs in main thread for better control
        self.accept_loop()

    def accept_loop(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
            except OSError:
                break
            print(f"[Server] Connection from {addr}")
            if self.password:
                try:
                    pwd = conn.recv(1024).decode("utf-8").strip()
                except Exception:
                    conn.close()
                    continue
                if pwd != self.password:
                    conn.sendall(b"Password mismatch\n")
                    conn.close()
                    continue
            self.clients.append(conn)
            threading.Thread(target=self.client_loop, args=(conn, addr), daemon=True).start()

    def client_loop(self, conn, addr):
        try:
            while self.running:
                try:
                    data = conn.recv(4096)
                except Exception:
                    break
                if not data:
                    break
                msg = data.decode("utf-8", errors="ignore").strip()
                print(f"[Server] {addr} says: {msg}")
                # broadcast to all
                for c in self.clients:
                    if c != conn:
                        try:
                            c.sendall(f"{addr}: {msg}\n".encode("utf-8"))
                        except Exception:
                            pass
        except Exception as e:
            print(f"[Server] client error: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
            if conn in self.clients:
                self.clients.remove(conn)

    def stop(self):
        self.running = False
        try:
            self.server_socket.close()
        except Exception:
            pass

# Basic client
class DLDSPTClient:
    def __init__(self, host, port=5000, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            if self.password:
                self.sock.sendall((self.password + "\n").encode("utf-8"))
            threading.Thread(target=self.listen_loop, daemon=True).start()
            print(f"[Client] Connected to {self.host}:{self.port}")
        except Exception as e:
            print(f"[Client] Connection failed: {e}")

    def listen_loop(self):
        try:
            while True:
                try:
                    data = self.sock.recv(4096)
                except Exception:
                    break
                if not data:
                    break
                print("[Client] Received:", data.decode("utf-8", errors="ignore").strip())
        except Exception as e:
            print("[Client] connection lost:", e)
        finally:
            try:
                self.sock.close()
            except Exception:
                pass

    def send(self, msg):
        try:
            self.sock.sendall((msg + "\n").encode("utf-8"))
        except Exception as e:
            print("[Client] Send failed:", e)

# Relay-based P2P client
class DLDSPTRelayClient:
    """
    Simple relay-based P2P chat using a public relay server.
    Usage:
        relay = DLDSPTRelayClient("roomname", relay_url="https://dld-relay.example.com")
        relay.send("Hello!")
        relay.listen_loop()
    """
    def __init__(self, room, relay_url="https://dldsptrelay.fly.dev"):
        self.room = room
        self.relay_url = relay_url.rstrip("/")
        self.last_id = 0

    def send(self, msg):
        try:
            payload = {"room": self.room, "msg": msg}
            requests.post(f"{self.relay_url}/send", json=payload, timeout=3)
        except Exception as e:
            print("[Relay] Send failed:", e)

    def listen_loop(self):
        print(f"[Relay] Listening in room '{self.room}' via relay server...")
        try:
            while True:
                try:
                    resp = requests.get(f"{self.relay_url}/recv", params={"room": self.room, "after": self.last_id}, timeout=5)
                    msgs = resp.json()
                    for m in msgs:
                        print(f"[Relay] {m.get('sender','peer')}: {m.get('msg')}")
                        self.last_id = max(self.last_id, m.get("id", self.last_id))
                except Exception:
                    pass
                import time; time.sleep(1)
        except KeyboardInterrupt:
            print("[Relay] Stopped listening.")

import socket

class DLDSPTLocalPeer:
    """
    Secure LAN broadcast chat (no server, no IP sharing).
    Usage:
        peer = DLDSPTLocalPeer(port=50505, password="sharedsecret")
        threading.Thread(target=peer.listen_loop, daemon=True).start()
        while True:
            msg = input("Message: ")
            if msg == "/quit":
                break
            peer.send(msg)
    """
    def __init__(self, port=50505, password="changeme"):
        self.port = port
        self.password = password.encode("utf-8")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", port))

    def sign(self, msg):
        return hmac.new(self.password, msg.encode("utf-8"), hashlib.sha256).hexdigest()

    def send(self, msg):
        try:
            sig = self.sign(msg)
            payload = json.dumps({"msg": msg, "sig": sig})
            self.sock.sendto(payload.encode("utf-8"), ("255.255.255.255", self.port))
        except Exception as e:
            print("[LAN] Send failed:", e)

    def listen_loop(self):
        print(f"[LAN] Listening for secure messages on port {self.port} (LAN broadcast)...")
        try:
            while True:
                try:
                    data, addr = self.sock.recvfrom(4096)
                    try:
                        payload = json.loads(data.decode('utf-8', errors='ignore'))
                        msg = payload.get("msg", "")
                        sig = payload.get("sig", "")
                        if hmac.compare_digest(sig, self.sign(msg)):
                            print(f"[LAN] {addr}: {msg}")
                        else:
                            print(f"[LAN] {addr}: [SECURITY WARNING] Invalid signature, message ignored.")
                    except Exception:
                        print(f"[LAN] {addr}: [SECURITY WARNING] Malformed message.")
                except Exception:
                    pass
        except KeyboardInterrupt:
            print("[LAN] Stopped listening.")

# The DLDSPTLocalPeer class does NOT use "rooms" or a host/client concept.
# It simply broadcasts messages to everyone on the same LAN using UDP.
# There is no "host room" option; all peers on the same port receive all messages.
# If you want to simulate a "room", you can add a prefix to your messages (e.g., "[room1] Hello").

# Example usage for a pseudo-room:
# peer = DLDSPTLocalPeer(port=50505)
# threading.Thread(target=peer.listen_loop, daemon=True).start()
# room = "room1"
# while True:
#     msg = input("Message: ")
#     if msg == "/quit":
#         break
#     peer.send(f"[{room}] {msg}")

# In listen_loop, you can filter messages by room prefix if desired.