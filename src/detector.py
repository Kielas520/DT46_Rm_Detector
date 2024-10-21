import cv2
import numpy as np
import math

RED = 0
BLUE = 1
BOTH = 2

mode_params = {"display": 0 , "color": 2}
light_params = {"light_distance_min": 20, "light_area_min": 5, "light_angle_min": -30, "light_angle_max": 30, "light_angle_tol": 5, "line_angle_tol": 7, "height_tol": 10, "width_tol": 10, "cy_tol": 5}
armor_params = {"armor_height/width_max": 3.5,"armor_height/width_min": 1,"armor_area_max": 200,"armor_area_min": 11000, "armor_height_tol": 30, "armor_width_tol": 30, "armor_angle_tol": 30}
img_params = {"resolution": (640,480) , "val": 35}

class Light:
    def __init__(self, rect, color):
        self.color = color
        self.height = None
        self.width = None
        self.angle = None
        self.center_x = None
        self.center_y = None
        (self.center_x , self.center_y) , (self.width , self.height) , self.angle = rect

# 定义装甲板类
class Armor:
    def __init__(self, light1, light2):
        if light1.center[0] < light2.center[0]:
            self.left_light = light1
            self.right_light = light2
        else:
            self.left_light = light2
            self.right_light = light1

        self.center = (self.left_light.center + self.right_light.center) / 2
        self.type = None
        self.number_img = None
        self.number = ""
        self.confidence = 0
        self.classification_result = ""

class Img:
    def __init__(self):
        self.darken = None
        self.binary = None
        self.draw = None

    def darker(self,img):
        """降低亮度"""
        hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 转换为 HSV 颜色空间
        hsv_image[:, :, 2] = hsv_image[:, :, 2] * 0.5  # 将 V 通道乘以 0.5
        darker_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)  # 转换回 BGR
        return darker_image
    
    def process(self,img,img_params):
        """处理图像，返回二值图像、调整大小和亮度的图像"""    
        resized = cv2.resize(img, img_params["resolution"])  # 调整图像大小
        self.darken = self.darker(cv2.convertScaleAbs(resized, alpha=0.5))  # 调整亮度 - 降低亮度
        gray = cv2.cvtColor(self.darken, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        _, self.img_binary = cv2.threshold(gray, img_params["val"], 255, cv2.THRESH_BINARY)  # 二值化处理

class Detector:
    def __init__(self, mode_params, light_params, armor_params):
        self.mode =  mode_params["display"]
        self.color = mode_params["color"]
        self.light_params = light_params  
        self.armor_params = armor_params 
        self.lights = []
        self.armors = []
        
    def adjust(self,rect):
        """调整旋转矩形的宽高和角度，使宽始终小于高"""
        c, (w, h), angle = rect
        if w > h:
            w, h = h, w  # 交换宽度和高度
            angle = (angle + 90) % 360  # 调整角度
            angle = angle - 360 if angle > 180 else angle - 180 if angle > 90 else angle  # 标准化角度：-90 到 90 度
        return c, (w, h), angle

    def project(self, polygon, axis):
        """将多边形投影到给定的轴上。辅助函数"""
        return np.dot(polygon, axis).min(), np.dot(polygon, axis).max()  # 计算最小值和最大值

    def is_coincide(self, a, b):
        """使用分离轴定理检查两个多边形是否相交。辅助函数"""
        for polygon in (a, b):
            for i in range(len(polygon)):
                p1, p2 = polygon[i], polygon[(i + 1) % len(polygon)]  # 获取边的两个端点
                normal = (p2[1] - p1[1], p1[0] - p2[0])  # 计算法向量
                min_a, max_a = self.project(a, normal)  # 计算投影的最小值和最大值
                min_b, max_b = self.project(b, normal)  # 计算投影的最小值和最大值
                if max_a < min_b or max_b < min_a:  # 检查是否相交
                    return False
    
    def find_lights(self, img, img_binary):
        """查找图像中的光源并返回旋转矩形。"""
        contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 查找灯条
        # 过滤条件合并为一个列表理解式
        lights_filtered = [
            self.adjust(cv2.minAreaRect(contour)) for contour in contours 
            if cv2.contourArea(contour) > self.light_params["light_area_min"] and self.light_params["light_angle_min"] <= self.adjust(cv2.minAreaRect(contour))[2] <= self.light_params["light_angle_max"]  # 过滤小的轮廓和大于-30°-30°的旋转矩形
        ]   
            # 进一步过滤重叠的光源
        lights_filtered = [
            light for light in lights_filtered 
            if not any(self.is_coincide(cv2.boxPoints(light).astype(int), cv2.boxPoints(other_light).astype(int)) for other_light in lights_filtered if light != other_light)  # 检查重叠
        ]
        for rect in lights_filtered:
            box = cv2.boxPoints(rect).astype(int)  # 获取旋转矩形的四个点
            mask = np.zeros(img_binary.shape, dtype=np.uint8)  # 创建掩膜
            cv2.drawContours(mask, [box], -1, 255, -1)  # 在掩膜上绘制轮廓
            masked_img = cv2.bitwise_and(img, img, mask=mask)  # 按掩膜提取区域 按位与
            sum_r, sum_b = np.sum(masked_img[:, :, 2]), np.sum(masked_img[:, :, 0])  # 计算红色和蓝色的总和
            if mode_params["color"] in [1,2] and sum_b > sum_r:       # 根据 mode 识别颜色
                self.lights.append(Light(rect, 1))  # 添加蓝色光源
            if mode_params["color"] == 0 and sum_r > sum_b:       # 根据 mode 识别颜色
            lights_blue.append(rect)  # 添加红色光源
        elif mode in [2,3]:
            (lights_red if sum_r > sum_b else lights_blue).append(rect)  # 根据颜色添加光源
    







    def detect(self, frame):
        Img.process(frame, img_params)
        
    
    

           
