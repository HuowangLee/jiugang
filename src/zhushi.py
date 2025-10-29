import pymysql

# ======= 数据库连接配置 =======
DB_CONFIG = {
    'host': '10.10.0.102',     # 数据库地址
    'user': 'root',          # 用户名
    'password': 'nzDn2NY5zRDMs6',    # 密码
    'database': 'niescloud_emad',  # 数据库名
    'port': 3306,            # 端口号
    'charset': 'utf8mb4'
}

# ======= 输出文件 =======
OUTPUT_FILE = 'db_structure.txt'

def main():
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 获取所有表名及其注释
    cursor.execute("""
        SELECT table_name, table_comment
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY table_name;
    """, (DB_CONFIG['database'],))
    tables = cursor.fetchall()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"数据库结构导出: {DB_CONFIG['database']}\n")
        f.write("=" * 60 + "\n\n")

        for table_name, table_comment in tables:
            f.write(f"表名: {table_name}\n")
            f.write(f"表注释: {table_comment or '(无)'}\n")
            f.write("-" * 60 + "\n")

            # 获取该表的列信息
            cursor.execute("""
                SELECT column_name, column_type, column_comment, is_nullable, column_key, extra
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
            """, (DB_CONFIG['database'], table_name))
            columns = cursor.fetchall()

            # 输出每列的信息
            f.write(f"{'字段名':<30} {'类型':<20} {'可空':<8} {'键':<8} {'额外':<10} {'注释'}\n")
            f.write("-" * 100 + "\n")
            for col in columns:
                col_name, col_type, col_comment, is_nullable, col_key, extra = col
                f.write(f"{col_name:<30} {col_type:<20} {is_nullable:<8} {col_key:<8} {extra:<10} {col_comment or ''}\n")

            f.write("\n\n")

    cursor.close()
    conn.close()
    print(f"✅ 导出完成！结果已保存到: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
