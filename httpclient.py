#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def parse_url(self,url):
        if (url.find("http://") != 0):
            url = "http://" + url
        
        o = urlparse.urlparse(url)
        
        if (":" in o.netloc):
            p = o.netloc.find(":")
            netloc = o.netloc[0:p]
        else:
            netloc = o.netloc
        
        path = o.path
        
        if (o.query != ""):
            query = "?" + urllib.quote(o.query,"$&+,/:;=?@")
        else:
            query = o.query
        
        if (o.port == None):
            port = 80
        else:
            port = int(o.port)

        host = netloc + ":" + str(port)
        path = path + query

        return port, netloc, path, host

    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port))
        return sock

    def get_code(self, data):
        return int(data.split(' ')[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        port,netloc,path,host = self.parse_url(url)
        sock = self.connect(netloc,port)
        _data = ("GET "+ path + 
                " HTTP/1.1\r\n" +
                "Host:"+ host + "\r\n" +
                "Accept:*/*\r\n"+
                "Connection:close\r\n\r\n")
        sock.sendall(_data)
        _buffer = self.recvall(sock)
        code = self.get_code(_buffer)
        body = self.get_headers(_buffer) + self.get_body(_buffer)
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        port,netloc,path,host = self.parse_url(url)
        sock = self.connect(netloc,port)
        if (args != None) :
            data = urllib.urlencode(args)
        else: 
            data = ''
        _data = ("POST "+ path + 
                " HTTP/1.1\r\n" +
                "Host:"+ host + "\r\n" +
                "Accept:*/*\r\n" +
                "Content-Length:" + 
                str(len(data)) + "\r\n" +
                "Connection:close\r\n" +
                "Content-Type:" +
                "application/x-www-form-urlencoded\r\n\r\n" +
                data)
        sock.sendall(_data)
        _buffer = self.recvall(sock)
        code = self.get_code(_buffer)
        body = self.get_body(_buffer)
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )
