from colorama import Fore
from pathlib import Path
import json
from PIL import Image

def error(msg):
    print(f'{Fore.RED}{msg}{Fore.RESET}')

def success(msg):
    print(f'{Fore.GREEN}{msg}{Fore.RESET}')

def validate_picture(png_filename, overwrite=False, width_limit=0, height_limit=0):
    '''
    - 图片文件是否存在?
    - 图片的尺寸是否合适
    - 图片文件的大小是否合理？
    - 图片是否有压缩的空间
    '''
    try:
        file_size =  file=Path(png_filename).stat().st_size
        # print(f'{png_filename} : {file_size}')
        img=Image.open(Path(png_filename))
        w,h=img.size    # w=Width and h=Height

        # 按比例缩放到需要的尺寸
        if width_limit > 0:
            ratio = w / width_limit
            new_width = width_limit
            new_height = round( h / ratio) 
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
        # 截取需要的高度
        if height_limit > 0:
            img = img.crop((0, 0, new_width, height_limit))
        # index "P" 模式，减小文件的体积。
        img = img.convert("P")
        if overwrite:
            img.save(png_filename)
        else:
            f_path = Path(png_filename)
            file_name = Path(f_path).stem
            file_name += '-indexed'
            new_png_filename = f_path.parent.joinpath(file_name + f_path.suffix)
            img.save(new_png_filename)
            success(f'重命名图片文件：{png_filename} ==> {new_png_filename}')
    except FileNotFoundError as fe:
        error(f'图片文件不存在：{png_filename}, {fe}')       
    except Exception as e: 
        error(f'图片处理中其它错误：{e}')

def validate_dice_sprite(dice_png, dice_dimension):
    '''图片文件，图片的尺寸，与dice的sprite的帧参数是否一致？'''
    # if the file exist?
    # if the picture size fit the frame of sprite setting?

    return True

def createItem(f, root, file_type, start_path):
    f_path = Path(root) / f
    if file_type == "image":
        # indexed color
        validate_picture(f_path, overwrite=True)
    url = f_path.relative_to(start_path)
    url = './'+str(url)
    url = url.replace("\\", "/")
    # print(f'url:{url}')

    params = f.split('_')
    if len(params) > 0 and params[0] == 'spritesheet':
        file_type = "spritesheet"
        frameConfig = {
                    "frameWidth": int(params[1]), # 280,
                    "frameHeight": int(params[2]) # 278
                }
        key = params[3].rsplit('.', 1)[0]
        ret = {"type":file_type, "key":key, "url":url, "frameConfig":frameConfig}
        
    else:
        key = f.rsplit('.', 1)[0]
        ret = {"type":file_type, "key":key, "url":url}
    
    return ret
