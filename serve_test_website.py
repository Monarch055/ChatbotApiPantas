#!/usr/bin/env python3
"""
Simple HTTP server to serve the test website
"""
import http.server
import socketserver
import os
import webbrowser
from threading import Timer

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://localhost:3000')

def run_server():
    """Run the HTTP server"""
    # Change to the test-website directory
    os.chdir(os.path.join(os.path.dirname(__file__), 'test-website'))
    
    PORT = 3000
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving test website at http://localhost:{PORT}")
        print("Make sure your ChatBot API is running at http://127.0.0.1:8000")
        print("Press Ctrl+C to stop the server")
        
        # Open browser after 1 second
        Timer(1.0, open_browser).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()