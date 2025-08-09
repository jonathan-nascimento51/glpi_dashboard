#!/usr/bin/env python3
"""
Servidor HTTP simples para servir arquivos de teste
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def main():
    # Definir porta
    PORT = 8080
    
    # Definir diretório atual como raiz
    web_dir = Path(__file__).parent
    os.chdir(web_dir)
    
    # Criar handler
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Adicionar cabeçalhos CORS
    class CORSRequestHandler(Handler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.end_headers()
    
    # Criar servidor
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print(f"Servidor rodando em http://localhost:{PORT}")
        print(f"Acesse: http://localhost:{PORT}/test_frontend_backend_communication.html")
        print("Pressione Ctrl+C para parar")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor parado.")
            sys.exit(0)

if __name__ == "__main__":
    main()