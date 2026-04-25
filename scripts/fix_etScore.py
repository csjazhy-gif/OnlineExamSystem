# -*- coding: utf-8 -*-
"""
修复 etScore 字段：将所有非待批阅记录的 etScore 更新为 score（总分）

问题原因：模拟脚本将 etScore 设为仅主观题分（et），
但系统设计中 etScore 应为最终总分（-1 表示待批阅）。
前端的 scoreTable.vue、examHistory.vue、allStudentsGrade.vue
全部读取 etScore 作为考试总分展示。

修复：UPDATE score SET etScore = score WHERE etScore != -1
"""
import pymysql

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': '123456', 'database': 'online_exam', 'charset': 'utf8mb4',
}


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # 1. 查看修复前状态
    cur.execute("SELECT COUNT(*) as cnt FROM score WHERE etScore != -1 AND etScore != score")
    mismatch = cur.fetchone()['cnt']
    print(f"[修复前] etScore != score 的记录数（非待批阅）: {mismatch}")

    cur.execute("""
        SELECT examCode, studentId, ptScore, etScore, score,
               (score - etScore) as diff
        FROM score
        WHERE etScore != -1 AND etScore != score
        ORDER BY ABS(score - etScore) DESC
        LIMIT 10
    """)
    samples = cur.fetchall()
    if samples:
        print("\n[示例] etScore 与 score 差异最大的记录:")
        print(f"  {'examCode':<12} {'studentId':<12} {'ptScore':>8} {'etScore':>8} {'score':>8} {'diff':>8}")
        for r in samples:
            print(f"  {r['examCode']:<12} {r['studentId']:<12} {r['ptScore']:>8} {r['etScore']:>8} {r['score']:>8} {r['diff']:>8}")

    # 2. 执行修复
    cur.execute("UPDATE score SET etScore = score WHERE etScore != -1 AND etScore != score")
    updated = cur.rowcount
    conn.commit()
    print(f"\n[修复] 更新了 {updated} 条记录: etScore = score")

    # 3. 验证修复结果
    cur.execute("SELECT COUNT(*) as cnt FROM score WHERE etScore != -1 AND etScore != score")
    remaining = cur.fetchone()['cnt']
    print(f"[验证] 修复后 etScore != score 的记录数: {remaining}")

    # 4. 查看修复后统计
    cur.execute("""
        SELECT
            MIN(etScore) as min_et, MAX(etScore) as max_et,
            AVG(etScore) as avg_et, STD(etScore) as std_et,
            MIN(score) as min_s, MAX(score) as max_s,
            AVG(score) as avg_s
        FROM score
        WHERE etScore != -1
    """)
    stats = cur.fetchone()
    print(f"\n[统计] 非待批阅记录:")
    print(f"  etScore: 最低={stats['min_et']}, 最高={stats['max_et']}, 平均={stats['avg_et']:.1f}, 标准差={stats['std_et']:.1f}")
    print(f"  score  : 最低={stats['min_s']}, 最高={stats['max_s']}, 平均={stats['avg_s']:.1f}")

    # 5. 分段统计（按 etScore）
    cur.execute("""
        SELECT
            SUM(etScore >= 90) as s90,
            SUM(etScore >= 80 AND etScore < 90) as s80,
            SUM(etScore >= 70 AND etScore < 80) as s70,
            SUM(etScore >= 60 AND etScore < 70) as s60,
            SUM(etScore >= 40 AND etScore < 60) as s40,
            SUM(etScore < 40 AND etScore != -1) as s_low,
            SUM(etScore = -1) as pending,
            COUNT(*) as total
        FROM score
    """)
    seg = cur.fetchone()
    print(f"\n[etScore 分段统计]")
    print(f"  ≥90: {seg['s90']} | 80-89: {seg['s80']} | 70-79: {seg['s70']} | 60-69: {seg['s60']} | 40-59: {seg['s40']} | <40: {seg['s_low']} | 待批阅: {seg['pending']}")
    print(f"  总记录: {seg['total']}")

    conn.close()
    print("\n[完成] etScore 已同步为总分，成绩查询和学情中心将显示正确分数")


if __name__ == '__main__':
    main()
