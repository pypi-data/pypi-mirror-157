import pandas as pd
from colorama import Fore

def validate_class(excel):
    print( f'{Fore.BLUE}检查班级配置文件: {excel} 是否正确{Fore.RESET}')
    
    sheet_list = ['客户', '班级', '小组', '学员名单']

    # sheets completed?
    try:
        dfs = pd.read_excel(excel, sheet_name=sheet_list)
        key_a = set(dfs['客户'].keys())
        key_b = set(['客户名称','描述'])
        if key_a.intersection(key_b) == key_b:
            print(f'{Fore.GREEN}[客户] 表单结构正确。==========={Fore.RESET}')
            print(f'{dfs["客户"]}')
        else:
            print(f'{Fore.RED}[客户] 表单结构错误！！！ {key_a}{Fore.RESET}')
        
        key_a = set(dfs['班级'].keys())
        key_b = set(['班级名称', '班级描述', '讲师登录ID（保证唯一性）', '讲师邮箱', '讲师姓名', '讲师初始密码', '模拟名称'])
        if key_a.intersection(key_b) == key_b:
            print(f'{Fore.GREEN}[班级] 表单结构正确。===={Fore.RESET}')
            print(dfs['班级'])
        else:
            print(f'{Fore.RED}[班级] 表单结构错误！！！ {key_a}{Fore.RESET}')
        
        key_a = set(dfs['小组'].keys())
        key_b = set(['小组编号', '小组名称', '教练邮箱', '教练姓名', '教练登录ID（确保唯一性）', '教练初始密码'])
        if key_a.intersection(key_b) == key_b:
            print(f'{Fore.GREEN}[小组] 表单结构正确。===={Fore.RESET}')
            print(dfs['小组'])
        else:
            print(f'{Fore.RED}[小组] 表单结构错误！！！ {key_a}{Fore.RESET}')
        
        key_a = set(dfs['学员名单'].keys())
        key_b = set(['姓名', '邮箱', '学员登录ID（确保唯一性）', '初始密码', '简介', '小组'])
        if key_a.intersection(key_b) == key_b:
            print(f'{Fore.GREEN}[学员名单] 表单结构正确。===={Fore.RESET}')
            l = len(dfs['学员名单'])
            print(f'学员人数：{l}')
        else:
            print(f'{Fore.RED}[学员名单] 表单结构错误！！！ {key_a}{Fore.RESET}')

    except ValueError as e:
        # if any sheet is missing, will be catched here
        print(f'{Fore.RED}班级配置文件 [{excel}] 有错误： {e}{Fore.RESET}')
        
    # print all line or data
