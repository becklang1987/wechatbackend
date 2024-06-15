import pandas as pd

# 创建数据
data = {
    'Location': ['Chengdu_Treat', 'Chengdu_Treat', 'Chengdu_Treat', 'Chengdu_Treat', 
                 'Chengdu_Commercial', 'Chengdu_Commercial', 'Chengdu_Commercial', 'Chengdu_Commercial'],
    'Device': ['cnchen02ar01', 'cnchen02ar02', 'cnchen02ir01', 'cnchen02ir02', 
               'cnchen01ar01', 'cnchen01ar02', 'cnchen01ir01', 'cnchen01ir02'],
    'model': ['CISCO-ISR-4451', 'CISCO-ISR-4451', 'CISCO-ISR-4451', 'CISCO-ISR-4451', 
              'CISCO-ISR-4451', 'CISCO-ISR-4451', 'CISCO-ISR-4451', 'CISCO-ISR-4451'],
    'SN': ['FDO2130000001', 'FDO2130000002', 'FDO2130000003', 'FDO2130000004', 
           'FDO2130000001', 'FDO2130000002', 'FDO2130000003', 'FDO2130000004']
}

# 创建DataFrame
df = pd.DataFrame(data)

# 写入CSV文件
df.to_csv('host_info.csv', index=False)

print("数据已成功写入CSV文件")