import cv2

light_params = {"light_distance_min": 20, "light_area_min": 5, 
                "light_angle_min": -35, "light_angle_max": 35, 
                "light_angle_tol": 5, "line_angle_tol": 7, 
                "height_tol": 10, "width_tol": 10, "cy_tol": 5}
armor_params = {"armor_height/width_max": 3.5,"armor_height/width_min": 1,
                "armor_area_max": 11000,"armor_area_min": 200}
img_params = {"resolution": (640,480) , 
                "val": 35}


def update_img_param(param, new_val):
    img_params[param] = new_val  # 更新图像参数


def update_armor_params1(param, new_armor_area_max):
    armor_params[param] = new_armor_area_max  # 更新图像参数


def update_armor_params2(param, new_armor_heightwidth_max):
    new_armor_heightwidth_max = new_armor_heightwidth_max / 10
    armor_params[param] = new_armor_heightwidth_max  # 更新图像参数


def light_params1(param, new_light_distance_min):
    light_params[param] = new_light_distance_min  # 更新图像参数


def light_params2(param, new_light_area_min):
    light_params[param] = new_light_area_min  # 更新图像参数


def light_params3(param, new_height_tol):
    light_params[param] = new_height_tol


def light_params4(param, new_width_tol):
    light_params[param] = new_width_tol


def light_params5(param, new_cy_tol):
    light_params[param] = new_cy_tol


def light_params6(param, new_light_angle_tol):
    light_params[param] = new_light_angle_tol


def light_params7(param, new_line_angle_tol):
    light_params[param] = new_line_angle_tol


def setup_windows():
    # 创建窗口
    cv2.namedWindow(
        "params",
    )
    cv2.resizeWindow("params", 640, 405)
    # 创建滑动条
    cv2.createTrackbar(
        "Thresh",
        "params",
        img_params["val"],
        255,
        lambda new_val: update_img_param("val", new_val),
    )  # 创建 Threshold 滑动条

    cv2.createTrackbar(
        "armor_area",
        "params",
        armor_params["armor_area_max"],
        85000,
        lambda new_armor_area_max: update_armor_params1(
            "armor_area_max", new_armor_area_max
        ),
    )  # 创建 armor_area_max 滑动条
    cv2.createTrackbar(
        "h/w",
        "params",
        int(armor_params["armor_height/width_max"] * 10),
        80,
        lambda new_armor_heightwidth_max: update_armor_params2(
            "armor_height/width_max", new_armor_heightwidth_max
        ),
    )  # 创建 armor_height/width_max 滑动条

    # 添加光照参数的滑动条
    cv2.createTrackbar(
        "distance",
        "params",
        light_params["light_distance_min"],
        200,
        lambda new_light_distance_min: light_params1(
            "light_distance_min", new_light_distance_min
        ),
    )  # 创建 light_distance_min 滑动条
    cv2.createTrackbar(
        "area",
        "params",
        light_params["light_area_min"],
        300,
        lambda new_light_area_min: light_params2("light_area_min", new_light_area_min),
    )  # 创建 light_area_min 滑动条
    cv2.createTrackbar(
        "height",
        "params",
        light_params["height_tol"],
        500,
        lambda new_height_tol: light_params3("height_tol", new_height_tol),
    )  # 创建 height_tol 滑动条
    cv2.createTrackbar(
        "width",
        "params",
        light_params["width_tol"],
        500,
        lambda new_width_tol: light_params4("width_tol", new_width_tol),
    )  # 创建 width_tol 滑动条
    cv2.createTrackbar(
        "cy",
        "params",
        light_params["cy_tol"],
        200,
        lambda new_cy_tol: light_params5("cy_tol", new_cy_tol),
    )  # 创建 cy_tol 滑动条
    cv2.createTrackbar(
        "lit_ang",
        "params",
        light_params["light_angle_tol"],
        50,
        lambda new_light_angle_tol: light_params6(
            "light_angle_tol", new_light_angle_tol
        ),
    )  # 创建 light_angle_tol 滑动条
    cv2.createTrackbar(
        "lin_ang",
        "params",
        light_params["line_angle_tol"],
        50,
        lambda new_line_angle_tol: light_params7("line_angle_tol", new_line_angle_tol),
    )  # 创建 line_angle_tol 滑动条


def process_image(image_path):
    global current_frame
    current_frame = cv2.imread(image_path)
    if current_frame is None:
        print("错误: 无法读取图像。请检查路径:", image_path)
        return

    setup_windows()  # 设置窗口

    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
