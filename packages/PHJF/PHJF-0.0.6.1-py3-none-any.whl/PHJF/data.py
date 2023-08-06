import requests
import json
import os
import atexit
from flask import Flask, render_template, jsonify

PHJF_text = ("\033[34m%s" % "PHJF:")
page_text = ""
all_file_name = ""

unicode = "utf-8"

web_name = ""
lists_info = []


def get_page(url, encoding, ish):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/52.0.2743.116 Safari/537.36'}
    print(PHJF_text + "\033[33m%s" % "开始抓取网页数据")
    page_back = requests.get(url, headers=headers)
    if page_back.status_code == requests.codes.ok:
        print(PHJF_text + "\033[32m%s" % "抓取成功")
    else:
        print(PHJF_text + "\033[31m%s" % "抓取失败")

    if ish == "save":
        write_page = page_back.text
        file_name = input(PHJF_text + "\033[35m%s" % "输入文件名称（包括后缀）")
        if encoding == "":
            encoding = unicode
        else:
            encoding = encoding
        with open(file_name, 'w', encoding=encoding) as save:
            save.write(write_page)
            print(PHJF_text + f"\033[32m%s \033[33m{file_name}" % "文件已保存")
    elif ish == "let":
        global page_text
        page_text = page_back.text
        print(PHJF_text + "\033[35m%s" % "对接数据已加载")
    else:
        print(PHJF_text + "\033[35m%s" % "页面数据已返回")
        return page_back.text


def run_compile_page(ish, file_name):
    if page_text != "":
        print(PHJF_text + "\033[36m%s" % "已对接数据")
        compile_page(ish, file_name)
    else:
        print(PHJF_text + "\033[31m%s" % "未查找到数据")


# 抓取特别页面数据
def compile_page(ish, file_name):
    global all_file_name
    all_file_name = file_name
    with open("var.txt", "a", encoding=unicode) as save:
        save.write(file_name)
    with open("page_text.txt", "a", encoding=unicode) as save:
        save.write(page_text)
    print(PHJF_text + "\033[33m%s" % "正在编译数据...")
    if ish == "json":
        with open(f"{file_name}.json", 'a', encoding=unicode) as save:
            json_file = json.dumps(lists_info, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))
            save.write(json_file + "\n")
        print(PHJF_text + "\033[32m%s" % "数据已保存")
    elif ish == "data":
        with open(f"templates/{file_name}.txt", 'a', encoding=unicode) as save:
            json_file = lists_info
            save.write(str(json_file))
        print(PHJF_text + "\033[32m%s" % "数据已对接")
    else:
        print(PHJF_text + "\033[31m%s" % "请输入正确的指令")
        exit()


def run_server():
    print(PHJF_text + "\033[33m%s" % "正在启动本地服务器...")
    content = """
from flask import Flask, render_template, jsonify


super_var = open("var.txt", "r")
File_name = super_var.read()
name = f"{File_name}.txt"

print("\033[34m%s" % "PHJF:" + "\033[32m%s" % "服务器已启动")
print("\033[34m%s" % "PHJF:" + "\033[35m%s" % "请打开启动网址中的" + "\033[36m%s" % f" /read_json/{File_name} " + "\033[35m%s" % "目录" + "\033[30m")

app = Flask(__name__)  # 实例化flask


# json_name是客户端传来的json文件名，根据传来的文件名从本地读取
@app.route('/read_json/<json_name>', methods=['GET'])
# 如果你改了名字，改变这里的名字，它是目录的名字
def game_json(json_name=File_name):
    try:
        # 如果你改了名字，改变这里的名字，它是更改的名字
        return jsonify(render_template(name))
    except Exception as e:
        return jsonify({"code": "Error", "message": "{}".format(e)})


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"  # 指定浏览器渲染的文件类型，和解码格式；
    app.run()
    """
    make_web = open('open_web.py', 'w', encoding='utf8')
    # 写入文件内容
    make_web.write(content)
    # 关闭文件
    make_web.close()

    os.system("python3 open_web.py")



@atexit.register
def clean_file():
    clear_var = open('var.txt', "r+")
    clear_var.truncate()
    clear_page_text = open('page_text.txt', "r+")
    clear_page_text.truncate()
    os.remove(f'templates/{all_file_name}.txt')
    print(PHJF_text + "\033[33m%s" % "超级全局变量和页面内容已清除")


'''
 ______     _     _      _____    _______ 
(_____ \   | |   | |    (_____)  (_______)
 _____) )  | |__ | |       _      _____   
|  ____/   |  __)| |      | |    |  ___)  
| |        | |   | |   ___| |    | |      
|_|        |_|   |_|  (____/     |_|      

2022 by CCAil                                          
'''
