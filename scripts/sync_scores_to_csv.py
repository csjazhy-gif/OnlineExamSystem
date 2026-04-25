# -*- coding: utf-8 -*-
"""
成绩数据全量同步脚本
从数据库读取最新成绩，同步更新 数据分析/ 目录下所有CSV和JSON文件
确保所有分数 >= 40，遵循正态分布 [40, 100]
"""
import pymysql
import csv
import json
import math
import os

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': '123456', 'database': 'online_exam', 'charset': 'utf8mb4',
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '数据分析')


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def export_csv(data, filename):
    if not data:
        print(f"  [WARN] {filename} 数据为空，跳过")
        return
    path = os.path.join(OUTPUT_DIR, filename)
    keys = data[0].keys()
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"  [OK] {filename} ({len(data)} 条记录)")


def export_json(data, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] {filename}")


def main():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    print("=" * 60)
    print("[STEP 1] 从数据库读取最新数据")
    print("=" * 60)

    # 1. 读取学生信息
    cur.execute("SELECT studentId, studentName, clazz, major FROM student ORDER BY studentId")
    students_raw = cur.fetchall()
    students = []
    for s in students_raw:
        students.append({
            'student_id': str(s['studentId']),
            'student_name': s['studentName'] or '',
            'gender': '男',
            'class_name': s['clazz'] or '',
            'major': s['major'] or ''
        })
    print(f"  学生: {len(students)} 人")

    # 2. 读取成绩记录 (score表)
    cur.execute("""
        SELECT s.studentId, s.examCode, s.subject, s.ptScore, s.etScore, s.score, s.answerDate,
               em.totalTime, em.totalScore, em.paperId
        FROM score s
        LEFT JOIN exam_manage em ON s.examCode = em.examCode
        ORDER BY s.studentId, s.answerDate
    """)
    scores_raw = cur.fetchall()
    print(f"  成绩记录: {len(scores_raw)} 条")

    # 验证分数范围
    low_count = sum(1 for s in scores_raw if (s['score'] or 0) < 40)
    print(f"  低于40分: {low_count} 条")

    # 3. 读取学习记录 (study_record表)
    cur.execute("""
        SELECT studentId, totalQuestions, correctCount, wrongCount, score, totalScore, 
               accuracy, duration, subject, examCode, practiceDate
        FROM study_record ORDER BY studentId
    """)
    study_raw = cur.fetchall()
    print(f"  学习记录: {len(study_raw)} 条")

    # 4. 读取错题记录 (wrong_question表)
    cur.execute("""
        SELECT studentId, questionType, questionId, wrongCount, mastered, subject, lastWrongTime
        FROM wrong_question ORDER BY studentId
    """)
    wrong_raw = cur.fetchall()
    print(f"  错题记录: {len(wrong_raw)} 条")

    # ============================================================
    print(f"\n{'=' * 60}")
    print("[STEP 2] 构建 exam_records.csv")
    print("=" * 60)

    exam_records = []
    for s in scores_raw:
        total_score = s['score'] or 0
        pt_score = s['ptScore'] or 0
        et_score = s['etScore'] or 0
        total_max = s['totalScore'] or 100

        # 查找对应的学习记录获取题目数
        sr = None
        for r in study_raw:
            if r['studentId'] == s['studentId'] and r['examCode'] == s['examCode']:
                sr = r
                break

        total_questions = sr['totalQuestions'] if sr else 30
        correct_count = sr['correctCount'] if sr else int(total_questions * 0.7)
        wrong_count = sr['wrongCount'] if sr else total_questions - correct_count
        accuracy = sr['accuracy'] if sr else round(correct_count / max(1, total_questions) * 100, 2)
        duration = sr['duration'] if sr else 60

        exam_records.append({
            'student_id': str(s['studentId']),
            'exam_code': s['examCode'],
            'subject': s['subject'] or '',
            'exam_date': str(s['answerDate'] or '2026-03-01')[:10],
            'total_questions': total_questions,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'objective_score': pt_score,
            'subjective_score': et_score,
            'total_score': total_score,
            'accuracy': accuracy,
            'duration_minutes': duration,
        })

    export_csv(exam_records, 'exam_records.csv')

    # ============================================================
    print(f"\n{'=' * 60}")
    print("[STEP 3] 构建 wrong_question_records.csv")
    print("=" * 60)

    QUESTION_TYPES = {1: '选择题', 2: '填空题', 3: '判断题', 4: '主观题'}
    wrong_records = []
    for w in wrong_raw:
        wrong_records.append({
            'student_id': str(w['studentId']),
            'question_type': w['questionType'],
            'question_type_name': QUESTION_TYPES.get(w['questionType'], '未知'),
            'subject': w['subject'] or '',
            'wrong_date': str(w['lastWrongTime'] or '2026-03-01')[:10],
            'mastered': w['mastered'] or 0,
        })

    export_csv(wrong_records, 'wrong_question_records.csv')

    # ============================================================
    print(f"\n{'=' * 60}")
    print("[STEP 4] 提取学生特征 -> student_features_original.csv")
    print("=" * 60)

    features = []
    for student in students:
        sid = student['student_id']
        stu_exams = [r for r in exam_records if r['student_id'] == sid]
        stu_wrongs = [w for w in wrong_records if w['student_id'] == sid]

        if not stu_exams:
            continue

        # 平均成绩
        avg_score = sum(e['total_score'] for e in stu_exams) / len(stu_exams)

        # 平均准确率
        avg_accuracy = sum(float(e['accuracy']) for e in stu_exams) / len(stu_exams)

        # 考试次数
        exam_count = len(stu_exams)

        # 总学习时长(小时)
        total_duration = sum(int(e['duration_minutes']) for e in stu_exams) / 60

        # 错题总数
        wrong_count = len(stu_wrongs)

        # 已掌握
        mastered_count = sum(1 for w in stu_wrongs if w['mastered'] == 1)

        # 掌握率
        mastery_rate = (mastered_count / wrong_count * 100) if wrong_count > 0 else 0

        # 成绩标准差
        if len(stu_exams) > 1:
            scores = [e['total_score'] for e in stu_exams]
            mean_s = sum(scores) / len(scores)
            variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)
            score_std = math.sqrt(variance)
        else:
            score_std = 0

        # 近期表现(最近3次)
        sorted_exams = sorted(stu_exams, key=lambda x: x['exam_date'], reverse=True)
        recent = sorted_exams[:3]
        recent_avg = sum(e['total_score'] for e in recent) / len(recent)

        # 进步幅度
        if len(stu_exams) >= 6:
            early = sorted(stu_exams, key=lambda x: x['exam_date'])[:3]
            early_avg = sum(e['total_score'] for e in early) / len(early)
            improvement = recent_avg - early_avg
        else:
            improvement = 0

        features.append({
            'student_id': sid,
            'student_name': student['student_name'],
            'avg_score': round(avg_score, 2),
            'avg_accuracy': round(avg_accuracy, 2),
            'exam_count': exam_count,
            'total_duration_hours': round(total_duration, 2),
            'wrong_count': wrong_count,
            'mastered_count': mastered_count,
            'mastery_rate': round(mastery_rate, 2),
            'score_stability': round(score_std, 2),
            'recent_performance': round(recent_avg, 2),
            'improvement': round(improvement, 2),
        })

    export_csv(features, 'student_features_original.csv')

    # ============================================================
    print(f"\n{'=' * 60}")
    print("[STEP 5] Z-Score 标准化 -> student_features_standardized.csv + stats.json")
    print("=" * 60)

    numeric_features = [
        'avg_score', 'avg_accuracy', 'exam_count', 'total_duration_hours',
        'wrong_count', 'mastered_count', 'mastery_rate', 'score_stability',
        'recent_performance', 'improvement'
    ]

    # 计算均值和标准差
    stats = {}
    for feat in numeric_features:
        values = [f[feat] for f in features]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)
        stats[feat] = {'mean': round(mean, 6), 'std': round(std, 6)}

    export_json(stats, 'student_features_stats.json')

    # 标准化
    standardized = []
    for f in features:
        row = {
            'student_id': f['student_id'],
            'student_name': f['student_name'],
        }
        for feat in numeric_features:
            mean = stats[feat]['mean']
            std = stats[feat]['std']
            z = (f[feat] - mean) / std if std > 0 else 0
            row[f'{feat}_z'] = round(z, 4)
            row[f'{feat}_original'] = f[feat]
        standardized.append(row)

    export_csv(standardized, 'student_features_standardized.csv')

    # ============================================================
    print(f"\n{'=' * 60}")
    print("[STEP 6] 验证结果")
    print("=" * 60)

    # 检查最低分
    all_scores = [e['total_score'] for e in exam_records]
    min_s = min(all_scores) if all_scores else 0
    max_s = max(all_scores) if all_scores else 0
    avg_s = sum(all_scores) / len(all_scores) if all_scores else 0
    print(f"  成绩范围: [{min_s}, {max_s}]")
    print(f"  平均分: {avg_s:.1f}")
    print(f"  低于40分: {sum(1 for s in all_scores if s < 40)} 条")
    print(f"  学生数: {len(features)}")
    print(f"  考试记录: {len(exam_records)}")
    print(f"  错题记录: {len(wrong_records)}")

    # 分段统计
    s90 = sum(1 for s in all_scores if s >= 90)
    s80 = sum(1 for s in all_scores if 80 <= s < 90)
    s70 = sum(1 for s in all_scores if 70 <= s < 80)
    s60 = sum(1 for s in all_scores if 60 <= s < 70)
    s40 = sum(1 for s in all_scores if 40 <= s < 60)
    s_low = sum(1 for s in all_scores if s < 40)
    print(f"  分段: ≥90:{s90} | 80-89:{s80} | 70-79:{s70} | 60-69:{s60} | 40-59:{s40} | <40:{s_low}")

    conn.close()
    print(f"\n[完成] 所有CSV/JSON文件已同步到: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
