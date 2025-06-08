# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pymongo",
# ]
# ///
import os
import subprocess
import glob
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def import_csv_to_mongodb(csv_file, collection_name):
    """使用mongoimport命令导入CSV文件到MongoDB"""
    try:
        logging.info(f"开始处理文件: {csv_file}")
        
        # 构建mongoimport命令
        cmd = [
            'mongoimport',
            '--db', 'soulwhisper',
            '--collection', collection_name,
            '--type', 'csv',
            '--headerline',
            '--file', csv_file
        ]
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info(f"成功导入文件 {csv_file} 到集合 {collection_name}")
            logging.info(f"命令输出: {result.stdout}")
        else:
            logging.error(f"导入失败: {result.stderr}")
            
    except Exception as e:
        logging.error(f"导入 {csv_file} 时出错: {str(e)}")
        raise

def main():
    try:
        # 获取所有CSV文件
        csv_files = glob.glob('mongodb data/*.csv')
        logging.info(f"找到 {len(csv_files)} 个CSV文件")
        
        for csv_file in csv_files:
            # 从文件名中提取集合名称
            collection_name = os.path.basename(csv_file).replace('.csv', '')
            logging.info(f"正在处理文件: {csv_file}")
            import_csv_to_mongodb(csv_file, collection_name)
            
        logging.info("所有文件处理完成")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
