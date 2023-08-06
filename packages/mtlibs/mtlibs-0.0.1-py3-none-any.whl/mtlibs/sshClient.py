import logging
import paramiko
class SshClient:
    def __init__(self, host,user="root", password=None, port=22):
        """如果没有指定密码，就使用私钥登陆"""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        #设置 paramiko的一些环境
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def exec_cmd(self, script):
        """执行命令(没用上，没封装好)"""
        stdin, stdout, stderr = self.client.exec_command("whoami", get_pty=True)
        while not stdout.channel.exit_status_ready():
            result = stdout.readline()
            print(result)
            # 由于在退出时，stdout还是会有一次输出，因此需要单独处理，处理完之后，就可以跳出了
            if stdout.channel.exit_status_ready():
                a = stdout.readlines()
                print(a)
                break
        self.client.close()


    def uploadFiles(self, file_from, file_to):
        trans=paramiko.Transport((self.host,self.port))
        trans.connect(username= self.user,password=self.password)
        #建立一个sftp客户端对象，通过ssh transport操作远程文件
        sftp=paramiko.SFTPClient.from_transport(trans)
        #Copy a local file (localpath) to the SFTP server as remotepath
        sftp.put(file_from,file_to)
        trans.close()

    def downloadFile(self,remote_path, local_path):
        #TODO: 
        logging.log("downloadFile 功能未实现")

    def portMap(self, local_port, remote_ip, remote_port):
        #端口映射
        import getpass
        import socket
        import select
        import json
        from threading import Thread
        try:
            import SocketServer
        except ImportError:
            import socketserver as SocketServer

        class ForwardServer(SocketServer.ThreadingTCPServer):
            daemon_threads = True
        allow_reuse_address = True


        class Handler(SocketServer.BaseRequestHandler):

            def handle(self):
                try:
                    chan = self.ssh_transport.open_channel(
                        "direct-tcpip",
                        (self.chain_host, self.chain_port),
                        self.request.getpeername(),
                    )
                except Exception as e:
                    logging.log(
                        "Incoming request to %s:%d failed: %s"
                        % (self.chain_host, self.chain_port, repr(e))
                    )
                    return
                if chan is None:
                    logging.log(
                        "Incoming request to %s:%d was rejected by the SSH server."
                        % (self.chain_host, self.chain_port)
                    )
                    return

                while True:
                    r, w, x = select.select([self.request, chan], [], [])
                    if self.request in r:
                        data = self.request.recv(1024)
                        if len(data) == 0:
                            break
                        chan.send(data)
                    if chan in r:
                        data = chan.recv(1024)
                        if len(data) == 0:
                            break
                        self.request.send(data)

                peername = self.request.getpeername()
                chan.close()
                self.request.close()


        def forward_tunnel(local_port, remote_host, remote_port, transport):
            class SubHander(Handler):
                chain_host = remote_host
                chain_port = remote_port
                ssh_transport = transport

            ForwardServer(("", local_port), SubHander).serve_forever()
        

        tunnel_thread = Thread(target=forward_tunnel, args=(local_port, remote_ip,
                                                                remote_port,
                                                                self.client.get_transport()))
        tunnel_thread.start()
        print("线程启动了")



        
  
