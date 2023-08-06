from util.logger import logger
import numpy as np
import pandas as pd
import constants
import openpyxl

'''
        time_cost_dict['app_start_time'] = start_time_index * time_interval
        time_cost_dict['app_tab_apper_time'] = start_complete_index * time_interval
        time_cost_dict['app_feed_apper_time'] = vedio_start_load_index * time_interval
        time_cost_dict['app_video_start_time'] = vedio_load_complete_index * time_interval
        time_cost_dict['start_time_cost'] = str(start_time_cost)
        time_cost_dict['total_cost_time'] = str(total_cost_time)

'''
def get_result_data_to_excel(result,result_path):
    data_series=[]
    not_recognize_data_series=[]
    cost_result = []
    result_count = 1
    not_recognize_count = 1
    excelwriter = pd.ExcelWriter(result_path, engine='openpyxl')
    for r in result:
        # start_tab_cost', 'tab_feed_cost', 'feed_video_cost', 'total_cost', 'vedio_path'
        result_data = []
        # start_tab_cost', 'tab_feed_cost', 'feed_video_cost', 'total_cost', 'vedio_path', 'is_ad
        not_recognize_data = []
        is_ad = r.get('is_ad', False)
        not_recognize = r.get('not_recognize_video', False)
        if is_ad or not_recognize:
            logger.info(u'未识别视屏:%s', r['not_recognize_video'])
            start_tab_cost = r[constants.RESULT_APP_TAB_APPEAR_TIME] - r[constants.RESULT_APP_START_TIME]
            tab_feed_cost = r[constants.RESULT_APP_FEED_APPEAR_TIME] - r[constants.RESULT_APP_TAB_APPEAR_TIME]
            tab_video_cost = r[constants.RESULT_APP_VEDIO_START_TIME] - r[constants.RESULT_APP_TAB_APPEAR_TIME]
            total_cost = r[constants.RESULT_TOTAL_TIME_COST] - r[constants.RESULT_APP_START_TIME]
            not_recognize_data.append(start_tab_cost * 1000 if start_tab_cost * 1000 > 0 else 'NA')
            not_recognize_data.append(tab_feed_cost * 1000 if tab_feed_cost * 1000 > 0 else 'NA')
            not_recognize_data.append(tab_video_cost * 1000 if tab_video_cost * 1000 > 0 else 'NA')
            not_recognize_data.append(total_cost * 1000 if total_cost * 1000 > 0 else 'NA')
            not_recognize_data.append(r[constants.RESULT_VEDIO_PATH])
            not_recognize_data.append(is_ad)
        else:
            start_tab_cost = r[constants.RESULT_APP_TAB_APPEAR_TIME] - r[constants.RESULT_APP_START_TIME]
            tab_feed_cost = r[constants.RESULT_APP_FEED_APPEAR_TIME] - r[constants.RESULT_APP_TAB_APPEAR_TIME]
            feed_video_cost = r[constants.RESULT_APP_VEDIO_START_TIME] - r[constants.RESULT_APP_TAB_APPEAR_TIME]
            total_cost = r[constants.RESULT_TOTAL_TIME_COST] - r[constants.RESULT_APP_START_TIME]
            result_data.append(start_tab_cost * 1000)
            result_data.append(tab_feed_cost * 1000)
            result_data.append(feed_video_cost * 1000)
            result_data.append(total_cost * 1000)
            result_data.append(r[constants.RESULT_VEDIO_PATH])

        if result_data:
            data = pd.Series(result_data, index=['start_tab_cost', 'tab_feed_cost', 'tab_video_cost', 'total_cost', 'vedio_path'], name=result_count)
            data_series.append(data)
            result_count+=1
            df=pd.DataFrame(data_series)
            df.to_excel(excelwriter, sheet_name='result')

        if not_recognize_data:
            data = pd.Series(not_recognize_data, index=['start_tab_cost', 'tab_feed_cost', 'tab_video_cost', 'total_cost', 'vedio_path', 'is_ad'], name=not_recognize_count)
            not_recognize_data_series.append(data)
            not_recognize_count+=1
            df=pd.DataFrame(not_recognize_data_series)
            df.to_excel(excelwriter, sheet_name='not_recognize_result')
    excelwriter.save()
    print(df)

def get_mean_result(path):
    mean_costs = []
    result_excel = pd.ExcelFile(path)
    result_sheets = result_excel.sheet_names
    if 'result' not in result_sheets:
        return
    costs = pd.read_excel(path, usecols=['start_tab_cost', 'tab_feed_cost', 'tab_video_cost', 'total_cost'], sheet_name='result')
    start_tab_cost = np.array(costs['start_tab_cost'])
    if len(start_tab_cost) <=2:
        return
    min_index = np.argwhere(start_tab_cost==start_tab_cost.min())[0]
    start_tab_cost = np.delete(start_tab_cost, min_index)
    max_index = np.argwhere(start_tab_cost == start_tab_cost.max())[0]
    start_tab_cost = np.delete(start_tab_cost, max_index)
    start_tab_cost = start_tab_cost
    mean_start_tab_cost = start_tab_cost.mean()
    mean_costs.append(mean_start_tab_cost)

    tab_feed_cost = np.array(costs['tab_feed_cost'])
    min_index = np.argwhere(tab_feed_cost==tab_feed_cost.min())[0]
    tab_feed_cost = np.delete(tab_feed_cost, min_index)
    max_index = np.argwhere(tab_feed_cost == tab_feed_cost.max())[0]
    tab_feed_cost = np.delete(tab_feed_cost, max_index)
    tab_feed_cost = tab_feed_cost
    mean_tab_feed_cost = tab_feed_cost.mean()
    mean_costs.append(mean_tab_feed_cost)

    feed_video_cost = np.array(costs['tab_video_cost'])
    min_index = np.argwhere(feed_video_cost==feed_video_cost.min())[0]
    feed_video_cost = np.delete(feed_video_cost, min_index)
    max_index = np.argwhere(feed_video_cost == feed_video_cost.max())[0]
    feed_video_cost = np.delete(feed_video_cost, max_index)
    feed_video_cost = feed_video_cost
    mean_feed_video_cost = feed_video_cost.mean()
    mean_costs.append(mean_feed_video_cost)

    total_cost = np.array(costs['total_cost'])
    min_index = np.argwhere(total_cost==total_cost.min())[0]
    total_cost = np.delete(total_cost, min_index)
    max_index = np.argwhere(total_cost == total_cost.max())[0]
    total_cost = np.delete(total_cost, max_index)
    total_cost = total_cost
    mean_total_cost = total_cost.mean()
    mean_costs.append(mean_total_cost)
    book = openpyxl.load_workbook(path)  # 读取你要写入的workbook
    excelwriter = pd.ExcelWriter(path=path, engine='openpyxl')
    ##此时的writer里还只是读写器. 然后将上面读取的book复制给writer
    excelwriter.book = book
    ## ExcelWriter for some reason uses writer.sheets to access the sheet.
    ## If you leave it empty it will not know that sheet Main is already there
    ## and will create a new sheet.
    excelwriter.sheets = dict((ws.title, ws) for ws in book.worksheets)
    data = pd.Series(mean_costs,
                     index=['start_tab_cost', 'tab_feed_cost', 'tab_video_cost', 'total_cost'],
                     name='mean')

    costs = costs.append(data)
    df = pd.DataFrame(costs)
    df.to_excel(excelwriter, sheet_name='result')
    excelwriter.save()

