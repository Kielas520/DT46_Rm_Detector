import cv2  # 导入 OpenCV 库
from detector import Detector  # 从 detector 导入 Detector 类
import adjust  # 导入调试代码

# 模式参数字典
mode_params = {
    "display": 1,  # 模式参数 0: 不显示图像, 1: 显示图像
    "resize": 1, # 图像是否要经过调整 0: 不调整, 1: 调整
    "color": 2  # 颜色参数 0: 识别红色装甲板, 1: 识别蓝色装甲板, 2: 识别全部装甲板
}

# 颜色参数字典
color_params = {
    "armor_color": {1: (255, 255, 0), 0: (128, 0, 128)},  # 装甲颜色
    "armor_id": {1: 1, 0: 7},  # 装甲 ID
    "light_color": {1: (200, 71, 90), 0: (0, 100, 255)},  # 灯条颜色
    "light_dot": {1: (0, 0, 255), 0: (255, 0, 0)}  # 灯点颜色
}

mode = 0  # 模式设置 0: 视频流调试, 1: 仅运行检测, 2: 静态图调试
video = True  # 是否识别视频
url = "./photo/test.mp4"  # 视频文件路径
image_path = "./photo/red_2.jpg"  # 图像路径

# 获取第一个可用的摄像头索引
def get_first_available_camera():
    """获取第一个可用的摄像头索引"""
    for i in range(10):  # 尝试摄像头索引从0到9
        cap = cv2.VideoCapture(i)  # 尝试打开摄像头
        if cap.isOpened():  # 检查摄像头是否打开成功
            cap.release()  # 释放摄像头
            return i  # 返回可用的摄像头索引
    return None  # 没有可用摄像头

camera_index = get_first_available_camera()  # 获取可用摄像头
if camera_index is None:  # 如果没有找到可用摄像头
    print("错误: 没有找到可用的摄像头。")

if video:  # 如果要识别视频
    camera_index = url  # 使用视频文件路径

if mode == 0:  # 处理视频流
    video_stream = cv2.VideoCapture(camera_index)  # 打开视频流
    if not video_stream.isOpened():  # 检查视频流是否成功打开
        print("错误: 无法打开视频流。")
    adjust.setup_windows()  # 创建滑动条窗口
    while True:  # 持续读取视频帧
        ret, frame = video_stream.read()  # 读取视频帧
        if not ret:  # 如果未成功读取帧
            print("错误: 无法读取帧")
            break  # 退出循环
        detector = Detector(mode_params, adjust.img_params, adjust.light_params, adjust.armor_params, color_params)  # 创建 Detector 实例
        detector.detect(frame)  # 使用 detector 进行检测
        if cv2.waitKey(1) & 0xFF == ord("q"):  # 检测按键
            break  # 退出循环
    video_stream.release()  # 释放视频流
    cv2.destroyAllWindows()  # 关闭所有窗口

elif mode == 1:  # 仅运行检测
    video_stream = cv2.VideoCapture(camera_index)  # 使用可用摄像头
    if not video_stream.isOpened():  # 检查摄像头是否成功打开
        print("错误: 无法打开摄像头。")
    while True:  # 持续读取摄像头帧
        ret, frame = video_stream.read()  # 读取摄像头帧
        if not ret:  # 如果未成功读取帧
            print("错误: 无法读取帧")
            break  # 退出循环
        detector = Detector(mode_params, adjust.img_params, adjust.light_params, adjust.armor_params, color_params)  # 创建 Detector 实例
        detector.detect(frame)  # 使用 detector 进行检测
        if cv2.waitKey(1) & 0xFF == ord("q"):  # 检测按键
            break  # 退出循环
    video_stream.release()  # 释放视频流
    cv2.destroyAllWindows()  # 关闭所有窗口

elif mode == 2:  # 实时处理静态图像
    current_frame = cv2.imread(image_path)  # 读取静态图像
    if current_frame is None:  # 检查图像是否读取成功
        print("错误: 无法读取图像。请检查路径:", image_path)  # 输出错误信息
    adjust.setup_windows()  # 创建滑动条窗口
    while True:  # 持续处理图像
        detector = Detector(mode_params, adjust.img_params, adjust.light_params, adjust.armor_params, color_params)  # 创建 Detector 实例
        detector.detect(current_frame)  # 使用 detector 进行检测
        if cv2.waitKey(1) & 0xFF == ord("q"):  # 检测按键
            break  # 退出循环
    cv2.destroyAllWindows()  # 关闭所有窗口

else:  # 如果模式无效
    print("无效的模式，程序结束。")  # 输出错误信息