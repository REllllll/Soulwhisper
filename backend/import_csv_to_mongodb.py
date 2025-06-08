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
from bson import ObjectId
from datetime import datetime
import glob
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_mongodb():
    """连接到MongoDB数据库"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        # 测试连接
        client.admin.command('ping')
        db = client['soulwhisper']
        logging.info("成功连接到MongoDB")
        return db
    except Exception as e:
        logging.error(f"连接MongoDB失败: {str(e)}")
        raise

def convert_value(value, field_name):
    """转换字段值为MongoDB兼容的类型"""
    if pd.isna(value):
        return None
    
    # 处理_id字段
    if field_name == '_id':
        try:
            return ObjectId(str(value))
        except:
            return value
    
    # 处理日期字段
    if isinstance(value, str) and ('_at' in field_name or 'date' in field_name.lower()):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    return value

def import_csv_to_mongodb(csv_file, collection_name, db):
    """将单个CSV文件导入到MongoDB集合中"""
    try:
        logging.info(f"开始处理文件: {csv_file}")
        
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        logging.info(f"CSV文件读取成功，共 {len(df)} 行数据")
        
        # 转换数据类型
        records = []
        for _, row in df.iterrows():
            record = {}
            for column in df.columns:
                record[column] = convert_value(row[column], column)
            records.append(record)
        
        logging.info(f"数据转换完成，准备导入 {len(records)} 条记录")
        
        # 如果集合已存在，先删除
        if collection_name in db.list_collection_names():
            logging.info(f"删除已存在的集合: {collection_name}")
            db[collection_name].drop()
        
        # 插入数据
        if records:
            result = db[collection_name].insert_many(records)
            logging.info(f"成功导入 {len(result.inserted_ids)} 条记录到 {collection_name}")
            
            # 验证导入
            count = db[collection_name].count_documents({})
            logging.info(f"验证: 集合 {collection_name} 中现有 {count} 条记录")
        else:
            logging.warning(f"警告: {csv_file} 中没有数据")
            
    except Exception as e:
        logging.error(f"导入 {csv_file} 时出错: {str(e)}")
        raise

def main():
    try:
        # 连接到MongoDB
        db = connect_to_mongodb()
        
        # 获取所有CSV文件
        csv_files = glob.glob('mongodb data/*.csv')
        logging.info(f"找到 {len(csv_files)} 个CSV文件")
        
        for csv_file in csv_files:
            # 从文件名中提取集合名称
            collection_name = os.path.basename(csv_file).replace('.csv', '')
            logging.info(f"正在处理文件: {csv_file}")
            import_csv_to_mongodb(csv_file, collection_name, db)
            
        logging.info("所有文件处理完成")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
