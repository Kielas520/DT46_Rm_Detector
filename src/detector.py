import cv2
import numpy as np
import math

class Light:
    def __init__(self, rect, color):
        self.color = color
        self.rect = rect

class Armor:
    def __init__(self, rect):
        self.color = None
        self.rect = rect

class Img:
    def __init__(self, img):
        self.raw = img
        self.resized = None
        self.draw = None
        self.darken = None
        self.binary = None

class Detector:
    def __init__(self, mode_params, img_params, light_params, armor_params, color_params):
        self.lights = []
        self.armors = []
        self.armors_dict = {}
        self.img_params = img_params    
        self.light_params = light_params  
        self.armor_params = armor_params 
        self.mode =  mode_params["display"]
        self.color = mode_params["color"]
        self.armor_color = color_params["armor_color"]
        self.armor_id = color_params["armor_id"]
        self.light_color = color_params["light_color"]
        self.light_dot = color_params["light_dot"]
        
    def darker(self, img):
        hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 转换为 HSV 颜色空间
        hsv_image[:, :, 2] = hsv_image[:, :, 2] * 0.5  # 将 V 通道乘以 0.5
        darker_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)  # 转换回 BGR
        return darker_image
    
    def process(self, img):  
        img.resized = cv2.resize(img.raw, self.img_params["resolution"])  # 调整图像大小
        img.darken = self.darker(cv2.convertScaleAbs(img.resized, alpha=0.5))  # 调整亮度 - 降低亮度
        img.draw = img.darken.copy()
        _, img.binary = cv2.threshold(cv2.cvtColor(img.darken, cv2.COLOR_BGR2GRAY), self.img_params["val"], 255, cv2.THRESH_BINARY)  # 二值化处理

    def adjust(self,rect):
        c, (w, h), angle = rect
        if w > h:
            w, h = h, w  # 交换宽度和高度
            angle = (angle + 90) % 360  # 调整角度
            angle = angle - 360 if angle > 180 else angle - 180 if angle > 90 else angle  # 标准化角度：-90 到 90 度
        return c, (w, h), angle

    def project(self, polygon, axis):
        return np.dot(polygon, axis).min(), np.dot(polygon, axis).max()  # 计算最小值和最大值

    def is_coincide(self, a, b):
        for polygon in (a, b):
            for i in range(len(polygon)):
                p1, p2 = polygon[i], polygon[(i + 1) % len(polygon)]  # 获取边的两个端点
                normal = (p2[1] - p1[1], p1[0] - p2[0])  # 计算法向量
                min_a, max_a = self.project(a, normal)  # 计算投影的最小值和最大值
                min_b, max_b = self.project(b, normal)  # 计算投影的最小值和最大值
                if max_a < min_b or max_b < min_a:  # 检查是否相交
                    return False
    
    def find_lights(self, img, img_binary, img_draw):
        contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 查找灯条
        lights_filtered = [
            self.adjust(cv2.minAreaRect(contour)) for contour in contours 
            if cv2.contourArea(contour) > self.light_params["light_area_min"] and self.light_params["light_angle_min"] <= self.adjust(cv2.minAreaRect(contour))[2] <= self.light_params["light_angle_max"]  # 过滤小的轮廓和大于-30°-30°的旋转矩形
        ]   # 过滤条件合并为一个列表理解式
        lights_filtered = [
            light for light in lights_filtered 
            if not any(self.is_coincide(cv2.boxPoints(light).astype(int), cv2.boxPoints(other_light).astype(int)) for other_light in lights_filtered if light != other_light)  # 检查重叠
        ]   # 进一步过滤重叠的光源
        for rect in lights_filtered:
            box = cv2.boxPoints(rect).astype(int)  # 获取旋转矩形的四个点
            mask = np.zeros(img_binary.shape, dtype=np.uint8)  # 创建掩膜
            cv2.drawContours(mask, [box], -1, 255, -1)  # 在掩膜上绘制轮廓
            masked_img = cv2.bitwise_and(img, img, mask=mask)  # 按掩膜提取区域 按位与
            sum_r, sum_b = np.sum(masked_img[:, :, 2]), np.sum(masked_img[:, :, 0])  # 计算红色和蓝色的总和
            if self.color in [1,2] and sum_b > sum_r:       # 根据 mode 识别颜色
                light_blue = Light(rect, 1)
                self.lights.append(light_blue)  # 添加蓝色光源
            if self.color in [0,2] and sum_r > sum_b:       # 根据 mode 识别颜色
                light_red = Light(rect, 0)
                self.lights.append(light_red)  # 添加红色光源
        self.draw_lights(img_draw)
    
    def is_close(self,rect1, rect2, light_params):
        (cx1, cy1), (w1, h1), angle1 = rect1  # 获取第一个旋转矩形的信息
        (cx2, cy2), (w2, h2), angle2 = rect2  # 获取第二个旋转矩形的信息
        distance = math.sqrt((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2)    # 计算中心点之间的距离
        if distance > light_params["light_distance_min"] :    # 首先判断距离是否大于20
            angle_diff = min(abs(angle1 - angle2), 360 - abs(angle1 - angle2))  # 计算角度差 # 判断旋转矩形的角度是否接近
            if angle_diff <= light_params["light_angle_tol"]:  # 判断角度差是否在容忍范围内
                if abs(h1 - h2) <= light_params["height_tol"] and abs(w1 - w2) <= light_params["width_tol"]:  # 判断高宽差
                    line_angle = math.degrees(math.atan2(cy2 - cy1, cx2 - cx1))  # 计算连线角度
                    if line_angle > 90:                        # 将角度标准化到 -90° 到 90° 之间
                        line_angle -= 180  
                    elif line_angle < -90:
                        line_angle += 180   
                    if (abs(line_angle - angle1) <= light_params["line_angle_tol"] or abs(line_angle - angle2) <= light_params["line_angle_tol"] or abs(cy1-cy2)< light_params["cy_tol"]):  
                        return True                            # 检查是否垂直或者判断中心点垂直坐标差         
        return False

    def is_armor(self,lights):
        processed_indices = set()  # 用于存储已处理的矩形索引
        lights_count = len(lights)  # 存储列表长度，避免重复计算
        for i in range(lights_count):  # 使用 for 循环遍历 lights
            if i in processed_indices:  # 如果该矩形已处理，跳过
                continue
            light = lights[i]  # 取出当前矩形
            close_lights = [j for j in range(lights_count) if j != i and lights[j].color == light.color and self.is_close(light.rect, lights[j].rect, self.light_params)]  # 找到接近的光源
            if close_lights:  # 如果找到接近的矩形
                group = [light.rect] + [lights[j].rect for j in close_lights]  # 将当前矩形和接近的矩形组合成一组
                points = np.concatenate([cv2.boxPoints(light) for light in group])  # 获取所有矩形的四个顶点
                armor_raw = cv2.minAreaRect(points)  # 计算最小外接矩形
                if self.armor_params["armor_area_min"] <= armor_raw[1][0] * armor_raw[1][1] <= self.armor_params["armor_area_max"] : # 限制识别到的装甲板面积大小
                    armor_flit = self.adjust(armor_raw)
                    if self.armor_params["armor_height/width_min"] <= armor_flit[1][1] / armor_flit[1][0] <= self.armor_params["armor_height/width_max"]:  # 限制识别到的装甲矩形高宽比
                        armor = Armor(self.adjust(armor_flit))
                        armor.color = light.color
                        self.armors.append(armor)
                        processed_indices.update([i] + close_lights)# 将已处理的矩形索引添加到 processed_indices 中

    def id_armor(self):
        for armor in self.armors:  # 遍历所有装甲矩形
            center, (width, height), angle = armor.rect  # 获取装甲矩形的中心、宽高和角度
            max_size = max(width, height)  # 计算最大尺寸
            self.armors_dict[f"{int(center[0])}"] = {        # 添加装甲信息到字典
                "armor_id": self.armor_color[armor.color],  # 添加 armor_id
                "height": int(max_size),  # 添加高度
                "center": [int(center[0]), int(center[1])]  # 添加中心点
            }
    
    def find_armor(self, img):
        self.is_armor(self.lights)  # 查找装甲
        self.id_armor()
        self.draw_armors(img)

    def draw_lights(self,img):
        for light in self.lights:
            box = cv2.boxPoints(light.rect).astype(int)  # 获取轮廓点
            cv2.drawContours(img, [box], 0, self.light_color[light.color], 1)  # 绘制紫色轮廓
            cv2.circle(img, tuple(map(int, light.rect[0])), 1, self.light_dot[light.color], -1)  # 绘制红色中心点

    def draw_armors(self, img):
        for armor in self.armors:
            center, (max_size, max_size), angle = armor.rect
            box = cv2.boxPoints(((center[0], center[1]), (max_size, max_size), angle)).astype(int)  # 获取装甲的四个顶点
            cv2.drawContours(img, [box], 0, self.armor_color[armor.color], 2)  # 绘制装甲的轮廓
            cv2.circle(img, (int(center[0]), int(center[1])), 5, self.armor_color[armor.color], -1)  # 绘制装甲中心点
            center_x, center_y = map(int, armor.rect[0])  # 获取中心坐标
            cv2.putText(img, f"({center_x}, {center_y})", (center_x, center_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 255, 255), 2)  # 在图像上标记坐标
            
    def display(self,img):
        cv2.imshow("Detected", img.draw)
        cv2.imshow("Binary", img.binary)        #cv2.imshow("Raw_Resized", img.resized)
        
    def detect(self, frame):
        frame = Img(frame)
        self.process(frame)
        self.find_lights(frame.darken, frame.binary, frame.draw)
        self.find_armor(frame.draw)
        if self.mode == 1 : self.display(frame)  # noqa: E701
        print(self.armors_dict)
        
if __name__ == "__main__":
    mode_params = {"display": 1 , "color": 2}
    light_params = {"light_distance_min": 20, "light_area_min": 5, 
                    "light_angle_min": -30, "light_angle_max": 30, 
                    "light_angle_tol": 5, "line_angle_tol": 7, 
                    "height_tol": 10, "width_tol": 10, "cy_tol": 5}
    armor_params = {"armor_height/width_max": 3.5,"armor_height/width_min": 1,
                    "armor_area_max": 11000,"armor_area_min": 200}
    img_params = {"resolution": (640,480) , 
                  "val": 35}
    color_params = {"armor_color":{1: (255, 255, 0), 0: (128, 0, 128)}, "armor_id":{1: 1, 0: 7}, 
                    "light_color":{1: (200, 71, 90), 0: (0, 100, 255)}, "light_dot":{1: (0, 0, 255), 0: (255, 0, 0)}}
    detector = Detector(mode_params, img_params, light_params, armor_params, color_params)
    detector.detect(cv2.imread('./photo/red_2.jpg'))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    

           
