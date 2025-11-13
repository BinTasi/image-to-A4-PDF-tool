# 批量图片转A4 PDF工具 - 功能详细说明

## 1. 核心功能概述

本工具是一个自动化的图片转PDF处理系统，主要功能是将指定文件夹中的图片文件按照2×3网格布局转换为标准A4尺寸的PDF文件，并在每张图片下方显示原文件名。

## 2. 详细功能说明

### 2.1 图片扫描与批量处理

#### 功能描述
自动扫描指定文件夹中的所有图片文件并进行批量处理。

#### 技术实现
- **扫描范围**：仅处理指定文件夹下的直接文件，不递归扫描子文件夹
- **支持格式**：所有PIL库支持的图片格式，包括但不限于JPEG、PNG、BMP、TIFF、GIF
- **文件识别**：通过检查文件扩展名（.jpg, .jpeg, .png, .bmp, .tiff, .tif, .gif）识别图片文件
- **排序规则**：按照文件名的字典顺序对图片进行排序

### 2.2 A4页面布局系统

#### 功能描述
生成标准A4尺寸的PDF页面，采用2×3网格布局。

#### 技术参数
- **页面尺寸**：A4标准尺寸，210mm × 297mm
- **边距设置**：上下左右各30mm
- **有效区域**：约150mm × 237mm（扣除边距后的可绘制区域）
- **网格布局**：2列3行共6个图片位置
- **图片尺寸**：约65mm × 75mm（每个网格单元大小）

#### 布局计算
```python
# A4尺寸（点，72dpi）
pdf_w, pdf_h = 595.2755905511812, 841.8897637795277

# 边距设置（点）
margins = {'left': 85.0, 'right': 85.0, 'top': 85.0, 'bottom': 85.0}

# 有效区域尺寸
effective_w = pdf_w - margins['left'] - margins['right']
effective_h = pdf_h - margins['top'] - margins['bottom']

# 2×3网格布局计算
columns = 2
rows = 3
img_w = effective_w / columns
grid_h = effective_h / rows
```

### 2.3 智能图片处理

#### 功能描述
对每张图片进行智能缩放和居中处理，确保在不改变比例的情况下最佳显示。

#### 技术实现
1. **尺寸获取**：读取原始图片的宽度和高度
2. **比例计算**：计算图片的宽高比
3. **缩放处理**：
   - 如果图片横长，则按宽度缩放至网格宽度
   - 如果图片竖长，则按高度缩放至网格高度
4. **居中对齐**：
   - 水平居中：计算左右边距，使图片在网格单元中水平居中
   - 垂直居中：计算上下边距，使图片在网格单元中垂直居中

#### 缩放算法
```python
img = Image.open(img_path)
orig_w, orig_h = img.size

# 计算缩放比例
scale_w = img_w / orig_w
scale_h = grid_h / orig_h
scale = min(scale_w, scale_h)

# 计算新尺寸
new_w = int(orig_w * scale)
new_h = int(orig_h * scale)

# 计算居中位置
draw_x = margins['left'] + col * img_w + (img_w - new_w) / 2
draw_y = margins['top'] + row * grid_h + (grid_h - new_h) / 2
```

### 2.4 自动分页系统

#### 功能描述
根据图片数量自动计算所需页数并创建多页PDF。

#### 技术实现
```python
# 计算总页数（每6张图片一页）
total_pages = (len(images) + 5) // 6

# 分页处理
for page_num in range(total_pages):
    # 创建新页
    c.showPage()
    
    # 处理当前页的图片
    start_idx = page_num * 6
    end_idx = min(start_idx + 6, len(images))
    page_images = images[start_idx:end_idx]
    
    # 绘制图片
    for i, img_path in enumerate(page_images):
        col = i % 2
        row = i // 2
        draw_image_with_filename(c, img_path, col, row, img_w, grid_h)
```

### 2.5 文件名显示功能

#### 功能描述
在每张图片的下方自动添加原文件名。

#### 技术实现
1. **文件名提取**：使用`os.path.basename()`获取文件名
2. **字体设置**：使用Helvetica 8号字体
3. **文本位置**：位于图片底部下方约5mm处，水平居中
4. **宽度计算**：使用`c.stringWidth()`计算文本宽度以实现居中

#### 文本绘制代码
```python
# 设置字体
c.setFont("Helvetica", 8)

# 提取文件名
filename = os.path.basename(img_path)

# 计算文本居中位置
text_x = margins['left'] + col * img_w + (img_w - c.stringWidth(filename)) / 2
text_y = draw_y + new_h + 14  # 图片下方约5mm

# 绘制文本
c.drawString(text_x, text_y, filename)
```

### 2.6 日志记录系统

#### 功能描述
详细记录整个转换过程，便于问题排查和进度跟踪。

#### 日志内容
- 程序启动和结束时间
- 输入和输出文件夹路径
- 检测到的图片数量
- 每页处理的图片数量
- PDF文件创建和保存路径
- 错误信息（如果有）

#### 日志配置
```python
# 日志文件路径
log_file = os.path.join(input_folder, f"image_to_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 日志格式配置
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
```

### 2.7 命令行参数支持

#### 功能描述
提供灵活的命令行参数配置，支持自定义输入和输出路径。

#### 支持参数
- `-i/--input`：指定输入图片文件夹路径（默认：当前目录）
- `-o/--output`：指定输出PDF文件夹路径（默认：输入目录下的pdf_output子文件夹）

#### 参数解析
```python
parser = argparse.ArgumentParser(description="批量图片转A4 PDF工具")
parser.add_argument('-i', '--input', default='.', help='输入文件夹路径')
parser.add_argument('-o', '--output', default=None, help='输出文件夹路径')
args = parser.parse_args()
```

## 3. 错误处理机制

### 3.1 图片读取错误
- **处理方式**：跳过无法读取的图片文件
- **日志记录**：记录错误信息和文件名
- **用户提示**：终端显示警告信息

### 3.2 目录权限错误
- **处理方式**：终止程序并提示错误
- **日志记录**：记录详细错误信息

### 3.3 内存不足
- **处理方式**：自动释放已处理图片的内存
- **日志记录**：记录相关信息

## 4. 性能优化

### 4.1 内存管理
- 图片逐个处理，处理完成后立即释放内存
- 不加载所有图片到内存，仅在处理时加载

### 4.2 处理速度
- 批量处理减少IO开销
- 高效的图片缩放算法

## 5. 输出文件说明

### 5.1 PDF文件命名
- 格式：`images_to_pdf_YYYYMMDD_HHMMSS.pdf`
- 包含时间戳，确保文件名唯一

### 5.2 文件结构
- 单文件包含所有图片
- 多页PDF，每页6张图片
- 保留图片原始顺序

## 6. 工作流程

1. **初始化**：
   - 解析命令行参数
   - 配置日志系统
   - 创建输出文件夹

2. **图片扫描**：
   - 扫描指定目录
   - 过滤图片文件
   - 按文件名排序

3. **PDF生成**：
   - 创建PDF文档
   - 计算总页数
   - 逐页绘制图片和文件名

4. **完成处理**：
   - 保存PDF文件
   - 记录处理结果
   - 清理资源

## 7. 技术栈

- **Python**：3.6+，核心开发语言
- **PIL/Pillow**：图片处理库
- **ReportLab**：PDF生成库
- **argparse**：命令行参数解析
- **logging**：日志系统

## 8. 系统要求

### 8.1 硬件要求
- 内存：至少512MB
- 存储：足够的空间存放输入图片和输出PDF

### 8.2 软件要求
- Windows操作系统
- Python环境（仅当使用脚本版本时需要）
- 依赖库：Pillow, ReportLab

---

以上是批量图片转A4 PDF工具的详细功能说明。该工具设计为易于使用且功能强大，同时具备良好的性能和错误处理能力，适用于各种批量图片转PDF的场景。