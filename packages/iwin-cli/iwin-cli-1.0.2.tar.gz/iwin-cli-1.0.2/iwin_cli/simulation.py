import pandas as pd
from colorama import Fore
from pathlib import Path
import json
from iwin_cli.utils import success, error, validate_picture

from iwin_cli.zip import generateConfigZip




def update_stops_json(path, df):
    jsonfile = Path(path) / 'assets' / 'info' / 'stops.json'

    total = len(df)
    seasons=[]
    idx = 0
    last_stop = 0
    g = df.groupby('季节')
    for name, group in g:
        print(f'name={name}: {len(group)}')
        last_stop += len(group)
        idx += 1
        a = {"last_stop": last_stop, "stop_icon": f"ball{idx}"}
        seasons.append(a)
    
    dictionary = {"stops": {
                    "total":total,
                    "seasons": seasons
                }
             }

    jsonString = json.dumps(dictionary, indent=4)

    print(jsonString)
    with open(jsonfile, 'w') as f:
        f.write(jsonString)
    print(f'stops.json updated: {jsonfile}')


def validate_simulation(path):
    print(f'validate_simulation in path: {path}')
    excel = Path(path) / 'config.xlsx'
    # excel = Path(path) / 'config_sheets_more.xlsx'

    sheet_list = ['模拟', '场景', '挑战（管理必做）', '团队成员', '部门角色', 'cars']

    # sheets completed?
    try:
        dfs = pd.read_excel(excel, sheet_name=sheet_list)
        
        key_a = set(dfs['模拟'].keys())
        key_b = set(['模拟名称', '描述', '版本号', '创建日期', '画面宽度', '画面高度'])
        if key_a.intersection(key_b) == key_b:
            success(f'[模拟] 表单结构正确。===========')
            print(f'{dfs["模拟"]}')
        else:
            error(f'[模拟] 表单结构错误！！！ {key_a}')
        
        key_a = set(dfs['场景'].keys())
        key_b = set(['季节', '编号', '情境标题', '情境描述', '是否必做', '优先级', '教练可以提问', '管理者可以做', '知识点'])
        if key_a.intersection(key_b) == key_b:
            success(f'[场景] 表单结构正确。===========')
            l = len(dfs["场景"])
            print(f'场景数量：{l}')
            # print(f'{dfs["场景"]}')
            update_stops_json(path, dfs["场景"])
        else:
            error(f'[场景] 表单结构错误！！！ {key_a}')
        
        key_a = set(dfs['挑战（管理必做）'].keys())
        key_b = set(['编号', '情境标题', '情境描述', '是否必做', '优先级', '教练可以提问', '管理者可以做', '知识点'])
        if key_a.intersection(key_b) == key_b:
            success(f'[挑战（管理必做）] 表单结构正确。===========')
            # print(f'{dfs["挑战（管理必做）"]}')
            l = len(dfs["挑战（管理必做）"])
            print(f'挑战（管理必做）数量：{l}')
        else:
            error(f'[挑战（管理必做）] 表单结构错误！！！ {key_a}')
        

        key_a = set(dfs['团队成员'].keys())
        key_b = set(['姓名', '描述', '是否明星员工'])
        if key_a.intersection(key_b) == key_b:
            success(f'[团队成员] 表单结构正确。===========')
            # print(f'{dfs["团队成员"]}')
            l = len(dfs["团队成员"])
            print(f'团队成员数量：{l}')
        else:
            error(f'[团队成员] 表单结构错误！！！ {key_a}')

        team_root = Path(path) / 'assets' / 'team'
        compress = input("团队成员照片需要压缩吗？[y/n?]") or 'n'
        if compress in ['y', 'Y', 'yes', 'Yes', 'YES']:
            overwrite = input("直接覆盖原来的图片吗？[y/n?]") or 'y'
            overwrite = overwrite in ['y', 'Y', 'yes', 'Yes', 'YES']
            width_limit =(input("团队成员照片的宽度：<500>")) or 500
            if type(width_limit) != int:
                width_limit = 500
            height_limit = (input("团队成员照片的高度：<400>")) or 400
            if type(height_limit) != int:
                height_limit = 400
            
            
            for idx, row in dfs['团队成员'].iterrows():
                img_path = team_root / (row['姓名']+'.png')
                validate_picture(img_path, overwrite=overwrite, width_limit=width_limit, height_limit=height_limit)

        key_a = set(dfs['部门角色'].keys())
        key_b = set(['部门', '职务', 'logo'])
        if key_a.intersection(key_b) == key_b:
            success(f'[部门角色] 表单结构正确。===========')
            # print(f'{dfs["部门角色"]}')
            l = len(dfs["部门角色"])
            print(f'部门角色数量：{l}')
        else:
            error(f'[部门角色] 表单结构错误！！！ {key_a}')
        

        key_a = set(dfs['cars'].keys())
        key_b = set(['车名', '3d图', 'icon图'])
        if key_a.intersection(key_b) == key_b:
            success(f'[cars] 表单结构正确。===========')
            # print(f'{dfs["cars"]}')
            l = len(dfs["cars"])
            print(f'跑车数量：{l}')
        else:
            error(f'[cars] 表单结构错误！！！ {key_a}')
        
        generateConfigZip(path)
    except ValueError as e:
        # if any sheet is missing, will be catched here
        error(f'班级配置文件 [{excel}] 有错误： {e}')
    except FileNotFoundError as fe:
        error(f'班级配置文件 [{excel}] 有错误： {fe}')
    # verify the team member portrait image
    # verify board image
    # verify dice sprite
    # verify stops.json
    # asking if you want to zip it? and give a name?

