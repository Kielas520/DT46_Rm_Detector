import cv2
import numpy as np
import math

RED = 0
BLUE = 1
BOTH = 2

mode_params = {"display": 0 , "color": 2}
light_params = {"light_distance_min": 20, "light_area_min": 5, "light_angle_min": -30, "light_angle_max": 30, "light_angle_tol": 5, "line_angle_tol": 7, "height_tol": 10, "width_tol": 10, "cy_tol": 5}
armor_params = {"armor_height/width_max": 3.5,"armor_height/width_min": 1,"armor_area_max": 11000,"armor_area_min": 200}
img_params = {"resolution": (640,480) , "val": 35}

class Light:
    def __init__(self, rect, color):
        self.color = color
        self.rect = rect

# 定义装甲板类
class Armor:
    def __init__(self, rect, color):
        self.rect = rect
        self.color = color
        self.id = None
        


class Img:
    def __init__(self):
        self.darken = None
        self.binary = None
        self.draw = self.darken.copy()

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
        self.color_map = {1: (255, 255, 0), 0: (128, 0, 128)}  # 蓝色和红色的颜色映射
        self.class_map = {1: 1, 0: 7}  # 蓝色和红色的 class_id 映射
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
            if self.color in [1,2] and sum_b > sum_r:       # 根据 mode 识别颜色
                self.lights_blue.append(Light(rect, 1))  # 添加蓝色光源
            if self.color == [0,2] and sum_r > sum_b:       # 根据 mode 识别颜色
                self.lights_red.append(Light(rect, 0))  # 添加红色光源
    
    def draw_lights(self):
        """在图像上绘制光源。"""
        for Light in self.lights:
            if Light.color == 0:
                box = cv2.boxPoints(Light.rect).astype(int)  # 获取轮廓点
                cv2.drawContours(Img.draw, [box], 0, (0, 100, 255), 1)  # 绘制橙色轮廓
                cv2.circle(Img.draw, tuple(map(int, Light.rect[0])), 3, (255, 0, 0), -1)  # 绘制蓝色中心点
            if Light.color == 1:
                box = cv2.boxPoints(Light.rect).astype(int)  # 获取轮廓点
                cv2.drawContours(Img.draw, [box], 0, (200, 71, 90), 1)  # 绘制紫色轮廓
                cv2.circle(Img.draw, tuple(map(int, Light.rect[0])), 1, (0, 0, 255), -1)  # 绘制红色中心点
    
    def is_close(self,rect1, rect2,light_params):
        """检查两个灯条(旋转矩形)是否足够相似。辅助函数"""
        (cx1, cy1), (w1, h1), angle1 = rect1  # 获取第一个旋转矩形的信息
        (cx2, cy2), (w2, h2), angle2 = rect2  # 获取第二个旋转矩形的信息
        distance = math.sqrt((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2)    # 计算中心点之间的距离
        
        if distance > 20 :    # 首先判断距离是否大于20
            angle_diff = min(abs(angle1 - angle2), 360 - abs(angle1 - angle2))  # 计算角度差 # 判断旋转矩形的角度是否接近
            if angle_diff <= light_params["light_angle_tol"]:  # 判断角度差是否在容忍范围内
                if abs(h1 - h2) <= light_params["height_tol"] and abs(w1 - w2) <= light_params["width_tol"]:  # 判断高宽差
                    line_angle = math.degrees(math.atan2(cy2 - cy1, cx2 - cx1))  # 计算连线角度
                    # 将角度标准化到 -90° 到 90° 之间
                    if line_angle > 90:    
                        line_angle -= 180  # 标准化处理
                    elif line_angle < -90:
                        line_angle += 180  # 标准化处理
                    # 检查是否垂直或者判断中心点垂直坐标差  
                    if (abs(line_angle - angle1) <= light_params["line_angle_tol"] or abs(line_angle - angle2) <= light_params["line_angle_tol"] or abs(cy1-cy2)< light_params["cy_tol"]):  
                        return True                
        return False

    def is_armor(self,lights):
        """匹配灯条，找装甲板"""
        armors = []  # 存放装甲信息= []  # 存放匹配的光源组
        processed_indices = set()  # 用于存储已处理的矩形索引
        lights_count = len(lights)  # 存储列表长度，避免重复计算

        for i in range(lights_count):  # 使用 for 循环遍历 lights
            if i in processed_indices:  # 如果该矩形已处理，跳过
                continue
            
            light1 = lights[i]  # 取出当前矩形
            close_lights = [j for j in range(lights_count) if j != i and lights[j].color == light1.color and self.is_close(light1.rect, lights[j].rect, self.light_params)]  # 找到接近的光源
            
            if close_lights:  # 如果找到接近的矩形
                group = [light1] + [lights[j] for j in close_lights]  # 将当前矩形和接近的矩形组合成一组
                points = np.concatenate(cv2.boxPoints(group))  # 获取所有矩形的四个顶点
                armor_raw = cv2.minAreaRect(points)  # 计算最小外接矩形
                if self.armor_params["armor_area_min"] <= armor_raw[1][0] * armor_raw[1][1] <= self.armor_params["armor_area_max"] : # 限制识别到的装甲板面积大小
                    armor_flit = self.adjust(armor_raw)
                    if self.armor_params["armor_height/width_min"] <= armor_flit[1][1] / armor_flit[1][0] <= self.armor_params["armor_height/width_max"]:  # 限制识别到的装甲矩形高宽比
                        armors.append(Armor(self.adjust(armor_flit), light1.color)) 
                processed_indices.update([i] + close_lights)# 将已处理的矩形索引添加到 processed_indices 中
                
        return armors  # 返回装甲信息

    def draw_armors(self, armors):
        """在图像上绘制装甲板。"""
        for armor in armors:
            center, (max_size, max_size), angle = armor
            box = cv2.boxPoints(((center[0], center[1]), (max_size, max_size), angle)).astype(int)  # 获取装甲的四个顶点
            cv2.drawContours(Img.draw, [box], 0, self.color_map[armor.color], 2)  # 绘制装甲的轮廓
            cv2.circle(Img.draw, (int(center[0]), int(center[1])), 5, self.color_map[armor.color], -1)  # 绘制装甲中心点
            center_x, center_y = map(int, armor[0])  # 获取中心坐标
            cv2.putText(Img.draw, f"({center_x}, {center_y})", (center_x, center_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 255, 255), 2)  # 在图像上标记坐标

    def id_armor(self, armors):
        """为装甲矩形标记信息并在图像上绘制轮廓。"""
        armors_dict = {}  # 存储装甲信息的字典
        
        for armor in armors:  # 遍历所有装甲矩形
            if armor.color not in self.color_map:    # 提前判断 class_id 是否在 color_map 中
                return armors_dict  # 如果不在，直接返回空的字典
            center, (width, height), angle = armor.rect  # 获取装甲矩形的中心、宽高和角度
            max_size = max(width, height)  # 计算最大尺寸
            armors_dict[f"{int(center[0])}"] = {        # 添加装甲信息到字典
                "class_id": self.class_map[armor.color],  # 添加 class_id
                "height": int(max_size),  # 添加高度
                "center": [int(center[0]), int(center[1])]  # 添加中心点
            }

        return armors_dict  # 返回装甲信息字典
    
    def find_armor(self):
        """识别装甲类型并返回装甲字典"""
        armors_dict, armors = {}, []  # 初始化装甲字典和列表
        armors = self.is_armor(self.lights_red)  # 查找装甲
        armors_dict.update(self.id_armor(armors))  # 添加装甲到列表    
        return armors_dict  # 返回装甲字典

    def detect(self, frame):
        Img.process(frame, img_params)
        armors_dict = self.find_armor(self.find_lights(Img.darken, Img.binary))
        print(armors_dict)
        
if __name__ == "__main__":
    frame = cv2.imread('./photo/blue_2.jpg')
    Detector.detect(frame)
    
    

           
