import numpy as np
import cv2

# 创建图像
# 创建一个 640x480 的白色图像
height, width = 480, 640
white_image = np.ones((height, width, 3), dtype=np.uint8) * 255
x1, y1 = 200, 300

rect = (x1, y1), (50, 100), -95
box = cv2.boxPoints(rect).astype(np.int32)
cv2.drawContours(white_image, [box], 0, (255, 0, 0), thickness=1)  # 绘制旋转矩形，颜色为蓝色，线宽为2

cv2.imshow("White Image", white_image)
cv2.waitKey(0)