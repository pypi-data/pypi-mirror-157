'''
读取数据:
import dwj_tools.read_hdf_wind as r  # wind数据
import dwj_tools.read_hdf_qfx_300 as r  # 权分析300数据
import dwj_tools.read_hdf_qfx_50 as r  # 权分析50数据
option,etf = r.read_data()

更新数据:
from dwj_tools.get_data_from_wind import update_option_data_wind as u  # wind更新
from dwj_tools.get_data_from_qfx import update_data_qfx as u  # wind更新
u.update()
'''