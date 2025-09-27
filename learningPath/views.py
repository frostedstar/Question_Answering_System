# views.py
from django.shortcuts import render
from questionAnswer.models import QuestionRecord
from questionAnswer.views import getQuestionRecordByUserId, getUserInformation, getAnswer
from django.contrib.auth.decorators import login_required
import json
from .models import LearningPath
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json

# def learningPath(request):
#     userInformation = getUserInformation(request)
#     questionRecords = getQuestionRecordByUserId(userInformation['userId'])

#     # 构建知识图谱数据结构
#     knowledge_graph = {}
#     for questionRecord in questionRecords:
#         keywords = questionRecord['questionTag'].split(", ")
#         if questionRecord['questionTime'].isoformat() not in knowledge_graph:
#             knowledge_graph[questionRecord['questionTime'].isoformat()] = {
#                 'questions': [],
#                 'keywords': set()
#             }

#         knowledge_graph[questionRecord['questionTime'].isoformat()]['questions'].append({
#             'questionContent': questionRecord['questionContent'],
#             'answer': questionRecord['systemAnswer']
#         })
#         knowledge_graph[questionRecord['questionTime'].isoformat()]['keywords'].update(keywords)

#     # 结构化数据生成思维导图
#     mind_map_data = {
#         'name': f"{userInformation['userName']}的学习路径",
#         'children': []
#     }

#     for questionTime, data in knowledge_graph.items():
#         category_node = {
#             'name': questionTime,
#             'children': []
#         }

#         for question in data['questions']:
#             category_node['children'].append({
#                 'name': question['questionContent'][:7] + "...",
#                 'details': question
#             })

#         if data['keywords']:
#             keywords_node = {
#                 'name': "",
#                 'children': [{'name': kw} for kw in data['keywords']]
#             }
#             category_node['children'].append(keywords_node)

#         mind_map_data['children'].append(category_node)

#     return render(request, 'learningPath.html', {
#         'mind_map_data': json.dumps(mind_map_data)
#     })

MAX_LEARNING_PATH_QUESTIONS = 10

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
    lastLearningPath = LearningPath.objects.filter(user_id=userId).order_by('-index').first()
    print(lastLearningPath)
    if lastLearningPath:
        return lastLearningPath.graph, lastLearningPath.graph_time, lastLearningPath.question_number
    else:
        return None, None, None


def learningPathPrompt(lastGraph, questionContent):
    if lastGraph:
        return f"""你是一名负责帮助木结构建筑相关专业学生的智能学习分析助手，能将学生的以往的问答记录转换为思维导图，该思维导图以graph LR语句的形式输出。\n
        下面是根据一名学生原来的问答记录转换为思维导图后对应的graph LR语句:\n\n
        {lastGraph}\n\n
        下面是该学生的新增的问答记录：\n\n
        {questionContent}\n\n
        请将该学生新增的问答记录整合到原来的graph LR语句中。\n
        除了graph LR语句之外，不要回复任何其他信息。\n
        注意：在graph LR语句的节点名称中，如果需要标点符号，请使用中文的标点符号！！！\n
        """
    else:
        return f"""你是一名负责帮助木结构建筑相关专业学生的智能学习分析助手，能将学生的以往的问答记录转换为思维导图，该思维导图以graph LR语句的形式输出。\n
        下面是一名学生的问答记录：\n\n
        {questionContent}\n\n
        请将该学生的问答记录转换为graph LR语句。\n
        除了graph LR语句之外，不要回复任何其他信息。\n
        注意：在graph LR语句的节点名称中，如果需要标点符号，请使用中文的标点符号！！！\n
        """

@csrf_exempt
def learningPath(request):
    learningPathContent = None
    newLearningPath = None
    selectedLearningIndex = '未查询到相关内容'
    userId = request.GET.get('userId', None)
    if not(userId):
        userInformation = getUserInformation(request)
        if userInformation and ('userId' in userInformation) and userInformation['userId']:
            userId = userInformation['userId']
        else:
            print('用户不存在')
            return render(request,'login.html')
    # if request.method == 'POST':
    #     id = request.POST.get('selectedId')
    #     if id:
    #         newLearningPath = LearningPath.objects.filter(id=id).first()
    # else:
        newLearningPath = LearningPath.objects.filter(
            user_id=userId
        ).order_by('-index').first()
    if newLearningPath:
        learningPathContent = newLearningPath.graph
        selectedLearningIndex = newLearningPath.index
    learningPathIndexs = getLearningPathIndexByUserId(userId)
    print(learningPathContent)
    print(learningPathIndexs)
    return render(request, 'learningPath.html', {
        'selectedLearningIndex': selectedLearningIndex,
        'learningPathContent': learningPathContent,
        'learningPathIndexs': learningPathIndexs
    })

def getLearingPathById(request):
    userId = request.GET.get('userId', None)
    if not(userId):
        userInformation = getUserInformation(request)
        if userInformation and ('userId' in userInformation) and userInformation['userId']:
            userId = userInformation['userId']
        else:
            print('用户不存在')
            return render(request,'login.html')
    if request.method == 'POST':
        id = request.POST.get('selectedId')
        learningPathContent = None
        selectedLearningIndex = '未查询到相关内容'
        if id:
            newLearningPath = LearningPath.objects.filter(id=id).first()
            if newLearningPath:
                learningPathContent = newLearningPath.graph
                selectedLearningIndex = newLearningPath.index
        learningPathIndexs = getLearningPathIndexByUserId(userId)
        return render(request, 'learningPath.html', {
            'selectedLearningIndex': selectedLearningIndex,
            'learningPathContent': learningPathContent,
            'learningPathIndexs': learningPathIndexs
        })

def getLearningPathIndexByUserId(userId):
    learningPaths = LearningPath.objects.filter(user_id=userId).order_by('-index')
    paths = []
    if learningPaths:
        for learningPath in learningPaths:
            paths.append({
                'id': learningPath.id,
                'learningPathIndex': learningPath.index
            })
    return paths

def getLearningPathMaxIndexByUserId(userId):
    learningPath = LearningPath.objects.filter(user_id=userId).order_by('-index').first()
    if learningPath:
        return learningPath.index
    else:
        return 0

def learningPathGraph(request):
    userId = request.GET.get('userId', None)
    if not(userId):
        userInformation = getUserInformation(request)
        if userInformation and ('userId' in userInformation) and userInformation['userId']:
            userId = userInformation['userId']
        else:
            print('用户不存在')
            return render(request,'login.html')
    lastGraph, lastGraphTime,  lastGraphQuestionNumber= getLastGraph(userId)
    createlearningPathGraph(userId, lastGraph, lastGraphTime,  lastGraphQuestionNumber)
    # learningPaths = selectLearningPathByUserId(userId)
    return learningPath(request)


def selectLearningPathByUserId(userId):
    learningPaths = LearningPath.objects.filter(user_id=userId).order_by('-index')
    paths = []
    if learningPaths:
        for learningPath in learningPaths:
            paths.append({
                'id': learningPath.id,
                'userId': learningPath.user_id,
                'graph': learningPath.graph,
                'graphTime': learningPath.graph_time.strftime('%Y-%m-%d %H:%M:%S'),
                'questionNumber': learningPath.question_number
            })
    return paths


def createlearningPathGraph(userId, lastGraph, lastGraphTime,  lastGraphQuestionNumber):
    questionContents = getQuestionContentByUserIdAndTime(userId, lastGraphTime)
    number = 0
    if lastGraphQuestionNumber and lastGraphQuestionNumber<MAX_LEARNING_PATH_QUESTIONS:
        number = MAX_LEARNING_PATH_QUESTIONS-lastGraphQuestionNumber
        if number>len(questionContents):
            number = len(questionContents)
        questionContent = questionContents[0:number]
        updateLearningPath(userId, lastGraph, lastGraphQuestionNumber + number, questionContent)

    while number < len(questionContents):
        if number + MAX_LEARNING_PATH_QUESTIONS <= len(questionContents):
            questionContent = questionContents[number:number+MAX_LEARNING_PATH_QUESTIONS]
            number = number + MAX_LEARNING_PATH_QUESTIONS
            createLearningPath(userId, None, MAX_LEARNING_PATH_QUESTIONS, questionContent)
        else:
            questionContent = questionContents[number:len(questionContents)]
            createLearningPath(userId, None, len(questionContents)-number, questionContent)
            number = len(questionContents)




def createLearningPath(userId, lastGraph, lastGraphQuestionNumber, questionContent):
    if questionContent and len(questionContent)>0:
        graphTime = datetime.now()
        prompt = learningPathPrompt(lastGraph, questionContent)
        answer = getAnswer(prompt)
        answer = removeWrongCharacters(answer)
        print('answer:')
        print(answer)
        maxIndex = getLearningPathMaxIndexByUserId(userId)
        newLearningPath = LearningPath(
            user_id = userId,
            graph = answer,
            graph_time = graphTime,
            question_number = lastGraphQuestionNumber,
            index = maxIndex + 1
        )
        newLearningPath.save()

def updateLearningPath(userId, lastGraph, lastGraphQuestionNumber, questionContent):
    if questionContent and len(questionContent)>0:
        graphTime = datetime.now()
        prompt = learningPathPrompt(lastGraph, questionContent)
        answer = getAnswer(prompt)
        answer = removeWrongCharacters(answer)
        print('answer:')
        print(answer)
        LearningPath.objects.filter(user_id=userId).update(
            graph = answer,
            graph_time = graphTime,
            question_number = lastGraphQuestionNumber
        )

def recreateLearingPathByIndex(request):
    userId = request.GET.get('userId', None)
    if not(userId):
        userInformation = getUserInformation(request)
        if userInformation and ('userId' in userInformation) and userInformation['userId']:
            userId = userInformation['userId']
        else:
            print('用户不存在')
            return render(request,'login.html')
    selectedLearningIndex = request.GET.get('selectedLearningIndex', None)
    if selectedLearningIndex:
        try:
            index = int(selectedLearningIndex)
        except (ValueError, TypeError):
            return learningPath(request)
        oldLearningPath = LearningPath.objects.filter(user_id=userId, index=index).first()
        if oldLearningPath:
            questionContent = getQuestionContentByUserIdAndIndex(userId, index)
            prompt = learningPathPrompt(None, questionContent)
            answer = getAnswer(prompt)
            answer = removeWrongCharacters(answer)
            oldLearningPath.graph = answer
            oldLearningPath.save()
            # LearningPath.objects.filter(user_id=userId, index=selectedLearningIndex).delete()
            # createlearningPathGraph(userId, None, 0, None)
    return learningPath(request)

def getQuestionContentByUserIdAndIndex(userId, index):
    questionContents = QuestionRecord.objects.filter(
        user_id=userId
        ).values('question_time', 'question_content', 'question_tags', 'system_answer').order_by('id')[(index-1)*MAX_LEARNING_PATH_QUESTIONS:index*MAX_LEARNING_PATH_QUESTIONS]
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

def removeWrongCharacters(graph):
    # 移除无法处理的字符
    cleanedGraph = graph.replace('\\n', '\n').replace('|', '，').replace('&', '和')
    return cleanedGraph