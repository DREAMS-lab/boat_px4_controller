import rospy
from mavros_msgs.msg import State, PositionTarget
from mavros_msgs.srv import SetMode, CommandBool
import time
from geometry_msgs.msg import TwistStamped


class BoatController:
    """
        Move the boat forward by x_vel velcity
        Check rostopic echo /boat/mavros/local_position/velocity_body to see the velocity
    """
    is_ready_to_move = False
    x_vel = 0.2
    y_vel = 0
    z_vel = 0
    yaw_rate = 0

    def __init__(self):
        rospy.init_node('offboard_test', anonymous=True)
        rospy.Subscriber('/boat/mavros/state', State, callback=self.state_callback)
        velocity_pub = rospy.Publisher('/boat/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=10)
        rate = rospy.Rate(10)
        rate.sleep()

        while not rospy.is_shutdown():
            velocity_pub.publish(self.set_velocity(self.x_vel, self.y_vel, self.z_vel, self.yaw_rate))
            rate.sleep()

    def set_velocity(self, x_vel, y_vel, z_vel, yaw_rate):
        des_vel = TwistStamped()
        des_vel.header.frame_id = "world"
        des_vel.header.stamp = rospy.Time.from_sec(time.time())
        des_vel.twist.linear.x = x_vel
        des_vel.twist.linear.y = y_vel
        des_vel.twist.linear.z = z_vel
        des_vel.twist.angular.z = yaw_rate
        return des_vel

    def set_offboard_mode(self):
        rospy.wait_for_service('/boat/mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('/boat/mavros/set_mode', SetMode)
            isModeChanged = flightModeService(custom_mode='OFFBOARD')
        except rospy.ServiceException as e:
            print("service set_mode call failed: %s. OFFBOARD Mode could not be set. Check that GPS is enabled" % e)

    def set_arm(self):
        rospy.wait_for_service('/boat/mavros/cmd/arming')
        try:
            armService = rospy.ServiceProxy('/boat/mavros/cmd/arming', CommandBool)
            armService(True)
            self.arm = True
        except rospy.ServiceException as e:
            print("Service arm call failed: %s" % e)

    def take_off(self):
        self.set_offboard_mode()
        self.set_arm()

    def state_callback(self, msg):
        if msg.mode == 'OFFBOARD' and self.arm == True:
            self.is_ready_to_move = True
        else:
            self.take_off()


if __name__ == "__main__":
    BoatController()
