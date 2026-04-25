# -*- coding: utf-8 -*-
"""
修复低分数据：将所有 score < 40 的成绩重新生成
遵循正态分布 [40, 100]，均值 70，标准差 15
同步更新 score / subjective_answer / study_record / wrong_question
"""
import pymysql
import numpy as np
import random
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': '123456', 'database': 'online_exam', 'charset': 'utf8mb4',
}

# 正态分布参数：均值70，标准差15，范围[40, 100]
MEAN_SCORE = 70
STD_SCORE = 15
MIN_SCORE = 40
MAX_SCORE = 100

np.random.seed(None)  # 随机种子，每次运行不同
random.seed()


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def difficulty_weight(level):
    try:
        lv = int(level) if level else 3
    except:
        lv = 3
    return {1: 1.3, 2: 1.15, 3: 1.0, 4: 0.8, 5: 0.6}.get(lv, 1.0)


def gen_wrong_answer_multi(correct):
    options = ['A', 'B', 'C', 'D']
    wrong = [o for o in options if o != correct]
    return random.choice(wrong) if wrong else 'A'


def fetch_paper_questions(cur, paper_id):
    result = {}
    cur.execute("""SELECT questionId, rightAnswer, score, level, question, subject, section, analysis,
                          answerA, answerB, answerC, answerD
                   FROM multi_question WHERE questionId IN
                   (SELECT questionId FROM paper_manage WHERE paperId=%s AND questionType=1)""", (paper_id,))
    result['multi'] = cur.fetchall()

    cur.execute("""SELECT questionId, answer, score, level, question, subject, section, analysis
                   FROM fill_question WHERE questionId IN
                   (SELECT questionId FROM paper_manage WHERE paperId=%s AND questionType=2)""", (paper_id,))
    result['fill'] = cur.fetchall()

    cur.execute("""SELECT questionId, answer, score, level, question, subject, section, analysis
                   FROM judge_question WHERE questionId IN
                   (SELECT questionId FROM paper_manage WHERE paperId=%s AND questionType=3)""", (paper_id,))
    result['judge'] = cur.fetchall()

    cur.execute("""SELECT questionId, referenceAnswer, score, level, question, subject, section, analysis
                   FROM subjective_question WHERE questionId IN
                   (SELECT questionId FROM paper_manage WHERE paperId=%s AND questionType=4)""", (paper_id,))
    result['subjective'] = cur.fetchall()

    return result


def simulate_with_target(ability, questions, exam, target_ratio):
    """
    根据目标得分比例模拟答题，确保总分落在目标范围内
    ability: 基础能力值 (0-1)
    target_ratio: 目标得分比例 (score / totalScore)
    """
    ms = exam.get('multiScore')
    fs = exam.get('fillScore')
    js = exam.get('judgeScore')
    ss = exam.get('subjectiveScore')

    nm = len(questions['multi'])
    nf = len(questions['fill'])
    nj = len(questions['judge'])
    ns = len(questions['subjective'])

    # 模拟选择题
    pt = 0
    wrong_multi = []
    for q in questions['multi']:
        qs = ms or q.get('score') or 2
        prob = min(0.98, max(0.15, ability * difficulty_weight(q.get('level'))))
        right = q.get('rightAnswer', 'A')
        if random.random() < prob:
            pt += qs
        else:
            wa = gen_wrong_answer_multi(right)
            wrong_multi.append({**q, 'wrongAnswer': wa, 'qscore': qs})

    # 模拟填空题
    wrong_fill = []
    for q in questions['fill']:
        qs = fs or q.get('score') or 5
        prob = min(0.95, max(0.10, ability * difficulty_weight(q.get('level')) * 0.85))
        ans = q.get('answer', '')
        if random.random() < prob:
            pt += qs
        else:
            wrong_fill.append({**q, 'wrongAnswer': ans[:max(1, len(ans)//3)] + '...', 'qscore': qs})

    # 模拟判断题
    wrong_judge = []
    for q in questions['judge']:
        qs = js or q.get('score') or 5
        prob = min(0.98, max(0.15, ability * difficulty_weight(q.get('level')) * 1.1))
        ans = q.get('answer', 'T')
        if random.random() < prob:
            pt += qs
        else:
            wa = 'F' if ans == 'T' else 'T'
            wrong_judge.append({**q, 'wrongAnswer': wa, 'qscore': qs})

    obj_max = nm * (ms or 2) + nf * (fs or 5) + nj * (js or 5)
    pt = min(pt, obj_max)

    # 模拟主观题
    et = 0
    subj_details = []
    subj_max = ns * (ss or 10)
    for q in questions['subjective']:
        max_s = ss or q.get('score') or 10
        ratio = ability * random.uniform(0.6, 1.15)
        ratio = min(1.0, max(0.0, ratio))
        earned = round(max_s * ratio)
        earned = min(earned, max_s)
        et += earned

        ref = q.get('referenceAnswer') or ''
        if ratio > 0.85:
            sa = ref
        elif ratio > 0.6:
            sa = ref[:max(10, len(ref)//2)] + "...（部分作答）"
        else:
            sa = "我认为" + (q.get('question', '')[:20]) + "的相关内容如下。"

        comment = "优秀" if ratio > 0.85 else ("良好" if ratio > 0.7 else ("一般" if ratio > 0.5 else "需加强"))
        subj_details.append({
            'questionId': q['questionId'], 'studentAnswer': sa,
            'teacherScore': earned, 'maxScore': max_s,
            'comment': f"{comment}，得分{earned}/{max_s}",
            'question': q.get('question', ''), 'referenceAnswer': ref,
        })

    et = min(et, subj_max)
    total_max = exam.get('totalScore') or 100
    final = min(pt + et, total_max)

    correct_cnt = (nm - len(wrong_multi)) + (nf - len(wrong_fill)) + (nj - len(wrong_judge))
    wrong_cnt = len(wrong_multi) + len(wrong_fill) + len(wrong_judge)

    return {
        'pt': pt, 'et': et, 'final': final,
        'correct_cnt': correct_cnt, 'wrong_cnt': wrong_cnt,
        'total_q': nm + nf + nj + ns,
        'wrong_multi': wrong_multi, 'wrong_fill': wrong_fill, 'wrong_judge': wrong_judge,
        'subj_details': subj_details,
        'obj_max': obj_max, 'subj_max': subj_max,
    }


def main():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # 1. 查找所有 score < 40 的记录
    cur.execute("SELECT * FROM score WHERE score < 40")
    low_scores = cur.fetchall()
    print(f"[INFO] 找到 {len(low_scores)} 条低于 40 分的成绩记录")

    if not low_scores:
        print("[INFO] 没有需要修复的记录，退出")
        conn.close()
        return

    # 统计每场考试的低分人数
    exam_low_count = {}
    for s in low_scores:
        ec = s['examCode']
        exam_low_count[ec] = exam_low_count.get(ec, 0) + 1
    for ec, cnt in exam_low_count.items():
        print(f"  examCode={ec}: {cnt} 条低分")

    # 2. 获取考试信息和试卷题目（缓存）
    exam_cache = {}
    question_cache = {}

    exam_codes = list(exam_low_count.keys())
    if exam_codes:
        ph = ','.join(['%s'] * len(exam_codes))
        cur.execute(f"""SELECT examCode, description, source, paperId, examDate, totalTime,
                               totalScore, type, multiScore, fillScore, judgeScore, subjectiveScore
                        FROM exam_manage WHERE examCode IN ({ph})""", tuple(exam_codes))
        for row in cur.fetchall():
            exam_cache[row['examCode']] = row
            pid = row['paperId']
            if pid not in question_cache:
                question_cache[pid] = fetch_paper_questions(cur, pid)

    # 3. 逐条修复
    fixed = 0
    failed = 0
    cur2 = conn.cursor()

    for s in low_scores:
        ec = s['examCode']
        sid = s['studentId']
        old_score = s['score']

        exam = exam_cache.get(ec)
        if not exam:
            print(f"  [WARN] examCode={ec} 找不到考试信息，跳过 studentId={sid}")
            failed += 1
            continue

        pid = exam['paperId']
        questions = question_cache.get(pid)
        if not questions:
            print(f"  [WARN] paperId={pid} 找不到题目，跳过 studentId={sid}")
            failed += 1
            continue

        total_max = exam.get('totalScore') or 100

        # 生成新的目标分数 (正态分布 [40, 100])
        new_target = np.random.normal(MEAN_SCORE, STD_SCORE)
        new_target = max(MIN_SCORE, min(MAX_SCORE, new_target))
        # 按比例换算到实际满分
        target_ratio = new_target / 100.0
        target_score_raw = round(total_max * target_ratio)
        target_score_raw = max(int(total_max * 0.4), min(total_max, target_score_raw))

        # 用较高的 ability 重新模拟
        ability = target_ratio + random.uniform(-0.05, 0.05)
        ability = max(0.4, min(0.98, ability))

        # 可能需要多次尝试确保 >= 40
        for attempt in range(10):
            result = simulate_with_target(ability, questions, exam, target_ratio)
            # 计算百分制分数
            pct_score = result['final'] / total_max * 100 if total_max > 0 else result['final']
            if pct_score >= 40:
                break
            # 提高 ability 重试
            ability = min(0.98, ability + 0.08)
        else:
            # 10次还不行，直接钳位到40分对应的实际分
            min_actual = max(int(total_max * 0.4), 40)
            if result['final'] < min_actual:
                # 强制调整主观题分
                deficit = min_actual - result['final']
                result['et'] = min(result['et'] + deficit, result['subj_max'])
                result['final'] = min(result['pt'] + result['et'], total_max)

        subject = exam.get('source') or exam.get('description') or ''

        # 4a. 更新 score 表（etScore 应为总分，与 score 一致，前端读取 etScore 展示）
        cur2.execute("UPDATE score SET ptScore=%s, etScore=%s, score=%s WHERE examCode=%s AND studentId=%s",
                     (result['pt'], result['final'], result['final'], ec, sid))

        # 4b. 更新 subjective_answer 表
        if result['subj_details']:
            cur2.execute("DELETE FROM subjective_answer WHERE examCode=%s AND studentId=%s", (ec, sid))
            for d in result['subj_details']:
                cur2.execute("""INSERT INTO subjective_answer
                    (questionId, examCode, studentId, studentAnswer, teacherScore,
                     teacherComment, scoredBy, scoredTime, submitTime, status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),1)""",
                    (d['questionId'], ec, sid, d['studentAnswer'],
                     d['teacherScore'], d['comment'], 1))

        # 4c. 更新 wrong_question（先删旧的该考试相关错题，再插入新的）
        # 删除该学生该考试相关的旧错题
        for q_type, wrong_list in [(1, result['wrong_multi']), (2, result['wrong_fill']), (3, result['wrong_judge'])]:
            for w in wrong_list:
                qid = w['questionId']
                cur2.execute("SELECT id FROM wrong_question WHERE studentId=%s AND questionType=%s AND questionId=%s",
                             (sid, q_type, qid))
                existing = cur2.fetchone()
                if existing:
                    cur2.execute("UPDATE wrong_question SET wrongCount=1, lastWrongTime=NOW(), mastered=0, wrongAnswer=%s WHERE id=%s",
                                 (w.get('wrongAnswer', ''), existing[0]))
                else:
                    correct_ans = w.get('rightAnswer') or w.get('answer') or ''
                    cur2.execute("""INSERT INTO wrong_question
                        (studentId, questionType, questionId, wrongCount, lastWrongTime, mastered,
                         questionContent, correctAnswer, wrongAnswer, score, subject, analysis)
                        VALUES (%s,%s,%s,1,NOW(),0,%s,%s,%s,%s,%s,%s)""",
                        (sid, q_type, qid, w.get('question', ''), correct_ans,
                         w.get('wrongAnswer', ''), w.get('qscore') or w.get('score', 0),
                         subject, w.get('analysis', '')))

        # 4d. 更新 study_record
        total_q = result['total_q']
        accuracy = round(result['correct_cnt'] / total_q * 100, 1) if total_q > 0 else 0
        duration = random.randint(40, exam.get('totalTime') or 120)
        date_str = exam.get('examDate') or '2026-03-01'

        cur2.execute("SELECT id FROM study_record WHERE examCode=%s AND studentId=%s", (ec, sid))
        sr = cur2.fetchone()
        if sr:
            cur2.execute("""UPDATE study_record SET totalQuestions=%s, correctCount=%s, wrongCount=%s,
                            score=%s, accuracy=%s, duration=%s WHERE examCode=%s AND studentId=%s""",
                         (total_q, result['correct_cnt'], result['wrong_cnt'],
                          result['final'], accuracy, duration, ec, sid))
        else:
            cur2.execute("""INSERT INTO study_record
                (studentId, practiceDate, practiceType, totalQuestions, correctCount, wrongCount,
                 score, totalScore, accuracy, duration, subject, examCode)
                VALUES (%s,%s,2,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (sid, date_str, total_q, result['correct_cnt'], result['wrong_cnt'],
                 result['final'], total_max, accuracy, duration, subject, ec))

        fixed += 1
        print(f"  [{fixed}/{len(low_scores)}] studentId={sid} examCode={ec}: {old_score} -> {result['final']} (目标≈{target_score_raw})")

    conn.commit()

    # 5. 验证结果
    cur.execute("SELECT COUNT(*) as cnt FROM score WHERE score < 40")
    remaining = cur.fetchone()['cnt']

    cur.execute("SELECT MIN(score) as min_s, MAX(score) as max_s, AVG(score) as avg_s, STD(score) as std_s FROM score")
    stats = cur.fetchone()

    print(f"\n{'='*60}")
    print(f"[完成] 修复统计:")
    print(f"  修复成功: {fixed} 条")
    print(f"  修复失败: {failed} 条")
    print(f"  仍低于40分: {remaining} 条")
    print(f"\n[全部成绩统计]")
    print(f"  最低分: {stats['min_s']}")
    print(f"  最高分: {stats['max_s']}")
    print(f"  平均分: {stats['avg_s']:.1f}")
    print(f"  标准差: {stats['std_s']:.1f}")

    # 分段统计
    cur.execute("""
        SELECT
            SUM(score >= 90) as s90,
            SUM(score >= 80 AND score < 90) as s80,
            SUM(score >= 70 AND score < 80) as s70,
            SUM(score >= 60 AND score < 70) as s60,
            SUM(score >= 40 AND score < 60) as s40,
            SUM(score < 40) as s_low,
            COUNT(*) as total
        FROM score
    """)
    seg = cur.fetchone()
    print(f"  ≥90: {seg['s90']}人 | 80-89: {seg['s80']}人 | 70-79: {seg['s70']}人 | 60-69: {seg['s60']}人 | 40-59: {seg['s40']}人 | <40: {seg['s_low']}人")
    print(f"  总记录数: {seg['total']}")

    conn.close()


if __name__ == '__main__':
    main()
