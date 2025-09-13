# views.py
from django.shortcuts import render
from questionAnswer.models import QuestionRecord
from questionAnswer.views import getQuestionRecordByUserId, getUserInformation, getAnswer
from django.contrib.auth.decorators import login_required
import json
from .models import LearningPath
from datetime import datetime

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
    questionContents = QuestionRecord.objects.filter(user_id=userId).values('question_time', 'question_content', 'question_tags', 'system_answer').order_by('id')
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

def getQuestionContentByUserIdAndTime(userId, graphTime):
    if graphTime:
        questionContents = QuestionRecord.objects.filter(
            user_id=userId,
            question_time__gt=graphTime
            ).values('question_time', 'question_content', 'question_tags', 'system_answer').order_by('id')
    else:
        questionContents = QuestionRecord.objects.filter(
            user_id=userId
            ).values('question_time', 'question_content', 'question_tags', 'system_answer').order_by('id')
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

def getLastGraph(userId):
    lastLearningPath = LearningPath.objects.filter(user_id=userId).order_by('-graph_time').first()
    print(lastLearningPath)
    if lastLearningPath:
        return lastLearningPath.graph, lastLearningPath.graph_time
    else:
        return None, None


def learningPathPrompt(lastGraph, QuestionContent):
    if lastGraph:
        return f"""你是一名负责帮助木结构建筑相关专业学生的智能学习分析助手，能将学生的以往的问答记录转换为思维导图，该思维导图以graph LR语句的形式输出。\n
        下面是根据一名学生原来的问答记录转换为思维导图后对应的graph LR语句:\n\n
        {lastGraph}\n\n
        下面是该学生的新增的问答记录：\n\n
        {QuestionContent}\n\n
        请将该学生新增的问答记录整合到原来的graph LR语句中。\n
        除了graph LR语句之外，不要回复任何其他信息。\n
        """
    else:
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
    lastGraph, lastGraphTime = getLastGraph(userId)
    graphTime = datetime.now()
    QuestionContent = getQuestionContentByUserIdAndTime(userId, lastGraphTime)
    if QuestionContent:
        prompt = learningPathPrompt(lastGraph, QuestionContent)
        answer = getAnswer(prompt)
        print('answer:')
        print(answer)
        newLearningPath = LearningPath(
            user_id = userId,
            graph = answer,
            graph_time = graphTime
        )
        newLearningPath.save()
        return render(request, 'learningPath.html', {'htmlContent': answer})
    else:
        if lastGraph:
            return render(request, 'learningPath.html', {'htmlContent': lastGraph})
        else:
            return render(request, 'learningPath.html')


