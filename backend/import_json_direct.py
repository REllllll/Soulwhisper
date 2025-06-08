# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pymongo",
# ]
# ///
import os
import json
import glob
import logging
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

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
        logging.info("MongoDB连接成功")
        return db
    except Exception as e:
        logging.error(f"MongoDB连接失败: {str(e)}")
        raise

def convert_mongo_types(doc):
    """转换MongoDB特殊类型"""
    if isinstance(doc, dict):
        for key, value in doc.items():
            if key == '_id' and isinstance(value, dict) and '$oid' in value:
                doc[key] = ObjectId(value['$oid'])
            elif isinstance(value, dict) and '$date' in value:
                doc[key] = datetime.fromisoformat(value['$date'].replace('Z', '+00:00'))
            elif isinstance(value, (dict, list)):
                doc[key] = convert_mongo_types(value)
    elif isinstance(doc, list):
        return [convert_mongo_types(item) for item in doc]
    return doc

def import_json_file(json_file, collection_name, db):
    """直接导入JSON文件到MongoDB"""
    try:
        logging.info(f"开始处理文件: {json_file}")
        
        # 检查文件是否存在
        if not os.path.exists(json_file):
            logging.error(f"文件不存在: {json_file}")
            return
            
        # 读取JSON文件
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        # 转换MongoDB特殊类型
        data = convert_mongo_types(data)
        
        # 如果集合已存在，先删除
        if collection_name in db.list_collection_names():
            logging.info(f"删除已存在的集合: {collection_name}")
            db[collection_name].drop()
        
        # 插入数据
        if isinstance(data, list):
            if data:
                result = db[collection_name].insert_many(data)
                logging.info(f"成功导入 {len(result.inserted_ids)} 条记录到 {collection_name}")
            else:
                logging.warning(f"警告: {json_file} 中没有数据")
        else:
            result = db[collection_name].insert_one(data)
            logging.info(f"成功导入 1 条记录到 {collection_name}")
            
        # 验证导入
        count = db[collection_name].count_documents({})
        logging.info(f"验证: 集合 {collection_name} 中现有 {count} 条记录")
            
    except Exception as e:
        logging.error(f"导入 {json_file} 时出错: {str(e)}")
        raise

def main():
    try:
        # 连接到MongoDB
        db = connect_to_mongodb()
        
        # 获取所有JSON文件
        json_files = glob.glob('mongodb data/*.json')
        logging.info(f"找到 {len(json_files)} 个JSON文件")
        
        for json_file in json_files:
            # 从文件名中提取集合名称
            collection_name = os.path.basename(json_file).replace('.json', '')
            logging.info(f"正在处理文件: {json_file}")
            import_json_file(json_file, collection_name, db)
            
        logging.info("所有文件处理完成")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main() 