import cv2

# 设置默认值
img_params = {"resolution": (640, 480), 
              "val": 35}
def update_img_param(param, new_val):
    img_params[param] = new_val  # 更新图像参数

def setup_windows():
    cv2.namedWindow('Threshold')
    cv2.createTrackbar('Threshold', 'Threshold', img_params["val"], 255, lambda new_val: update_img_param("val", new_val))  # 创建 val 滑动条

def process_image(image_path):
    global current_frame
    current_frame = cv2.imread(image_path)
    if current_frame is None:
        print("错误: 无法读取图像。请检查路径:", image_path)
        return

    setup_windows()  # 设置窗口

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()