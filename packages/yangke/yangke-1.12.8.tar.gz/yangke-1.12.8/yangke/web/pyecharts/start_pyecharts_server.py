import os
import sys
import traceback

from yangke.web.pyecharts.app import start_ws_serve, update_port_in_html


def start_pyecharts_server(port=5000):
    os.chdir(os.path.dirname(__file__))  # 改变当前工作路径
    try:
        update_port_in_html(port)
        start_ws_serve(port=port)
    except:
        traceback.print_exc()


if __name__ == "__main__":
    start_pyecharts_server(5000)
