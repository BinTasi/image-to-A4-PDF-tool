#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量图片转A4 PDF工具

功能：将文件夹中的图片按每6张一组，排列成2x3的网格，生成A4大小的PDF文件
使用方法：
  1. 默认处理当前目录：python batch_images_to_a4_pdf_with_logging.py
  2. 指定输入文件夹：python batch_images_to_a4_pdf_with_logging.py --input 你的图片文件夹路径
  3. 同时指定输入和输出文件夹：python batch_images_to_a4_pdf_with_logging.py --input 你的图片文件夹路径 --output 你的输出文件夹路径

命令行参数：
  -i, --input   指定要处理的图片文件夹路径（默认为当前目录）
  -o, --output  指定PDF输出文件夹路径（默认为在输入文件夹下创建pdf_output子文件夹）

依赖：
  - PIL (Pillow)
  - reportlab

安装依赖：pip install Pillow reportlab
"""
import os
import glob
import logging
import argparse
from datetime import datetime
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# 配置日志
def setup_logging(log_dir="logs"):
    """配置日志记录系统"""
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志文件名包含时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"image_to_pdf_{timestamp}.log")
    
    # 配置日志格式和级别
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    
    logging.info("日志系统初始化完成")
    return log_file

def create_a4_pdf(image_paths, output_pdf):
    """
    将图片排列成2列3行的网格，生成A4大小的PDF。
    当图片数量超过6张时，会自动创建多页PDF，每页放置6张图片。
    每张图片下方会显示其文件名。
    
    参数:
        image_paths: 包含图片路径的列表
        output_pdf: 输出PDF的路径
    """
    try:
        # A4尺寸（点）
        a4_width, a4_height = A4
        
        # 创建PDF画布
        c = canvas.Canvas(output_pdf, pagesize=A4)
        
        # 计算每张图片的位置和大小（2列3行网格）
        margin = 40
        inner_margin = 20
        
        # 有效区域尺寸
        effective_width = a4_width - 2 * margin
        effective_height = a4_height - 2 * margin
        
        # 每张图片的尺寸（2列3行）
        img_width = (effective_width - inner_margin) / 2     # 2列
        img_height = (effective_height - 2 * inner_margin) / 3  # 3行
        
        # 计算总页数
        total_images = len(image_paths)
        images_per_page = 6
        total_pages = (total_images + images_per_page - 1) // images_per_page  # 向上取整
        
        logging.info(f"将创建 {total_pages} 页PDF，每页最多6张图片")
        
        # 处理每一页
        for page_num in range(total_pages):
            # 计算当前页的图片范围
            start_idx = page_num * images_per_page
            end_idx = min((page_num + 1) * images_per_page, total_images)
            page_images = image_paths[start_idx:end_idx]
            
            logging.debug(f"处理第 {page_num + 1} 页，共 {len(page_images)} 张图片")
            
            # 处理并放置当前页的每张图片
            for i, img_path in enumerate(page_images):
                try:
                    # 检查文件是否存在
                    if not os.path.exists(img_path):
                        logging.warning(f"图片文件不存在: {img_path}，将跳过该图片")
                        continue
                    
                    # 检查文件是否可打开
                    with Image.open(img_path) as img:
                        # 验证图片是否有效
                        img.verify()
                
                    # 重新打开图片进行处理（verify后需要重新打开）
                    with Image.open(img_path) as img:
                        # 计算缩放比例以适应目标尺寸，保持宽高比
                        img_ratio = img.width / img.height
                        target_ratio = img_width / img_height
                        
                        if img_ratio > target_ratio:
                            # 图片更宽，按宽度缩放
                            scale = img_width / img.width
                        else:
                            # 图片更高，按高度缩放
                            scale = img_height / img.height
                        
                        # 计算缩放后的尺寸
                        new_width = img.width * scale
                        new_height = img.height * scale
                        
                        # 计算位置 - 2列3行网格
                        col = i % 2   # 0 或 1
                        row = i // 2  # 0, 1 或 2
                        
                        x = margin + col * (img_width + inner_margin)
                        # 计算Y坐标时考虑PDF的坐标原点在左下角
                        y = a4_height - margin - (row + 1) * img_height - row * inner_margin
                        
                        # 将图片绘制到PDF上
                        c.drawImage(
                            img_path, 
                            x + (img_width - new_width) / 2,  # 水平居中
                            y + (img_height - new_height) / 2, # 垂直居中
                            width=new_width, 
                            height=new_height, 
                            preserveAspectRatio=True
                        )
                        
                        # 获取图片文件名（不含路径）
                        img_filename = os.path.basename(img_path)
                        # 设置字体大小
                        c.setFont("Helvetica", 8)
                        # 计算文本宽度和居中位置
                        text_width = c.stringWidth(img_filename, "Helvetica", 8)
                        text_x = x + (img_width - text_width) / 2
                        text_y = y - 15  # 图片下方15点位置
                        # 绘制文本
                        c.drawString(text_x, text_y, img_filename)
                        logging.debug(f"已将图片 {os.path.basename(img_path)} 添加到PDF")
            
                except Exception as e:
                    logging.error(f"处理图片 {img_path} 时出错: {str(e)}", exc_info=True)
                    continue
            
            # 如果不是最后一页，则添加新页面
            if page_num < total_pages - 1:
                c.showPage()
        
        # 保存PDF
        c.save()
        logging.info(f"PDF已生成: {output_pdf}")
        return True
        
    except Exception as e:
        logging.error(f"生成PDF {output_pdf} 时出错: {str(e)}", exc_info=True)
        return False

def batch_process_folder(input_folder, output_folder=None, image_extensions=('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp')):
    """
    批量处理文件夹中的所有图片，生成一个多页PDF文件，每页放置6张图片
    
    参数:
        input_folder: 包含图片的输入文件夹路径
        output_folder: 输出PDF的文件夹路径
        image_extensions: 要处理的图片扩展名元组
    """
    try:
        # 验证输入文件夹是否存在
        if not os.path.isdir(input_folder):
            raise NotADirectoryError(f"输入文件夹不存在或不是一个有效的目录: {input_folder}")
        
        # 设置输出文件夹
        if output_folder is None:
            output_folder = os.path.join(input_folder, 'pdf_output')
        
        # 创建输出文件夹（如果不存在）
        os.makedirs(output_folder, exist_ok=True)
        logging.info(f"PDF文件将保存到: {output_folder}")
        
        # 获取所有图片文件路径
        image_files = []
        for ext in image_extensions:
            found_files = glob.glob(os.path.join(input_folder, ext))
            image_files.extend(found_files)
            logging.debug(f"找到 {len(found_files)} 个 {ext} 格式的文件")
        
        # 按文件名排序
        image_files.sort()
        
        # 统计图片数量
        total_images = len(image_files)
        logging.info(f"在文件夹 {input_folder} 中找到 {total_images} 张图片")
        
        if total_images == 0:
            logging.warning("没有找到任何图片文件")
            return False
        
        # 生成PDF文件名（使用时间戳确保唯一性）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"images_{timestamp}.pdf"
        pdf_path = os.path.join(output_folder, pdf_filename)
        
        # 处理所有图片，生成一个多页PDF
        logging.info(f"正在处理所有 {total_images} 张图片，将生成一个多页PDF")
        create_a4_pdf(image_files, pdf_path)
        
        logging.info("批量处理完成")
        return True
        
    except Exception as e:
        logging.error(f"批量处理文件夹时出错: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    try:
        # 创建命令行参数解析器
        parser = argparse.ArgumentParser(description='批量将图片转换为A4大小的PDF文件')
        parser.add_argument('--input', '-i', default='.', 
                            help='输入图片文件夹路径（默认为当前目录）')
        parser.add_argument('--output', '-o', default=None, 
                            help='输出PDF文件夹路径（默认为在输入文件夹下创建pdf_output子文件夹）')
        
        # 解析命令行参数
        args = parser.parse_args()
        
        # 初始化日志
        log_file = setup_logging()
        print(f"日志将记录到: {log_file}")
        
        # 执行批量处理
        batch_process_folder(args.input, args.output)
        
        print(f"\n已成功处理文件夹: {os.path.abspath(args.input)}")
        if args.output:
            print(f"多页PDF文件已保存到: {os.path.abspath(args.output)}")
        else:
            print(f"多页PDF文件已保存到: {os.path.abspath(os.path.join(args.input, 'pdf_output'))}")
        print(f"程序会自动将所有图片整合到一个PDF文件中，每页放置6张图片（2列3行布局）")
        
    except Exception as e:
        logging.critical(f"程序运行出错: {str(e)}", exc_info=True)
        print(f"程序出错: {str(e)}")
        print("详细错误信息请查看日志文件")
    
    try:
        # 尝试检测是否在交互模式下运行，如果是则保留停留功能
        # 仅在命令行模式下等待用户输入
        if os.isatty(0):
            input("\n处理完成，按回车键退出...")
    except (IOError, OSError, AttributeError):
        # 在非交互模式（如打包成可执行文件时）跳过input语句
        pass
    