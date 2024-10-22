# DT46_Rm_Detector
- 面向对象版本 - 使用 OpenCV

---

## 运行代码的准备工作

### 1. 克隆代码库
使用 Git 克隆代码仓库：
```bash
git clone https://github.com/your_username/DT46_Rm_Detector.git
```

### 2. 环境设置
- **Python**: 3.x。

### 3. 安装依赖库
```bash
pip install opencv-python numpy 
```

---

## 功能模块介绍

### 1. [adjust.py](src/adjust.py) 功能介绍
- `adjust.py` 用于设置图像处理的参数，包括阈值的动态调整。

#### 使用说明
- 通过滑动条调整阈值，以查看不同处理效果的实时结果。

#### 主要变量
- `img_params`: 设定图像处理参数
  - **resolution**: 图像分辨率，默认为 (640, 480)
  - **val**: 二值化处理的阈值，默认为 35

#### 主要函数
1. **`update_img_param(param, new_val)`**
   - **参数**: 
     - `param`: 要更新的参数名称。
     - `new_val`: 新的参数值。
   - **功能**: 更新图像参数。

2. **`setup_windows()`**
   - **功能**: 创建滑动条窗口供用户调整阈值。

3. **`process_image(image_path)`**
   - **参数**:
     - `image_path`: 图像文件的路径。
   - **返回**: 无
   - **功能**: 读取图像并进行处理。

---

### 2. [cam.py](src/cam.py) 功能介绍
- `cam.py` 负责处理相机输入，支持视频流调试和静态图像处理。

#### 使用说明
- 设置不同的模式以选择处理方式：
  - **0**: 视频流调试
  - **1**: 仅运行检测
  - **2**: 仅运行检测-无图
  - **3**: 静态图调试

#### 主要变量
- `mode_params`: 模式参数设置
  - **display**: 显示模式，默认为 1。
  - **color**: 颜色模式，默认为 2。

- `light_params`: 灯条检测参数
  - **light_distance_min**: 最小灯条距离，默认为 20。
  - **light_area_min**: 最小灯条面积，默认为 5。
  - **light_angle_min**: 灯条最小角度，默认为 -30。
  - **light_angle_max**: 灯条最大角度，默认为 30。
  - **light_angle_tol**: 灯条角度容忍度，默认为 5。
  - **line_angle_tol**: 线条角度容忍度，默认为 7。
  - **height_tol**: 高度差容忍度，默认为 10。
  - **width_tol**: 宽度差容忍度，默认为 10。
  - **cy_tol**: 中心点垂直坐标差容忍度，默认为 5。

- `armor_params`: 装甲板检测参数
  - **armor_height/width_max**: 装甲板最大高宽比，默认为 3.5。
  - **armor_height/width_min**: 装甲板最小高宽比，默认为 1。
  - **armor_area_max**: 装甲板最大面积，默认为 11000。
  - **armor_area_min**: 装甲板最小面积，默认为 200。

- `image_path`: 静态图像的路径。

#### 主要函数
1. **`get_first_available_camera()`**
   - **返回**: 第一个可用摄像头的索引，若无则返回 None。
   - **功能**: 获取第一个可用的摄像头索引。

2. **`main()`**
   - **功能**: 根据设置的模式处理相机输入。
   - **返回**: 无

---

### 3. [detector.py](src/detector.py) 功能介绍
- `detector.py` 提供主要的目标检测功能，负责装甲板的识别和处理。

#### 相关阈值说明

##### 二值化阈值
- **val**: 用于二值化处理的阈值，范围 [0, 255]，默认值为 35。

#### 主要函数：
1. **`processed(img, val, mode)`**
   - **参数**:
     - `img`: 输入图像。
     - `val`: 二值化阈值。
     - `mode`: 处理模式。
   - **返回**: 处理后的图像和二值化图像。
   - **功能**: 处理图像，返回调整大小和亮度的图像及二值化图像。

2. **`find_light(img_binary, img, mode)`**
   - **参数**:
     - `img_binary`: 二值化图像。
     - `img`: 原始图像。
     - `mode`: 处理模式。
   - **返回**: 灯条的列表。
   - **功能**: 查找图像中的光源并返回灯条。

3. **`is_armor(lights, light_tol=5, angle_tol=7, height_tol=10, width_tol=10, cy_tol=5)`**
   - **参数**:
     - `lights`: 灯条列表。
     - `light_tol`: 灯条的容忍度。
     - `angle_tol`: 角度容忍度。
     - `height_tol`: 高度差容忍度。
     - `width_tol`: 宽度差容忍度。
     - `cy_tol`: 中心点垂直坐标差容忍度。
   - **返回**: 布尔值，表示是否为装甲板。
   - **功能**: 匹配灯条，判断是否为装甲板。

4. **`id_armor(img, armors, class_id, mode)`**
   - **参数**:
     - `img`: 原始图像。
     - `armors`: 装甲板列表。
     - `class_id`: 装甲板类 ID。
     - `mode`: 处理模式。
   - **返回**: 无
   - **功能**: 为装甲板标记信息并在图像上绘制轮廓，并用于生成装甲字典内容。

5. **`find_armor(img, lights_red, lights_blue, mode)`**
   - **参数**:
     - `img`: 原始图像。
     - `lights_red`: 红色灯条列表。
     - `lights_blue`: 蓝色灯条列表。
     - `mode`: 处理模式。
   - **返回**: 装甲字典。
   - **功能**: 识别装甲类型并返回装甲字典。

---

### 4. [square.py](src/square.py) 功能介绍
- `square.py` 用于创建一个640x480白色背景上的正方形图像，并在中心绘制一个面积为 14400 的正方形图像。

---

## 装甲板识别流程 *track_armor(img, val, mode)*

### 1. 图像处理
- **调用函数**: `processed(img, val, mode)`
  - **功能**: 调整图像大小、应用亮度调整、进行灰度转换并进行二值化处理。

### 2. 查找光源
- **调用函数**: `find_light(img_binary, img, mode)`
  - **功能**: 查找图像中的光源并返回灯条。

### 3. 跟踪装甲
- **调用函数**: `find_armor(img, lights_red, lights_blue, mode)`
  - **功能**: 识别装甲类型并返回装甲字典。

### 4. 返回结果
- 返回包含检测到的装甲信息的字典：
```json
{
  '443': {'class_id': 7, 'height': 101, 'center': [443, 364]}, 
  '264': {'class_id': 1, 'height': 31, 'center': [264, 241]}, 
  '366': {'class_id': 1, 'height': 35, 'center': [366, 229]}
}
```
