import cv2
from detector import Detector  # 从 detector 导入 Detector 类
import adjust  # 导入调试代码

mode_params = {"display": 1 , "color": 2}
color_params = {"armor_color":{1: (255, 255, 0), 0: (128, 0, 128)}, "armor_id":{1: 1, 0: 7}, 
                "light_color":{1: (200, 71, 90), 0: (0, 100, 255)}, "light_dot":{1: (0, 0, 255), 0: (255, 0, 0)}}

mode = 0  # 模式设置 0: 视频流调试, 1: 仅运行检测, 2: 静态图调试
video = True  # 是否识别视频
url = "./photo/test.mp4"
image_path = "./photo/red_2.jpg"  # 图像路径


def get_first_available_camera():
    """获取第一个可用的摄像头索引"""
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cap.release()
            return i
    return None  # 没有可用摄像头


camera_index = get_first_available_camera()  # 获取可用摄像头
if camera_index is None:
    print("错误: 没有找到可用的摄像头。")

if video:
    camera_index = url

if mode == 0:  # 处理视频流
    video_stream = cv2.VideoCapture(camera_index)
    if not video_stream.isOpened():
        print("错误: 无法打开视频流。")
    adjust.setup_windows()  # 创建滑动条窗口
    while True:
        ret, frame = video_stream.read()
        if not ret:
            print("错误: 无法读取帧")
            break
        detector = Detector(
            mode_params,
            adjust.img_params,
            adjust.light_params,
            adjust.armor_params,
            color_params,
        )
        detector.detect(frame)  # 使用 detector 进行检测
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    video_stream.release()
    cv2.destroyAllWindows()

elif mode == 1:  # 仅运行检测
    video_stream = cv2.VideoCapture(camera_index)  # 使用可用摄像头
    if not video_stream.isOpened():
        print("错误: 无法打开摄像头。")
    while True:
        ret, frame = video_stream.read()
        if not ret:
            print("错误: 无法读取帧")
            break
        detector = Detector(
            mode_params,
            adjust.img_params,
            adjust.light_params,
            adjust.armor_params,
            color_params,
        )
        detector.detect(frame)  # 使用 detector 进行检测
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    video_stream.release()
    cv2.destroyAllWindows()

elif mode == 2:  # 实时处理静态图像
    current_frame = cv2.imread(image_path)
    if current_frame is None:
        print("错误: 无法读取图像。请检查路径:", image_path)
    adjust.setup_windows()  # 创建滑动条窗口
    while True:
        detector = Detector(
            mode_params,
            adjust.img_params,
            adjust.light_params,
            adjust.armor_params,
            color_params,
        )
        detector.detect(current_frame)  # 使用 detector 进行检测
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()

else:
    print("无效的模式，程序结束。")
