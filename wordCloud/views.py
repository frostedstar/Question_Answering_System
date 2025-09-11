from django.shortcuts import render,redirect
from userfunctions.views import getUserInfo
import jieba
from collections import Counter
import regex
from questionAnswer.models import QuestionRecord
from django.http import JsonResponse
from django.conf import settings



def wordCloud(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        userInfo = getUserInfo(request)
        if userInfo["userId"] is None:
            return redirect('login')
        user_id = userInfo["userId"]
    


    return render(request, 'wordCloud.html', {"userId": user_id})


def wordCloudData(request, userId):
    questionRecords = QuestionRecord.objects.filter(user_id=userId)

    allRecord = " ".join([f"{record.question_content} {record.system_answer}" for record in questionRecords])

    # 中文分词
    words = jieba.lcut(allRecord)

    # 过滤停用词
    stopWords=settings.STOPWORDS
    words = [w for w in words
             if (len(w) > 1)
             and w.strip()
             and w not in stopWords
             and not regex.match(r"^[A-Za-z]+$", w)  # 去掉纯英文
             ]

    # 词频统计
    word_counts = Counter(words)
    top_words = word_counts.most_common(100)
    data = [{"name": word, "value": count} for word, count in top_words]

    return JsonResponse(data, safe=False)

