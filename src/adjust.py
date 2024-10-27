import cv2  # 导入 OpenCV 库

class Adjust:
    def __init__(self, light_params, armor_params, binary_val):
        self.flag = False
        self.light_params = light_params        # 灯条参数字典
        self.armor_params = armor_params       # 装甲板参数字典
        self.binary_val = binary_val           # 图像参数字典

    # 更新图像参数的函数
    def img_val(self,new_val):
        self.binary_val = new_val  # 更新图像参数
        self.flag = True

    # 更新装甲板参数的函数（面积最大）
    def armor_area_max(self, param, new_armor_area_max):
        self.armor_params[param] = new_armor_area_max  # 更新装甲板最大面积参数
        self.flag = True

    # 更新装甲板参数的函数（高度宽度最大）
    def armor_heightwidth_max(self, param, new_armor_heightwidth_max):
        new_armor_heightwidth_max = new_armor_heightwidth_max / 10  # 将新值除以10
        self.armor_params[param] = new_armor_heightwidth_max  # 更新装甲板高度宽度最大参数
        self.flag = True

    # 更新装甲板参数的函数（面积最小）
    def armor_area_min(self, param, new_armor_area_min):
        self.armor_params[param] = new_armor_area_min  # 更新装甲板最小面积参数
        self.flag = True

    # 更新灯条参数的函数（最小灯条距离）
    def light_distance_min(self, param, new_light_distance_min):
        self.light_params[param] = new_light_distance_min  # 更新最小灯条距离参数
        self.flag = True

    # 更新灯条参数的函数（最小灯条面积）
    def light_area_min(self, param, new_light_area_min):
        self.light_params[param] = new_light_area_min  # 更新最小灯条面积参数
        self.flag = True

    # 更新灯条参数的函数（高度容差）
    def height_tol(self, param, new_height_tol):
        self.light_params[param] = new_height_tol  # 更新高度容差参数
        self.flag = True

    # 更新灯条参数的函数（宽度容差）
    def width_tol(self, param, new_width_tol):
        self.light_params[param] = new_width_tol  # 更新宽度容差参数
        self.flag = True

    # 更新灯条参数的函数（中心点y轴容差）
    def cy_tol(self, param, new_cy_tol):
        self.light_params[param] = new_cy_tol  # 更新中心点y轴容差参数
        self.flag = True

    # 更新灯条参数的函数（灯条角度容差）
    def light_angle_tol(self, param, new_light_angle_tol):
        self.light_params[param] = new_light_angle_tol  # 更新灯条角度容差参数
        self.flag = True

    # 更新灯条参数的函数（线角度容差）
    def line_angle_tol(self, param, new_line_angle_tol):
        self.light_params[param] = new_line_angle_tol  # 更新线角度容差参数
        self.flag = True

    # 创建窗口和滑动条的函数
    def setup_windows(self):
        # 创建窗口
        cv2.namedWindow("params")  # 创建名为"params"的窗口
        cv2.resizeWindow("params", (640, 445))  # 调整窗口大小
        # 创建图像参数滑动条
        cv2.createTrackbar("bin_val", "params", self.binary_val, 255, lambda new_val: self.img_val(new_val))  # 创建阈值滑动条
        # 创建装甲板参数滑动条
        cv2.createTrackbar("arm_max", "params", self.armor_params["armor_area_max"], 85000, lambda new_armor_area_max: self.armor_area_max("armor_area_max", new_armor_area_max))  # 创建装甲板面积最大滑动条
        cv2.createTrackbar("arm_min", "params", self.armor_params["armor_area_min"], 1500, lambda new_armor_area_min: self.armor_area_min("armor_area_min", new_armor_area_min))  # 创建装甲板面积最小滑动条
        cv2.createTrackbar("h/w", "params", int(self.armor_params["armor_height/width_max"] * 10), 80, lambda new_armor_heightwidth_max: self.armor_heightwidth_max("armor_height/width_max", new_armor_heightwidth_max))  # 创建装甲板高度宽度最大滑动条
        # 添加灯条参数的滑动条
        cv2.createTrackbar("distance", "params", self.light_params["light_distance_min"], 200, lambda new_light_distance_min: self.light_distance_min("light_distance_min", new_light_distance_min))  # 创建最小灯条距离滑动条
        cv2.createTrackbar("area", "params", self.light_params["light_area_min"], 300, lambda new_light_area_min: self.light_area_min("light_area_min", new_light_area_min))  # 创建最小灯条面积滑动条
        cv2.createTrackbar("height", "params", self.light_params["height_tol"], 500, lambda new_height_tol: self.height_tol("height_tol", new_height_tol))  # 创建高度容差滑动条
        cv2.createTrackbar("width", "params", self.light_params["width_tol"], 500, lambda new_width_tol: self.width_tol("width_tol", new_width_tol))  # 创建宽度容差滑动条
        cv2.createTrackbar("cy", "params", self.light_params["cy_tol"], 200, lambda new_cy_tol: self.cy_tol("cy_tol", new_cy_tol))  # 创建中心点y轴容差滑动条
        cv2.createTrackbar("lit_ang", "params", self.light_params["light_angle_tol"], 50, lambda new_light_angle_tol: self.light_angle_tol("light_angle_tol", new_light_angle_tol))  # 创建灯条角度容差滑动条
        cv2.createTrackbar("lin_ang", "params", self.light_params["line_angle_tol"], 50, lambda new_line_angle_tol: self.line_angle_tol("line_angle_tol", new_line_angle_tol))  # 创建线角度容差滑动条
