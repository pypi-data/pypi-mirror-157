"""Utils"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import ssl
import webbrowser


class CustomHTTPHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if '/' in self.path:
            global code_param
            code_param = self.path
            self.send_response(301)
            self.send_header('Location', 'http://localhost' + self.path)
            self.end_headers()
            self.stop_server()

    def stop_server(self):
        self.server.server_close()
        self.server.shutdown()


def wait_for_request(url, server_class=ThreadingHTTPServer):
    webbrowser.open(url)
    server_address = ('', 1443)
    httpd = server_class(server_address, CustomHTTPHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   server_side=True,
                                   keyfile="localhost.key",
                                   certfile='localhost.crt',
                                   )
    httpd.serve_forever()
    print(httpd)
    code = code_param.split('=')[1]
    return code
