# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
#     "pymongo",
# ]
# ///
import os
import pandas as pd
from pymongo import MongoClient
import glob

def connect_to_mongodb():
    """连接到MongoDB数据库"""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soulwhisper']
    return db

def import_csv_to_mongodb(csv_file, collection_name, db):
    """将单个CSV文件导入到MongoDB集合中"""
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        
        # 将DataFrame转换为字典列表
        records = df.to_dict('records')
        
        # 如果集合已存在，先删除
        if collection_name in db.list_collection_names():
            db[collection_name].drop()
        
        # 插入数据
        if records:
            db[collection_name].insert_many(records)
            print(f"成功导入 {len(records)} 条记录到 {collection_name}")
        else:
            print(f"警告: {csv_file} 中没有数据")
            
    except Exception as e:
        print(f"导入 {csv_file} 时出错: {str(e)}")

def main():
    # 连接到MongoDB
    db = connect_to_mongodb()
    
    # 获取所有CSV文件
    csv_files = glob.glob('mongodb data/*.csv')
    
    for csv_file in csv_files:
        # 从文件名中提取集合名称
        collection_name = os.path.basename(csv_file).replace('.csv', '')
        print(f"正在处理文件: {csv_file}")
        import_csv_to_mongodb(csv_file, collection_name, db)

if __name__ == "__main__":
    main() 
