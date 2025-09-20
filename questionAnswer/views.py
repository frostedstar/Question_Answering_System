import json
from smtplib import SMTPException

from .models import QuestionRecord, StudyReport
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import callQwenApi
import markdown
from userfunctions.models import ReadUserInfo
import requests

userInformationTest = {
        'id': 1,
        'userId': 100000,
        'userName': 'ice10',
        'studentId': '111',
    }

def testzjz(request):
    return render(request, 'studyReport.html')

# 根据userId从数据库读取用户信息
def getUserInformationByUserId(userId:int):
    data = ReadUserInfo.objects.filter(user_id=userId).values()
    userInformation = data.first()
    print(userInformation)
    if userInformation and ('user_id' in userInformation) and userInformation['user_id']:
        information = {
            'userId': userInformation['user_id'],
            'userName': userInformation['user_name'],
            'studentId': userInformation['student_id'],
        }
        return information
    else:
        return {}

# 获取已登录的用户信息
def getUserInformation(request):
    userInformation = {
        'id': request.session.get('id'),
        'userId': request.session.get('userId'),
        'userName': request.session.get('userName'),
        'studentId': request.session.get('studentId'),
        'password': request.session.get('password'),
        'phoneNumber': request.session.get('phoneNumber'),
        'type': request.session.get('type')
    }
    return userInformation

# 跳转至主页
def index(request):
    # 获取需要的用户信息
    userInformation = getUserInformation(request)
    return render(request, 'index.html', {'userInformation': userInformation})

# 跳转至用户空间
def account(request):
    # 获取需要的用户信息
    context = {
        # 'user': request.user,
        # 其他上下文数据...
    }
    return render(request, 'account.html', context)

def questionRecordToList(questionRecords):
    newQuestionRecords = []
    for questionRecord in questionRecords:
        newQuestionRecords.append({
            'userId': questionRecord.user_id,
            'userName': questionRecord.user_name,
            'studentId': questionRecord.student_id,
            'questionContent': questionRecord.question_content,
            'systemAnswer': questionRecord.system_answer,
            # 'systemAnswer': markdown.markdown(questionRecord.system_answer),
            'questionTime': questionRecord.question_time,
            'responseDuration': questionRecord.response_duration,
            'questionTag': questionRecord.question_tags,
            'hitKnowledgeGraph': questionRecord.hit_knowledge_graph,
            'answerValidity': questionRecord.answer_validity
        })
    return newQuestionRecords

def studyReportToList(studyReports):
    newStudyReports = []
    for studyReport in studyReports:
        newStudyReports.append({
            'id':studyReport.id,
            'userId':studyReport.user_id,
            'studyReport':studyReport.study_report,
            'studyReportTime':studyReport.study_report_time
        })
    return newStudyReports

# 根据userId获取用户问答记录
def getQuestionRecordByUserId(userId):
    questionRecords = QuestionRecord.objects.filter(user_id=userId)
    newQuestionRecords = []
    if questionRecords:
        newQuestionRecords = questionRecordToList(questionRecords)
    return newQuestionRecords

def getQuestionRecordByUserIdAndTime(userId, startTime, endTime):
    questionRecords = QuestionRecord.objects.filter(
        user_id=userId,
        study_report_time__range=(startTime, endTime)
    )
    newQuestionRecords = []
    if questionRecords:
        newQuestionRecords = questionRecordToList(questionRecords)
    return newQuestionRecords


# def uploadToFastapi(content):
#     url = "http://127.0.0.1:8000/upload/"
#     data = {"content": content}
#     response = requests.post(url, json=data)
#     print("上传结果:", response.json())
#
#
# # 跳转至问答页面
# def toQuestionAnswer(request):
#     userInformation = getUserInformation(request)
#     userId = userInformation['userId']
#     questionRecords = getQuestionRecordByUserId(userId)
#     messages = []
#     messages.append({
#         'userId':userId
#     })
#     for questionRecord in questionRecords:
#         messages.append({
#             'role':'user',
#             'content':questionRecord['questionContent'],
#         })
#         messages.append({
#             'role':'assistant',
#             'content':questionRecord['systemAnswer']
#         })
#     result = uploadToFastapi(messages)
#     print(result)
#
#     url = "http://127.0.0.1:8000/fetch/"
#     response = requests.get(url)
#     print("获取结果:", response.json())
#     return redirect('http://localhost:8501/')

# def question_answer_view(request):
#     # 获取历史问答记录
#     question_answers = QuestionAnswer.objects.filter(user=request.user).order_by('-created_at')[:10]
#
#     context = {
#         'userInformation': {
#             'userName': request.user.username
#         },
#         'questionAnswers': question_answers
#     }
#     return render(request, 'questionAnswer.html', context)


@csrf_exempt
def getAnswer(questionContent):
    question = questionContent
    # 调用API获取回答
    answer = callQwenApi(question)
    # 保存问答记录到数据库（可选）
    # QuestionAnswer.objects.create(
    #     user=request.user,
    #     questionContent=question,
    #     systemAnswer=answer
    # )
    # answer = markdown.markdown(answer)
    return answer

def studyReportPrompt(strQuestion):
    return f"""你是一名木结构建筑学生的学习分析助手，能根据学生的历史提问记录，向学生推荐未涉及的知识模块进行学习，并且对学生较为关注的模块进行拓展推荐。\n
    下面是一名学生的历史提问记录：\n
    {strQuestion}\n
    除了学习分析报告中的内容之外，不要回复任何其他信息。\n
    现在为这名学生生成学习分析报告，例如可以列举一些接下来学生可以学习、关注的案例与知识模块。\n
    """

def createStudyReport(request):
    userInformation = getUserInformation(request)
    if userInformation and ('userId' in userInformation) and userInformation['userId']:
        questionRecords = getQuestionRecordByUserId(userInformation['userId'])
        questions = []
        for questionRecord in questionRecords:
            questions.append(questionRecord['questionContent'])
        strQuestion = '\n'.join(questions)
        prompt = studyReportPrompt(strQuestion)
        studyReportTime = datetime.now()
        answer = getAnswer(prompt)
        print(answer)
        newStudyReport = StudyReport(
            user_id=userInformation['userId'],
            study_report=answer,
            study_report_time=studyReportTime
        )
        newStudyReport.save()
    else:
        print('用户不存在')
        return render(request, 'login.html')
    # return render(request, 'testzjz.html', {'html_content': answer})
    # renderedHtml = markDownToHTML(answer)
    # reportTimes = getStudyReportTimeByUserId(userInformation['userId'])
    return studyReport(request)

def getStudyReportTimeByUserId(userId):
    # 获取指定用户的所有学习报告时间
    studyReports = StudyReport.objects.filter(
        user_id=userId
    ).order_by('study_report_time')
    newStudyReports = studyReportToList(studyReports)
    # studyReportTimes = []
    # for newStudyReport in newStudyReports:
    #     studyReportTimes.append(newStudyReport['studyReportTime'])
    # 将时间转换为更友好的格式
    studyReportTimes = []
    for newStudyReport in newStudyReports:
        studyReportTimes.append({
            'id':newStudyReport['id'],
            'studyReportTime':newStudyReport['studyReportTime'].strftime('%Y-%m-%d %H:%M:%S')
        })
    return studyReportTimes

@csrf_exempt
def studyReport(request):
    studyReportContent = '未查询到相关内容'
    newStudyReport = None
    selectedStudyReportTime = '未查询到相关内容'
    userId = request.GET.get('userId', None)
    if not userId:
        userInformation = getUserInformation(request)
        if userInformation and ('userId' in userInformation) and userInformation['userId']:
            userId = userInformation['userId']
        else:
            print('用户不存在')
            return render(request, 'login.html')
    # if request.method == 'POST':
    #     id = request.POST.get('selectedId')
    #     if id:
    #         newStudyReport = StudyReport.objects.filter(id=id).first()
    # else:
        newStudyReport = StudyReport.objects.filter(
            user_id=userId
        ).order_by('-study_report_time').first()
    if newStudyReport:
        studyReportContent = markDownToHTML(newStudyReport.study_report)
        selectedStudyReportTime = newStudyReport.study_report_time.strftime('%Y-%m-%d %H:%M:%S')
    studyReportTimes = getStudyReportTimeByUserId(userId)
    print(studyReportContent)
    return render(request, 'studyReport.html', {
        'selectedStudyReportTime': selectedStudyReportTime,
        'studyReportContent': studyReportContent,
        'studyReportTimes': studyReportTimes
    })

# 在 views.py 中添加以下视图函数
@csrf_exempt
def get_study_report_ajax(request):
    """异步获取学习报告内容"""
    if request.method == 'POST':
        try:
            reportId = request.POST.get('reportId')
            if reportId:
                study_report = StudyReport.objects.filter(id=reportId).first()
                if study_report:
                    studyReportContent = markDownToHTML(study_report.study_report)
                    print(studyReportContent)
                    selectedStudyReportTime = study_report.study_report_time.strftime('%Y-%m-%d %H:%M:%S')
                    return JsonResponse({
                        'status': 'success',
                        'studyReportContent': studyReportContent,
                        'selectedStudyReportTime': selectedStudyReportTime
                    })
            return JsonResponse({'status': 'error', 'message': '报告不存在'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '无效请求'})

@csrf_exempt  # 临时禁用CSRF，生产环境应使用认证
def saveQuestionRecord(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            questionRecord = data['data']
            print(questionRecord)
            print(questionRecord['userId'])
            print(questionRecord['questionContent'])
            print(questionRecord['systemAnswer'])
            print(questionRecord['responseDuration'])
            print(questionRecord['questionTags'])
            print(", ".join(questionRecord['questionTags']))
            print(questionRecord['hitKnowledgeGraph'])
            userInformation = getUserInformationByUserId(questionRecord['userId'])
            print(userInformation)
            if userInformation and ('userId' in userInformation) and userInformation['userId']:
            # userInformation = userInformationTest
            # ChatHistory.objects.create(
            #     question=data['question'],
            #     answer=data['answer'],
            #     cypher_query=data['cypher'],
            #     raw_data=json.dumps(data['raw_data'])
            # )
                newQuestionRecord = QuestionRecord(
                    user_id=userInformation['userId'],
                    user_name=userInformation['userName'],
                    student_id=userInformation['studentId'],
                    question_content=questionRecord['questionContent'],
                    system_answer=questionRecord['systemAnswer'],
                    question_time=datetime.now(),
                    response_duration=questionRecord['responseDuration'],
                    question_tags=", ".join(questionRecord['questionTags']),
                    hit_knowledge_graph=questionRecord['hitKnowledgeGraph'],
                    answer_validity=1
                )
                newQuestionRecord.save()
                print("-------------------questionRecord----------------")
                print(questionRecord)
            else:
                url = "http://127.0.0.1:8000/fetch/"
                response = requests.get(url)
                print("获取结果:", response.json())
                print('用户不存在')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



from django.shortcuts import render
import markdown
import bleach

# 允许的 HTML 标签和属性（白名单）
ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    'p', 'pre', 'code', 'blockquote', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td','hr', 'br'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'style'],
    'img': ['src', 'alt', 'title'],
    'a': ['href', 'title', 'target']
}

def markDownToHTML(markDownText):
    # renderedHtml = ""

    # if request.method == "POST":
        # mdText = request.POST.get("markdown", "")

    # 1. Markdown 转 HTML（支持代码高亮）
    html = markdown.markdown(
        markDownText,
        extensions=['fenced_code', 'codehilite', 'tables']
    )

    # 2. 过滤 HTML（防止 XSS）
    renderedHtml = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES
    )

    return renderedHtml


