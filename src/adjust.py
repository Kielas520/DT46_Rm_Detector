import cv2  # 导入 OpenCV 库

# 灯条参数字典
light_params = {
    "light_distance_min": 20,  # 最小灯条距离
    "light_area_min": 5,  # 最小灯条面积
    "light_angle_min": -35,  # 最小灯条角度
    "light_angle_max": 35,  # 最大灯条角度
    "light_angle_tol": 5,  # 灯条角度容差
    "line_angle_tol": 7,  # 线角度容差
    "height_tol": 10,  # 高度容差
    "width_tol": 10,  # 宽度容差
    "cy_tol": 5  # 中心点的y轴容差
}

# 装甲板参数字典
armor_params = {
    "armor_height/width_max": 3.5,  # 装甲板高度与宽度最大比值
    "armor_height/width_min": 1,  # 装甲板高度与宽度最小比值
    "armor_area_max": 11000,  # 装甲板最大面积
    "armor_area_min": 200  # 装甲板最小面积
}

# 图像参数字典
img_params = {
    "resolution": (640, 480),  # 图像分辨率
    "val": 35  # 参数值
}

# 更新图像参数的函数
def update_img_param(param, new_val):
    img_params[param] = new_val  # 更新图像参数

# 更新装甲板参数的函数（面积最大）
def update_armor_params1(param, new_armor_area_max):
    armor_params[param] = new_armor_area_max  # 更新装甲板最大面积参数

# 更新装甲板参数的函数（高度宽度最大）
def update_armor_params2(param, new_armor_heightwidth_max):
    new_armor_heightwidth_max = new_armor_heightwidth_max / 10  # 将新值除以10
    armor_params[param] = new_armor_heightwidth_max  # 更新装甲板高度宽度最大参数

# 更新装甲板参数的函数（面积最小）
def update_armor_params3(param, new_armor_area_min):
    armor_params[param] = new_armor_area_min  # 更新装甲板最小面积参数

# 更新灯条参数的函数（最小灯条距离）
def light_params1(param, new_light_distance_min):
    light_params[param] = new_light_distance_min  # 更新最小灯条距离参数

# 更新灯条参数的函数（最小灯条面积）
def light_params2(param, new_light_area_min):
    light_params[param] = new_light_area_min  # 更新最小灯条面积参数

# 更新灯条参数的函数（高度容差）
def light_params3(param, new_height_tol):
    light_params[param] = new_height_tol  # 更新高度容差参数

# 更新灯条参数的函数（宽度容差）
def light_params4(param, new_width_tol):
    light_params[param] = new_width_tol  # 更新宽度容差参数

# 更新灯条参数的函数（中心点y轴容差）
def light_params5(param, new_cy_tol):
    light_params[param] = new_cy_tol  # 更新中心点y轴容差参数

# 更新灯条参数的函数（灯条角度容差）
def light_params6(param, new_light_angle_tol):
    light_params[param] = new_light_angle_tol  # 更新灯条角度容差参数

# 更新灯条参数的函数（线角度容差）
def light_params7(param, new_line_angle_tol):
    light_params[param] = new_line_angle_tol  # 更新线角度容差参数

# 创建窗口和滑动条的函数
def setup_windows():
    # 创建窗口
    cv2.namedWindow("params")  # 创建名为"params"的窗口
    cv2.resizeWindow("params", (640, 445))  # 调整窗口大小

    # 创建滑动条
    cv2.createTrackbar("Thresh", "params", img_params["val"], 255, lambda new_val: update_img_param("val", new_val))  # 创建阈值滑动条

    cv2.createTrackbar("arm_max", "params", armor_params["armor_area_max"], 85000, lambda new_armor_area_max: update_armor_params1("armor_area_max", new_armor_area_max))  # 创建装甲板面积最大滑动条
    cv2.createTrackbar("arm_min", "params", armor_params["armor_area_min"], 1500, lambda new_armor_area_min: update_armor_params3("armor_area_min", new_armor_area_min))  # 创建装甲板面积最小滑动条
    cv2.createTrackbar("h/w", "params", int(armor_params["armor_height/width_max"] * 10), 80, lambda new_armor_heightwidth_max: update_armor_params2("armor_height/width_max", new_armor_heightwidth_max))  # 创建装甲板高度宽度最大滑动条

    # 添加灯条参数的滑动条
    cv2.createTrackbar("distance", "params", light_params["light_distance_min"], 200, lambda new_light_distance_min: light_params1("light_distance_min", new_light_distance_min))  # 创建最小灯条距离滑动条
    cv2.createTrackbar("area", "params", light_params["light_area_min"], 300, lambda new_light_area_min: light_params2("light_area_min", new_light_area_min))  # 创建最小灯条面积滑动条
    cv2.createTrackbar("height", "params", light_params["height_tol"], 500, lambda new_height_tol: light_params3("height_tol", new_height_tol))  # 创建高度容差滑动条
    cv2.createTrackbar("width", "params", light_params["width_tol"], 500, lambda new_width_tol: light_params4("width_tol", new_width_tol))  # 创建宽度容差滑动条
    cv2.createTrackbar("cy", "params", light_params["cy_tol"], 200, lambda new_cy_tol: light_params5("cy_tol", new_cy_tol))  # 创建中心点y轴容差滑动条
    cv2.createTrackbar("lit_ang", "params", light_params["light_angle_tol"], 50, lambda new_light_angle_tol: light_params6("light_angle_tol", new_light_angle_tol))  # 创建灯条角度容差滑动条
    cv2.createTrackbar("lin_ang", "params", light_params["line_angle_tol"], 50, lambda new_line_angle_tol: light_params7("line_angle_tol", new_line_angle_tol))  # 创建线角度容差滑动条

# 处理图像的函数
def process_image(image_path):
    global current_frame  # 声明全局变量
    current_frame = cv2.imread(image_path)  # 读取图像
    if current_frame is None:  # 检查图像是否读取成功
        print("错误: 无法读取图像。请检查路径:", image_path)  # 输出错误信息
        return  # 退出函数

    setup_windows()  # 设置窗口

    while True:  # 循环直到按下'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):  # 检测按键
            break  # 退出循环

    cv2.destroyAllWindows()  # 关闭所有窗口