import cv2  # 导入 OpenCV 库
import numpy as np  # 导入 NumPy 库
import math  # 导入数学库
from loguru import logger
import time  # 导入时间库

def calculate_distance(point1, point2):
    x1, y1 = point1  # 解包第一个点的坐标
    x2, y2 = point2  # 解包第二个点的坐标
    # 使用距离公式计算并返回结果
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

def time_logger(func):  # 定义装饰器
    def wrapper(*args, **kwargs):  # 包装函数
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 调用原函数
        end_time = time.time()  # 记录结束时间
        print(f"函数 '{func.__name__}' 的运行时间: {end_time - start_time:.5f} 秒")  # 打印运行时间
        return result  # 返回原函数的结果
    return wrapper

class Light:  # 定义灯条类
    def __init__(self, up, down, angle, color):  # 初始化灯条的矩形和颜色
        self.cx = int(abs(up[0] - down[0]) / 2 + min(up[0], down[0]))
        self.cy = int(abs(up[1] - down[1]) / 2 + min(up[1], down[1]))
        self.height = calculate_distance(up, down)
        self.angle = angle
        self.color = color  # 设置灯条颜色
        self.up = up
        self.down = down

class Armor:  # 定义装甲板类
    def __init__(self, center):  # 初始化装甲板的矩形
        self.color = None  # 装甲板颜色初始化为 None
        self.center = center
        self.height = None
        self.light1_up = None
        self.light1_down = None
        self.light2_up = None
        self.light2_down = None


class Detector:  # 定义检测器类
    def __init__(self, detect_mode, binary_val, light_params, color_params):  # 初始化检测器
        self.img = None
        self.img_binary = None
        self.img_darken = None
        self.binary_val = binary_val  # 二值化阈值
        self.color = detect_mode  # 颜色模式
        self.light_params = light_params  # 灯条参数
        self.armor_color = color_params["armor_color"]  # 装甲板颜色映射
        self.armor_id = color_params["armor_id"]  # 装甲板 ID 映射
        self.light_color = color_params["light_color"]  # 灯条颜色映射
        self.light_dot = color_params["light_dot"]  # 灯条中心点颜色映射
        self.lights = []  # 存储灯条列表
        self.armors = []  # 存储装甲板列表
        self.armors_dict = {}  # 存储装甲板信息的字典
        self.light_min_distance = None
        self.light_distance = light_params["light_distance"]

    @time_logger
    def process(self, img):  # 处理图像的函数
        self.img = img
        _, self.img_binary = cv2.threshold(cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY), self.binary_val, 255, cv2.THRESH_BINARY)  # 二值化处理
        return self.img_binary
 
    def adjust(self, rect):  # 调整矩形的函数
        c, (w, h), angle = rect  # 解包矩形的中心、宽高和角度
        if w > h:  # 如果宽度大于高度
            w, h = h, w  # 交换宽度和高度
            angle = (angle + 90) % 360  # 调整角度
            angle = angle - 360 if angle > 180 else angle - 180 if angle > 90 else angle  # 标准化角度：-90 到 90 度
        return c, (w, h), angle  # 返回调整后的结果

    def project(self, polygon, axis):  # 投影计算
        return np.dot(polygon, axis).min(), np.dot(polygon, axis).max()  # 计算最小值和最大值

    def is_coincide(self, a, b):  # 检查两个多边形是否重叠
        for polygon in (a, b):  # 遍历多边形 a 和 b
            for i in range(len(polygon)):  # 遍历每个多边形的边
                p1, p2 = polygon[i], polygon[(i + 1) % len(polygon)]  # 获取边的两个端点
                normal = (p2[1] - p1[1], p1[0] - p2[0])  # 计算法向量
                min_a, max_a = self.project(a, normal)  # 计算多边形 a 的投影的最小值和最大值
                min_b, max_b = self.project(b, normal)  # 计算多边形 b 的投影的最小值和最大值
                if max_a < min_b or max_b < min_a:  # 检查是否相交
                    return False  # 不相交则返回 False
                
    @time_logger    
    def find_lights(self, img_binary):  # 查找灯条的函数
        lights = []
        contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓
        lights_filtered = [  # 过滤灯条
            self.adjust(cv2.minAreaRect(contour)) for contour in contours 
            if cv2.contourArea(contour) > self.light_params["light_area_min"] and self.light_params["light_angle_min"] <= self.adjust(cv2.minAreaRect(contour))[2] <= self.light_params["light_angle_max"]  # 过滤小轮廓和大于-30°到30°的旋转矩形
        ]  # 过滤条件合并为一个列表理解式
        lights_filtered = [  # 进一步过滤重叠的灯条
            light for light in lights_filtered 
            if not any(self.is_coincide(cv2.boxPoints(light).astype(int), cv2.boxPoints(other_light).astype(int)) for other_light in lights_filtered if light != other_light)  # 检查重叠
        ]  
        for rect in lights_filtered:  # 遍历过滤后的灯条
            box = cv2.boxPoints(rect).astype(int)  # 获取旋转矩形的四个点
            
            # 通过角点裁剪出对应的区域
            right_up_x, right_up_y = box[0]
            left_up_x, left_up_y = box[3]

            up_x = int(abs(right_up_x - left_up_x) / 2 + min(right_up_x, left_up_x))
            up_y = int(abs(right_up_y - left_up_y) / 2 + min(right_up_y, left_up_y))
            up = (up_x, up_y)

            right_down_x, right_down_y = box[1]
            left_down_x, left_down_y = box[2]
            
            down_x = int((abs(right_down_x - left_down_x) / 2 + min(right_down_x, left_down_x)))
            down_y = int((abs(right_down_y - left_down_y) / 2 + min(right_down_y, left_down_y)))
            down = (down_x, down_y)

            # 计算线段的长度
            length = int(np.sqrt((down_x - up_x) ** 2 + (down_y - up_y) ** 2))
            # 创建一个新图像以存储裁剪的线段像素
            roi = np.zeros((1, length, 3), dtype=np.uint8)

            # 计算线段上的每个像素
            for i in range(length):
                # 计算当前像素的坐标
                t = i / length  # 计算比例
                current_x = int(up_x + (down_x - up_x) * t)
                current_y = int(up_y + (down_y - up_y) * t)
                            
                # 添加边界检查
                if 0 <= current_x < self.img.shape[1] and 0 <= current_y < self.img.shape[0]:
                    roi[0, i] = self.img[current_y, current_x]  # 保存像素值

            #计算裁剪图像的红色和蓝色的总和
            sum_r, sum_b = np.sum(roi[:, :, 2]), np.sum(roi[:, :, 0])  # 计算红色和蓝色的总和
            if self.color in [1, 2] and sum_b > sum_r:  # 根据模式识别颜色
                light_blue = Light(up, down, rect[2],  1)  # 创建蓝色灯条对象
                lights.append(light_blue)  # 添加蓝色灯条
            if self.color in [0, 2] and sum_r > sum_b:  # 根据模式识别颜色
                light_red = Light(up, down, rect[2], 0)  # 创建红色灯条对象
                lights.append(light_red)  # 添加红色灯条
        self.lights = lights
        return self.lights
    
    def angle_to_slope(self, angle_degrees):
        # 将角度转换为弧度
        angle_radians = math.radians(angle_degrees)
        # 计算斜率
        slope = math.tan(angle_radians)
        return slope
        
    def is_close(self, light1, light2, light_params):  # 检查两个矩形是否接近
        distance = calculate_distance((light1.cx, light1.cy), (light2.cx, light2.cy))
        angle_diff = min(abs(light1.angle - light2.angle), 360 - abs(light1.angle - light2.angle))  # 计算角度差
        print(light1.angle)
        if angle_diff <= light_params["light_angle_tol"]:  # 判断角度差是否在容忍范围内
            if abs(light1.height - light2.height) <= light_params["height_tol"]:  # 判断高差
                line_angle = math.degrees(math.atan2(light1.cy - light2.cy, light1.cx - light2.cx))  # 计算连线角度

                if line_angle <= 270  and line_angle > 180:
                    line_angle = 270 - line_angle  # 计算补角
                if line_angle <= 180  and line_angle > 90:
                    line_angle = -(line_angle - 90)  # 计算补角 
                if line_angle <= 90  and line_angle > 0:
                    line_angle = 90 - line_angle                     
                if line_angle <= 360  and line_angle > 270:
                    line_angle = -(line_angle - 270)             
                #if abs(line_angle - light1.angle) >= light_params["line_angle_tol"] and abs(line_angle - light2.angle) >= light_params["line_angle_tol"] : 
                real_distance = min(light1.height, light2.height)
                # 计算斜率
                slope1 = self.angle_to_slope(light1.angle)
                slope2 = self.angle_to_slope(light2.angle)           
                slope_line = self.angle_to_slope(line_angle)
                
                if abs(slope1 * slope_line + 1) < light_params["line_angle_tol"] and abs(slope2 * slope_line + 1) < light_params["line_angle_tol"]:
                    cv2.line(self.img, (light1.cx, light1.cy),(light2.cx,light2.cy), (0, 255, 0), 2)  # 绿色线条，厚度为2
                    if distance > real_distance and distance < distance * light_params["light_distance"]:
                        self.light_min_distance = real_distance
                        return True, distance # 检查是否垂直或者判断中心点垂直坐标差 
                    elif abs(light1.cy - light2.cy) < light_params["cy_tol"]: 
                        real_distance = min(light1.height, light2.height)
                        if distance > real_distance and distance < distance * light_params["light_distance"]:
                            self.light_min_distance = real_distance
                            return True, distance # 检查是否垂直或者判断中心点垂直坐标差 
        return False, None # 不满足条件则返回 False
    @time_logger
    def is_armor(self, lights):  # 检查是否为装甲板的函数
        armors = []
        processed_indices = set()  # 用于存储已处理的矩形索引
        lights_count = len(lights)  # 存储列表长度，避免重复计算
        for i in range(lights_count):  # 遍历所有灯条
            if i in processed_indices:  # 如果该矩形已处理，跳过
                continue
            light = lights[i]  # 取出当前灯条
            for j in range(lights_count) : 
                if j != i and lights[j].color == light.color :  # 如果找到接近的灯条
                    close, real_distance = self.is_close(light, lights[j], self.light_params)
                    if close == True and real_distance is not None :
                        armor_cx = int(abs(light.cx - lights[j].cx) / 2 + min(light.cx, lights[j].cx))
                        armor_cy = int(abs(light.cy - lights[j].cy) / 2 + min(light.cy, lights[j].cy))
                        armor_center = (armor_cx, armor_cy)
                        armor = Armor(armor_center)  # 创建装甲板对象
                        armor.height = self.light_distance
                        armor.light1_up = light.up
                        armor.light1_down = light.down
                        armor.light2_up = lights[j].up
                        armor.light2_down = lights[j].down
                        armor.color = light.color  # 设置装甲板颜色
                        armors.append(armor)  # 添加装甲板到列表
                        processed_indices.update([i])  # 将已处理的矩形索引添加到 processed_indices 中
                        processed_indices.update([j])  # 将已处理的矩形索引添加到 processed_indices 中
        self.armors = armors
        return self.armors
    @time_logger
    def id_armor(self):  # 为装甲板分配 ID 的函数
        armors_dict = {}
        for armor in self.armors:  # 遍历所有装甲板矩形
            center = armor.center
            armors_dict[f"{int(center[0])}"] = {  # 添加装甲板信息到字典
                "armor_id": self.armor_color[armor.color],  # 添加 armor_id
                "height": int(armor.height),  # 添加高度
                "center": [int(center[0]), int(center[1])]  # 添加中心点
            }
        self.armors_dict = armors_dict
        return self.armors_dict
    @time_logger    
    def find_armor(self):  # 查找装甲板的函数
        self.is_armor(self.lights)  # 查找装甲板
        self.id_armor()  # 为装甲板分配 ID

    def draw_lights(self, img):  # 绘制灯条的函数
        for light in self.lights:  # 遍历灯条
        # 绘制直线
            cv2.line(img, light.up, light.down, self.light_color[light.color], 1) 
            # 绘制中心点
            cv2.circle(img, (light.cx, light.cy), 5, self.light_dot[light.color], -1)  # 5是半径，-1表示填充
        return img

    def draw_armors(self, img):  # 绘制装甲板的函数
        for armor in self.armors:  # 遍历装甲板
            center = armor.center
            cv2.line(img, armor.light1_up, armor.light2_down, self.armor_color[armor.color], 1) 
            cv2.line(img, armor.light2_up, armor.light1_down, self.armor_color[armor.color], 1) 
            center_x, center_y = map(int, center)  # 获取中心坐标
            cv2.putText(img, f"({center_x}, {center_y})", (center_x, center_y),  # 在图像上标记坐标
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 255, 255), 2)  # 绘制文本
        return img

    def draw_img(self):
        drawn = self.img.copy()
        drawn = self.draw_armors(drawn)  # 绘制装甲板
        drawn = self.draw_lights(drawn)  # 绘制灯条
        return drawn

    def display(self):  # 显示图像的函数
        cv2.namedWindow("Binary",cv2.WINDOW_NORMAL)       
        cv2.imshow("Binary", self.img_binary)  # 显示二值化图像
        drawn = self.draw_img()
        cv2.namedWindow("Detected",cv2.WINDOW_NORMAL)
        cv2.imshow("Detected", drawn)      # cv2.namedWindow("raw",cv2.WINDOW_NORMAL) # cv2.imshow("raw", self.img)       
    @time_logger        
    def detect(self, frame):  # 检测函数
        frame_binary = self.process(frame)  # 处理图像
        self.find_lights(frame_binary)  # 查找灯条
        self.find_armor()  # 查找装甲板        print(self.armors_dict)  # 打印装甲板信息字典
        return self.armors_dict
        
if __name__ == "__main__":  # 主程序入口
    # 模式参数字典
    detect_mode =  2  # 颜色参数 0: 识别红色装甲板, 1: 识别蓝色装甲板, 2: 识别全部装甲板
    # 图像参数字典
    binary_val = 170  
    # 灯条参数字典
    light_params = {
        "light_area_min": 5,  # 最小灯条面积
        "light_angle_min": -35,  # 最小灯条角度
        "light_angle_max": 35,  # 最大灯条角度
        "light_angle_tol": 6,  # 灯条角度容差
        "line_angle_tol": 1.1,  # 线角度容差
        "height_tol": 15,  # 高度容差
        "cy_tol": 5,  # 中心点的y轴容差
        "light_distance": 1.5
    }

    # 颜色参数字典
    color_params = {
        "armor_color": {1: (255, 255, 0), 0: (128, 0, 128)},  # 装甲板颜色映射
        "armor_id": {1: 1, 0: 7},  # 装甲板 ID 映射
        "light_color": {1: (200, 71, 90), 0: (0, 100, 255)},  # 灯条颜色映射
        "light_dot": {1: (0, 0, 255), 0: (255, 0, 0)}  # 灯条中心点颜色映射
    }
    detector = Detector(detect_mode, binary_val, light_params, color_params)  # 创建检测器对象
    info = detector.detect(cv2.imread('./photo/red_2.jpg'))  # 读取图像并进行检测
    logger.info(info) # 打印检测结果
    detector.display()  # 显示图像
    cv2.waitKey(0)  # 等待按键
    cv2.destroyAllWindows()  # 关闭所有窗口