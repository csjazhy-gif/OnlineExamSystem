# -*- coding: utf-8 -*-
"""
完整模拟考试数据生成脚本
1. 清理不存在学生的孤儿数据 (studentId=20210001)
2. 清除所有正式考试的旧成绩
3. 为全部学生模拟所有正式考试，成绩正态分布
4. 生成完整的: score / subjective_answer / wrong_question / study_record
"""
import pymysql
import numpy as np
import random
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': '123456', 'database': 'online_exam', 'charset': 'utf8mb4',
}

# 正态分布参数
MEAN_RATIO = 0.72
STD_RATIO  = 0.13
MIN_RATIO  = 0.15
MAX_RATIO  = 0.98

np.random.seed(42)
random.seed(42)


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def difficulty_weight(level):
    try: lv = int(level) if level else 3
    except: lv = 3
    return {1: 1.3, 2: 1.15, 3: 1.0, 4: 0.8, 5: 0.6}.get(lv, 1.0)


# ==================== STEP 1: 清理孤儿数据 ====================
def cleanup_orphan_data(conn):
    print("=" * 60)
    print("[STEP 1] 清理不存在学生的孤儿数据")
    cur = conn.cursor()
    cur.execute("SELECT studentId FROM student")
    valid_ids = set(r[0] for r in cur.fetchall())

    tables = ['score', 'subjective_answer', 'wrong_question', 'study_record', 'face_change_request']
    total_deleted = 0
    for t in tables:
        try:
            cur.execute(f"SELECT DISTINCT studentId FROM {t}")
            t_ids = set(r[0] for r in cur.fetchall())
            orphan = t_ids - valid_ids
            if orphan:
                placeholders = ','.join(['%s'] * len(orphan))
                cur.execute(f"DELETE FROM {t} WHERE studentId IN ({placeholders})", tuple(orphan))
                cnt = cur.rowcount
                total_deleted += cnt
                print(f"  {t}: 删除 {cnt} 条孤儿记录 (studentId={orphan})")
        except Exception as e:
            pass
    conn.commit()
    print(f"  共清理 {total_deleted} 条孤儿数据")
    return valid_ids


# ==================== STEP 2: 获取数据 ====================
def fetch_students(conn):
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT studentId, studentName FROM student ORDER BY studentId")
    return cur.fetchall()


def fetch_formal_exams(conn):
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""
        SELECT examCode, description, source, paperId, examDate, totalTime,
               totalScore, type, multiScore, fillScore, judgeScore, subjectiveScore
        FROM exam_manage WHERE type = '正式考试' ORDER BY examCode
    """)
    return cur.fetchall()


def fetch_paper_questions(conn, paper_id):
    cur = conn.cursor(pymysql.cursors.DictCursor)
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


# ==================== STEP 3: 模拟答题 ====================
def gen_wrong_answer_multi(correct, q):
    """生成错误的选择题答案"""
    options = ['A', 'B', 'C', 'D']
    wrong = [o for o in options if o != correct]
    return random.choice(wrong) if wrong else 'A'


def simulate_multi(ability, questions, per_score):
    """模拟选择题, 返回 (得分, 正确列表, 错误列表)"""
    total = 0
    correct_list = []
    wrong_list = []
    for q in questions:
        qs = per_score or q.get('score') or 2
        prob = min(0.98, max(0.05, ability * difficulty_weight(q.get('level'))))
        right = q.get('rightAnswer', 'A')
        if random.random() < prob:
            total += qs
            correct_list.append(q)
        else:
            wa = gen_wrong_answer_multi(right, q)
            wrong_list.append({**q, 'wrongAnswer': wa, 'qscore': qs})
    return total, correct_list, wrong_list


def simulate_fill(ability, questions, per_score):
    total = 0
    correct_list = []
    wrong_list = []
    for q in questions:
        qs = per_score or q.get('score') or 5
        prob = min(0.95, max(0.05, ability * difficulty_weight(q.get('level')) * 0.85))
        ans = q.get('answer', '')
        if random.random() < prob:
            total += qs
            correct_list.append(q)
        else:
            wrong_list.append({**q, 'wrongAnswer': ans[:max(1,len(ans)//3)] + '...', 'qscore': qs})
    return total, correct_list, wrong_list


def simulate_judge(ability, questions, per_score):
    total = 0
    correct_list = []
    wrong_list = []
    for q in questions:
        qs = per_score or q.get('score') or 5
        prob = min(0.98, max(0.10, ability * difficulty_weight(q.get('level')) * 1.1))
        ans = q.get('answer', 'T')
        if random.random() < prob:
            total += qs
            correct_list.append(q)
        else:
            wa = 'F' if ans == 'T' else 'T'
            wrong_list.append({**q, 'wrongAnswer': wa, 'qscore': qs})
    return total, correct_list, wrong_list


def simulate_subjective(ability, questions, per_score):
    total = 0
    details = []
    for q in questions:
        max_s = per_score or q.get('score') or 10
        ratio = ability * random.uniform(0.55, 1.15)
        ratio = min(1.0, max(0.0, ratio))
        earned = round(max_s * ratio)
        earned = min(earned, max_s)
        total += earned

        ref = q.get('referenceAnswer') or ''
        if ratio > 0.85:
            sa = ref
        elif ratio > 0.6:
            sa = ref[:max(10, len(ref)//2)] + "...（部分作答）"
        else:
            sa = "我认为" + (q.get('question', '')[:20]) + "的相关内容如下。"

        comment = "优秀" if ratio>0.85 else ("良好" if ratio>0.7 else ("一般" if ratio>0.5 else "需加强"))
        details.append({
            'questionId': q['questionId'], 'studentAnswer': sa,
            'teacherScore': earned, 'maxScore': max_s,
            'comment': f"{comment}，得分{earned}/{max_s}",
            'question': q.get('question',''), 'referenceAnswer': ref,
        })
    return total, details


# ==================== STEP 4: 写入数据 ====================
def clear_exam_data(conn, exam_codes):
    """清除指定考试的所有数据"""
    if not exam_codes:
        return
    cur = conn.cursor()
    ph = ','.join(['%s'] * len(exam_codes))
    cur.execute(f"DELETE FROM subjective_answer WHERE examCode IN ({ph})", tuple(exam_codes))
    sa = cur.rowcount
    cur.execute(f"DELETE FROM score WHERE examCode IN ({ph})", tuple(exam_codes))
    sc = cur.rowcount
    # study_record中关联的考试记录也清除
    cur.execute(f"DELETE FROM study_record WHERE examCode IN ({ph})", tuple(exam_codes))
    sr = cur.rowcount
    conn.commit()
    print(f"  清除旧数据: score={sc}, subjective_answer={sa}, study_record={sr}")


def insert_score(cur, exam_code, sid, subject, pt, et, total, date):
    cur.execute("""INSERT INTO score (examCode,studentId,subject,ptScore,etScore,score,answerDate)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (exam_code, sid, subject, pt, et, total, date))


def insert_subjective_answers(cur, exam_code, sid, details):
    for d in details:
        cur.execute("""INSERT INTO subjective_answer
            (questionId, examCode, studentId, studentAnswer, teacherScore,
             teacherComment, scoredBy, scoredTime, submitTime, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),1)""",
            (d['questionId'], exam_code, sid, d['studentAnswer'],
             d['teacherScore'], d['comment'], 1))


def insert_wrong_questions(cur, sid, wrong_list, q_type, subject):
    """插入错题记录"""
    for w in wrong_list:
        qid = w['questionId']
        # 先检查是否已存在
        cur.execute("SELECT id, wrongCount FROM wrong_question WHERE studentId=%s AND questionType=%s AND questionId=%s",
                    (sid, q_type, qid))
        existing = cur.fetchone()
        if existing:
            cur.execute("UPDATE wrong_question SET wrongCount=wrongCount+1, lastWrongTime=NOW(), mastered=0, wrongAnswer=%s WHERE id=%s",
                        (w.get('wrongAnswer',''), existing[0]))
        else:
            correct_ans = w.get('rightAnswer') or w.get('answer') or ''
            cur.execute("""INSERT INTO wrong_question
                (studentId, questionType, questionId, wrongCount, lastWrongTime, mastered,
                 questionContent, correctAnswer, wrongAnswer, score, subject, analysis)
                VALUES (%s,%s,%s,1,NOW(),0,%s,%s,%s,%s,%s,%s)""",
                (sid, q_type, qid, w.get('question',''), correct_ans,
                 w.get('wrongAnswer',''), w.get('qscore') or w.get('score',0),
                 subject, w.get('analysis','')))


def insert_study_record(cur, exam_code, sid, subject, total_q, correct_cnt, wrong_cnt, score, total_score, duration, date_str):
    accuracy = round(correct_cnt / total_q * 100, 1) if total_q > 0 else 0
    cur.execute("""INSERT INTO study_record
        (studentId, practiceDate, practiceType, totalQuestions, correctCount, wrongCount,
         score, totalScore, accuracy, duration, subject, examCode)
        VALUES (%s,%s,2,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (sid, date_str, total_q, correct_cnt, wrong_cnt,
         score, total_score, accuracy, duration, subject, exam_code))


# ==================== 主流程 ====================
def main():
    conn = get_conn()
    try:
        # Step 1: 清理孤儿
        cleanup_orphan_data(conn)

        # Step 2: 获取数据
        students = fetch_students(conn)
        exams = fetch_formal_exams(conn)
        print(f"\n[INFO] {len(students)} 名学生, {len(exams)} 场正式考试")

        if not students or not exams:
            print("[ERROR] 缺少学生或考试数据!")
            return

        # 清除旧考试数据
        exam_codes = [e['examCode'] for e in exams]
        print("\n[STEP 2] 清除旧的正式考试数据")
        clear_exam_data(conn, exam_codes)

        # 清除所有旧 wrong_question (重新生成)
        cur = conn.cursor()
        cur.execute("DELETE FROM wrong_question")
        print(f"  清除旧错题: {cur.rowcount} 条")
        conn.commit()

        # Step 3: 生成能力值 (每个学生一个固定基础能力)
        abilities = np.random.normal(MEAN_RATIO, STD_RATIO, len(students))
        abilities = np.clip(abilities, MIN_RATIO, MAX_RATIO)

        total_scores = 0
        total_sa = 0
        total_wq = 0
        total_sr = 0

        for exam in exams:
            ec = exam['examCode']
            pid = exam['paperId']
            subject = exam['source'] or exam['description']
            total_max = exam['totalScore'] or 100
            date_str = exam['examDate'] or '2026-03-01'
            ms = exam.get('multiScore')
            fs = exam.get('fillScore')
            js = exam.get('judgeScore')
            ss = exam.get('subjectiveScore')

            print(f"\n{'='*60}")
            print(f"考试: {exam['description']} (examCode={ec}, paperId={pid})")

            questions = fetch_paper_questions(conn, pid)
            nm = len(questions['multi'])
            nf = len(questions['fill'])
            nj = len(questions['judge'])
            ns = len(questions['subjective'])
            print(f"  选择题:{nm} 填空题:{nf} 判断题:{nj} 主观题:{ns}")

            if nm + nf + nj + ns == 0:
                print("  [WARN] 无题目, 跳过")
                continue

            # 满分计算
            obj_max = nm * (ms or 2) + nf * (fs or 5) + nj * (js or 5)
            subj_max = ns * (ss or 10)
            print(f"  客观满分:{obj_max} 主观满分:{subj_max} 总分:{obj_max+subj_max}")

            scores_arr = []
            cur = conn.cursor()

            for i, stu in enumerate(students):
                sid = stu['studentId']
                ab = abilities[i] + np.random.normal(0, 0.05)
                ab = max(MIN_RATIO, min(MAX_RATIO, ab))

                # 模拟各题型
                pt = 0
                all_correct = 0
                all_wrong = 0
                all_wrong_list_multi = []
                all_wrong_list_fill = []
                all_wrong_list_judge = []

                if nm > 0:
                    s, cl, wl = simulate_multi(ab, questions['multi'], ms)
                    pt += s; all_correct += len(cl); all_wrong += len(wl)
                    all_wrong_list_multi = wl
                if nf > 0:
                    s, cl, wl = simulate_fill(ab, questions['fill'], fs)
                    pt += s; all_correct += len(cl); all_wrong += len(wl)
                    all_wrong_list_fill = wl
                if nj > 0:
                    s, cl, wl = simulate_judge(ab, questions['judge'], js)
                    pt += s; all_correct += len(cl); all_wrong += len(wl)
                    all_wrong_list_judge = wl

                et = 0
                subj_details = []
                if ns > 0:
                    et, subj_details = simulate_subjective(ab, questions['subjective'], ss)

                pt = min(pt, obj_max)
                et = min(et, subj_max)
                final = min(pt + et, total_max)

                # 写入 score（etScore 应为总分，前端读取 etScore 展示）
                insert_score(cur, ec, sid, subject, pt, final, final, date_str)
                total_scores += 1

                # 写入 subjective_answer
                if subj_details:
                    insert_subjective_answers(cur, ec, sid, subj_details)
                    total_sa += len(subj_details)

                # 写入 wrong_question
                sub = questions['multi'][0].get('subject', subject) if nm > 0 else subject
                if all_wrong_list_multi:
                    insert_wrong_questions(cur, sid, all_wrong_list_multi, 1, sub)
                    total_wq += len(all_wrong_list_multi)
                if all_wrong_list_fill:
                    insert_wrong_questions(cur, sid, all_wrong_list_fill, 2, sub)
                    total_wq += len(all_wrong_list_fill)
                if all_wrong_list_judge:
                    insert_wrong_questions(cur, sid, all_wrong_list_judge, 3, sub)
                    total_wq += len(all_wrong_list_judge)

                # 写入 study_record
                total_q = nm + nf + nj
                duration = random.randint(40, exam.get('totalTime') or 120)
                insert_study_record(cur, ec, sid, subject, total_q + ns,
                                    all_correct + (1 if et > subj_max*0.6 else 0),
                                    all_wrong + (0 if et > subj_max*0.6 else 1),
                                    final, total_max, duration, date_str)
                total_sr += 1

                scores_arr.append(final)

            conn.commit()

            # 统计
            arr = np.array(scores_arr)
            pass_line = total_max * 0.6
            print(f"  均分={arr.mean():.1f} 标准差={arr.std():.1f} 最高={arr.max()} 最低={arr.min()}")
            print(f"  及格率: {(arr>=pass_line).sum()}/{len(arr)} ({(arr>=pass_line).mean()*100:.1f}%)")
            seg = [
                (f"≥90", (arr >= 90).sum()),
                (f"80-89", ((arr >= 80) & (arr < 90)).sum()),
                (f"70-79", ((arr >= 70) & (arr < 80)).sum()),
                (f"60-69", ((arr >= 60) & (arr < 70)).sum()),
                (f"<60", (arr < 60).sum()),
            ]
            print(f"  分段: {' | '.join(f'{n}:{c}人' for n,c in seg)}")

        print(f"\n{'='*60}")
        print(f"[完成] 数据生成统计:")
        print(f"  成绩记录 (score): {total_scores} 条")
        print(f"  主观题答案 (subjective_answer): {total_sa} 条")
        print(f"  错题记录 (wrong_question): {total_wq} 条")
        print(f"  学习记录 (study_record): {total_sr} 条")
        print(f"  覆盖考试: {len(exams)} 场")
        print(f"  覆盖学生: {len(students)} 人")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
