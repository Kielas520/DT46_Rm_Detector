import cv2  # 导入 OpenCV 库

class Adjust:
    def __init__(self, light_params,binary_val):
        self.flag = False
        self.light_params = light_params        # 灯条参数字典
        self.binary_val = binary_val           # 图像参数字典

    # 更新图像参数的函数
    def img_val(self,new_val):
        self.binary_val = new_val  # 更新图像参数
        self.flag = True

    # 更新灯条参数的函数（最小灯条面积）
    def light_area_min(self, param, new_light_area_min):
        self.light_params[param] = new_light_area_min  # 更新最小灯条面积参数
        self.flag = True

    # 更新灯条参数的函数（高度容差）
    def height_tol(self, param, new_height_tol):
        self.light_params[param] = new_height_tol  # 更新高度容差参数
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
    def vertical_discretization(self, param, new_vertical_discretization):
        self.light_params[param] = new_vertical_discretization / 1000 # 更新线角度容差参数
        self.flag = True

        # 更新灯条参数的函数（线角度容差）
    def height_multiplier(self, param, new_height_multiplier):
        self.light_params[param] = new_height_multiplier  # 更新线角度容差参数
        self.flag = True

    def setup_windows(self):
        # 创建窗口
        cv2.namedWindow("params")  # 创建名为"params"的窗口
        cv2.resizeWindow("params", (640, 445))  # 调整窗口大小
        # 创建图像参数滑动条
        cv2.createTrackbar("bin_val", "params", self.binary_val, 255, lambda new_val: self.img_val(new_val))  # 创建阈值滑动条
        # 添加灯条参数的滑动条
        cv2.createTrackbar("area", "params", self.light_params["light_area_min"], 300, lambda new_light_area_min: self.light_area_min("light_area_min", new_light_area_min))  # 创建最小灯条面积滑动条
        cv2.createTrackbar("height", "params", self.light_params["height_tol"], 100, lambda new_height_tol: self.height_tol("height_tol", new_height_tol))  # 创建高度容差滑动条
        cv2.createTrackbar("cy", "params", self.light_params["cy_tol"], 50, lambda new_cy_tol: self.cy_tol("cy_tol", new_cy_tol))  # 创建中心点y轴容差滑动条
        cv2.createTrackbar("lit_ang", "params", self.light_params["light_angle_tol"], 50, lambda new_light_angle_tol: self.light_angle_tol("light_angle_tol", new_light_angle_tol))  # 创建灯条角度容差滑动条
        cv2.createTrackbar("vertical_discretization", "params", self.light_params["vertical_discretization"], 3000, lambda new_vertical_discretization: self.vertical_discretization("vertical_discretization", new_vertical_discretization))  # 创建线角度容差滑动条
        cv2.createTrackbar("height_multiplier", "params", self.light_params["height_multiplier"], 50, lambda new_height_multiplier: self.height_multiplier("height_multiplier", new_height_multiplier))  # 创建高度倍率滑动条