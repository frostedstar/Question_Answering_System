# views.py
from django.shortcuts import render
from questionAnswer.models import QuestionRecord
from questionAnswer.views import getQuestionRecordByUserId, getUserInformation, getAnswer
from django.contrib.auth.decorators import login_required
import json
#
#
# def learningPath(request):
#     userInformation = getUserInformation(request)
#     questionRecords = getQuestionRecordByUserId(userInformation['userId'])
#
#     # 提取关键词和构建知识关联
#     knowledge_graph = {}
#     for questionRecord in questionRecords:
#
#         keywords = questionRecord['questionTag'].split(", ")
#         if questionRecord['questionTime'].isoformat() not in knowledge_graph:
#             knowledge_graph[questionRecord['questionTime'].isoformat()] = {
#                 'questions': [],
#                 'keywords': set()
#             }
#
#         knowledge_graph[questionRecord['questionTime'].isoformat()]['questions'].append({
#             'questionContent': questionRecord['questionContent'],
#             'answer': questionRecord['systemAnswer']
#         })
#         knowledge_graph[questionRecord['questionTime'].isoformat()]['keywords'].update(keywords)
#
#     # 转换为前端可用的格式
#     mind_map_data = {
#         'name': f"{userInformation['userName']}'s Learning Path",
#         'children': []
#     }
#
#     for questionTime, data in knowledge_graph.items():
#         category_node = {
#             'time': questionTime,
#             'children': []
#         }
#
#         # 添加问题节点
#         for question in data['questions']:
#             category_node['children'].append({
#                 'name': question['questionContent'][:5] + "...",
#                 'details': question
#             })
#
#         # 添加关键词节点
#         if data['keywords']:
#             keywords_node = {
#                 'name': "Keywords",
#                 'children': [{'name': kw} for kw in data['keywords']]
#             }
#             category_node['children'].append(keywords_node)
#
#         mind_map_data['children'].append(category_node)
#
#     return render(request, 'learningPath.html', {
#         'mind_map_data': json.dumps(mind_map_data)
#     })

# views.py

from django.shortcuts import render
import json

def learningPath(request):
    userInformation = getUserInformation(request)
    questionRecords = getQuestionRecordByUserId(userInformation['userId'])

    # 构建知识图谱数据结构
    knowledge_graph = {}
    for questionRecord in questionRecords:
        keywords = questionRecord['questionTag'].split(", ")
        if questionRecord['questionTime'].isoformat() not in knowledge_graph:
            knowledge_graph[questionRecord['questionTime'].isoformat()] = {
                'questions': [],
                'keywords': set()
            }

        knowledge_graph[questionRecord['questionTime'].isoformat()]['questions'].append({
            'questionContent': questionRecord['questionContent'],
            'answer': questionRecord['systemAnswer']
        })
        knowledge_graph[questionRecord['questionTime'].isoformat()]['keywords'].update(keywords)

    # 结构化数据生成思维导图
    mind_map_data = {
        'name': f"{userInformation['userName']}的学习路径",
        'children': []
    }

    for questionTime, data in knowledge_graph.items():
        category_node = {
            'name': questionTime,
            'children': []
        }

        for question in data['questions']:
            category_node['children'].append({
                'name': question['questionContent'][:7] + "...",
                'details': question
            })

        if data['keywords']:
            keywords_node = {
                'name': "",
                'children': [{'name': kw} for kw in data['keywords']]
            }
            category_node['children'].append(keywords_node)

        mind_map_data['children'].append(category_node)

    return render(request, 'learningPath.html', {
        'mind_map_data': json.dumps(mind_map_data)
    })



def getQuestionContentByUserId(userId):
    # userId = 100028
    questionContents = QuestionRecord.objects.filter(user_id=userId).values('question_time', 'question_content', 'question_tags', 'system_answer').order_by('id')
    # print(questionContents)
    questions = []
    if questionContents:
        for questionContent in questionContents:
            questions.append({
                'questionTime': questionContent['question_time'].strftime('%Y-%m-%d %H:%M:%S'),
                'questionContent':questionContent['question_content'],
                'questionTags':questionContent['question_tags'],
                'systemAnswer':questionContent['system_answer']
            })
    print(questions)
    return questions


def learningPathPrompt(QuestionContent):
    return f"""你是一名负责帮助木结构建筑相关专业学生的智能学习分析助手，能将学生的以往的问答记录转换为思维导图，该思维导图以graph LR语句的形式输出。\n
    下面是一名学生的问答记录：\n\n
    {QuestionContent}\n\n
    请将该学生的问答记录转换为graph LR语句。\n
    除了graph LR语句之外，不要回复任何其他信息。\n

    """


def learningPathGraph(request):
    # userInformation = getUserInformation(request)
    # userId =  request.GET.get('user_id', None)
    # if userId:
    #     QuestionContent = getQuestionContentByUserId(userId)
    #     prompt = learningPathPrompt(QuestionContent)
    #     answer = getAnswer(prompt)
    #     print(answer)
    # elif userInformation and ('userId' in userInformation) and userInformation['userId']:
    #     userId = userInformation['userId']
    #     QuestionContent = getQuestionContentByUserId(userId)
    #     prompt = learningPathPrompt(QuestionContent)
    #     answer = getAnswer(prompt)
    #     print(answer)
    # else:
    #     print('用户不存在')
    # return render(request, 'learningPath.html', {'html_content': answer})
    userId = request.GET.get('userId', None)
    if not(userId):
        userInformation = getUserInformation(request)
        if userInformation and ('userId' in userInformation) and userInformation['userId']:
            userId = userInformation['userId']
        else:
            print('用户不存在')
            return render(request,'login.html')
    QuestionContent = getQuestionContentByUserId(userId)
    prompt = learningPathPrompt(QuestionContent)
    answer = getAnswer(prompt)
    print(answer)
    return render(request, 'learningPath.html', {'htmlContent': answer})