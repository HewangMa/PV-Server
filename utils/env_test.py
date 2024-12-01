import cv2
import numpy as np
import os
import socket
import nmap

try:
    # 测试OpenCV
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(img, (10, 10), (90, 90), (0, 255, 0), 2)
    
    # 测试numpy
    arr = np.array([1, 2, 3])
    arr_sum = np.sum(arr)
    
    # 测试os
    cwd = os.getcwd()
    
    # 测试socket
    hostname = socket.gethostname()
    
    # 测试nmap
    nm = nmap.PortScanner()
    
    print("环境测试通过! 所有包都已正确安装")
    print(f"当前工作目录: {cwd}")
    print(f"主机名: {hostname}")
    print(f"arr_sum: {arr_sum}")
    
    
except Exception as e:
    print(f"环境测试失败: {str(e)}")