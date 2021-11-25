import sys
import signal
from termios import TIOCMIWAIT
import rclpy  # ROS2のPythonモジュールのインポート 
import time   # timeモジュールのインポート                                                                        
import math   # 数学関数モジュールのインポート                                                                    
import numpy as np # numpyモジュールを別名npをつけてインポート   
import matplotlib.pyplot as plt                                                 
from rclpy.node import Node # rclpy.nodeモジュールからNodeクラスをインポート                                      
from std_msgs.msg import String # トピック通信に使うStringメッセージ型をインポート                                
from geometry_msgs.msg import Twist # トピック通信に使うTwistメッセージ型をインポート                             
from nav_msgs.msg import Odometry # nav_msgs.msgモジュールからOdometryクラスをインポート  
from concurrent.futures import ThreadPoolExecutor  

if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty

def handler(signal, frame):
    print('強制終了')
    sys.exit(0)

def getKey(settings):
    if sys.platform == 'win32':
        # getwch() returns a string on Windows
        key = msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        # sys.stdin.read() returns a string on Linux
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


class Pose:                                                                                                       
    """"姿勢のクラス    
        位置(x, y)、向き(yaw)                                                                               
    """                                                                                                           
    def __init__(self, x = 0.0, y = 0.0, yaw = 0.0):                                                              
        self.x = x                                                                                                
        self.y = y                                                                                                
        self.yaw = yaw
        self.n = -1     
                                                                                               
    def set(self, x, y, yaw,):                                                                                     
        self.x = x                                                                                                
        self.y = y                                                                                                
        self.yaw = yaw 
        self.n = self.n + 1
        print("callback:",self.x,self.y,self.yaw,self.n)                                                                                           
                                                                                                                  
    def get(self):                                                                                                
        return self.x, self.y, self.yaw, self.n 
        
class Teleop_twist(Node):                                                                       
    def __init__(self):                                                                                           
                                                                                                            
        # Nodeクラスのコンストラクタを呼び出し、'teleop_twist'というノード名をつける。                                
        super().__init__('teleop_twist')                                                                              
                                                                                                                  
        # パブリッシャーの生成。create_publisherの1番目の引数はトピック通信に使うメッセージ型。                   
        # Twist型は速度指令値を通信するのに使われる。2番目の引数'cmd_vel'はトピック名。                           
        # 3番目の引数はキューのサイズ。キューサイズはQOS(quality of service)の設定に使われる。                    
        # サブスクライバーがデータを何らかの理由で受信できないときのキューサイズの上限となる。                    
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)                                                     
                                                                                                                  
        # サブスクライバーの生成。create_subscriptionの1番目の引数Odometryはトピック通信に使うメッセージ型。         
        # 2番目の引数'odom'はトピック名。                           
        # 3番目の引数はコールバック関数。 4番目の引数はキューのサイズ。                                           
        self.sub = self.create_subscription(Odometry,'odom', self.odom_callback, 10)                              
                                                                                                                  
        # Twistメッセージ型オブジェクトの生成。メンバーにdVector3型の並進速度成分linear、                         
        # 角速度成分angularを持つ。       

                                                                                               
        print("***start***")                                             
        self.twist = Twist()                                                                                                     
        self.odom  = Odometry()                                                                                   
        self.pose  = Pose()
        
    def odom_callback(self, odom): 
        
        x = odom.pose.pose.position.x
        y = odom.pose.pose.position.y                                                                           
        yaw = np.arctan2(2 * (odom.pose.pose.orientation.w * odom.pose.pose.orientation.z + odom.pose.pose.orientation.x * odom.pose.pose.orientation.y), 1 - 2 *(odom.pose.pose.orientation.y * odom.pose.pose.orientation.y + odom.pose.pose.orientation.z * odom.pose.pose.orientation.z))
        self.pose.set(x, y, yaw)    
                                                                 

def main(args=None):                                                                                              
    rclpy.init(args=args) # rclpyモジュールの初期化                                                               
    teleop_twist = Teleop_twist()  # ノードの作成
    signal.signal(signal.SIGINT, handler)
    settings = saveTerminalSettings()

    key = getKey(settings)
    while True:
        pass
        teleop_twist.twist = Twist()
        teleop_twist.twist.linear.x = 0.0
        teleop_twist.twist.angular.z = 0.0 
        teleop_twist.pub.publish(teleop_twist.twist)
        
    
     
if __name__ == '__main__':
    main()