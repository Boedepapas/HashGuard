"""
TCP socket-based IPC for HashGuard backend-frontend communication over localhost.
"""

import socket
import threading
import json
import os
from pathlib import Path
from typing import Optional, Callable, Dict, Any

PIPE_NAME = r"\\.\pipe\HashGuardBackend"
LOCALHOST = "127.0.0.1"
IPC_PORT = 54321


class IPCServer:
    """
    Listens for commands from the frontend and broadcasts status updates.
    Runs in a background thread.
    """
    
    def __init__(self, command_handler: Optional[Callable] = None):
        """
        Args:
            command_handler: Callback function(command_dict) -> response_dict
        """
        self.command_handler = command_handler
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.thread: Optional[threading.Thread] = None
        self.clients = set()
        self.clients_lock = threading.Lock()
    
    def start(self):
        """Start the IPC server in a background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        print(f"[IPC] Server started on {LOCALHOST}:{IPC_PORT}")
    
    def stop(self):
        """Stop the IPC server."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        if self.thread:
            self.thread.join(timeout=5)
        print("[IPC] Server stopped")
    
    def _run_server(self):
        """Main server loop."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((LOCALHOST, IPC_PORT))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            
            while self.running:
                try:
                    client, addr = self.server_socket.accept()
                    print(f"[IPC] Client connected from {addr}")
                    
                    # Add to client list
                    with self.clients_lock:
                        self.clients.add(client)
                    
                    # Handle client in separate thread
                    threading.Thread(
                        target=self._handle_client,
                        args=(client, addr),
                        daemon=True
                    ).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[IPC] Server error: {e}")
        except Exception as e:
            print(f"[IPC] Failed to start server: {e}")
    
    def _handle_client(self, client: socket.socket, addr):
        """Handle a single client connection."""
        try:
            while self.running:
                # Receive message
                data = client.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    print(f"[IPC] Received from {addr}: {message}")
                    
                    # Handle command
                    response = {"status": "ok"}
                    if self.command_handler:
                        response = self.command_handler(message) or response
                    
                    # Send response
                    client.send(json.dumps(response).encode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"[IPC] Invalid JSON from {addr}: {e}")
                    client.send(json.dumps({"status": "error", "message": "Invalid JSON"}).encode('utf-8'))
        except Exception as e:
            print(f"[IPC] Client error: {e}")
        finally:
            with self.clients_lock:
                self.clients.discard(client)
            try:
                client.close()
            except:
                pass
            print(f"[IPC] Client {addr} disconnected")
    
    def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        data = json.dumps(message).encode('utf-8')
        with self.clients_lock:
            dead_clients = set()
            for client in self.clients:
                try:
                    client.send(data)
                except Exception as e:
                    print(f"[IPC] Failed to send to client: {e}")
                    dead_clients.add(client)
            
            # Remove dead clients
            for client in dead_clients:
                self.clients.discard(client)
                try:
                    client.close()
                except:
                    pass


class IPCClient:
    """Simple client for communicating with the backend."""
    
    def __init__(self, host: str = LOCALHOST, port: int = IPC_PORT):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
    
    def connect(self) -> bool:
        """Connect to the IPC server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"[IPC Client] Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[IPC Client] Failed to connect: {e}")
            return False
    
    def send_command(self, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a command and get response."""
        if not self.socket:
            return None
        
        try:
            self.socket.send(json.dumps(command).encode('utf-8'))
            response = self.socket.recv(4096)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            print(f"[IPC Client] Error: {e}")
            return None
    
    def close(self):
        """Close the connection."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
