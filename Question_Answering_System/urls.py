"""
URL configuration for Question_Answering_System project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from questionAnswer import views as questionAnswerViews
from userfunctions import views as userFunctionsViews
from sendEmail import views as sendEmailViews
from wordCloud import views as wordCloudViews
from learningPath import views as learningPathViews

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('questionAnswer/', questionAnswerViews.questionAnswer, name = 'questionAnswerViews'),
    # path('askAI/', questionAnswerViews.askAI),
    path('account/', questionAnswerViews.account, name='account'),
    path('index/', questionAnswerViews.index, name='index'),
    path("login/",userFunctionsViews.login,name='login'),
    path("register/",userFunctionsViews.register,name='register'),
    path("questionAnswerViews/",userFunctionsViews.questionAnswerViews,name="questionAnswerViews"),
    path("userManagement/",userFunctionsViews.userManagement,name='userManagement'),
    path('reset-password/<int:user_id>/', userFunctionsViews.reset_password, name='reset_password'),
    path('change-permission/<int:user_id>/', userFunctionsViews.change_permission, name='change_permission'),
    path('delete-user/<int:user_id>/', userFunctionsViews.delete_user, name='delete_user'),
    path("profile/",userFunctionsViews.profile,name='profile'),
    path('update_info/', userFunctionsViews.update_info, name='update_info'),
    path('update_password/', userFunctionsViews.update_password, name='update_password'),
    path('studyReport/', questionAnswerViews.studyReport, name='studyReport'),
    path('registrationManagement/', userFunctionsViews.registrationManagement, name='registrationManagement'),
    path('registrationApprove/<int:user_id>/', userFunctionsViews.registrationApprove, name='registrationApprove'),
    path('registrationDeny/<int:user_id>/', userFunctionsViews.registrationDeny, name='registrationDeny'),
    # path('wordCloud/', wordCloudViews.wordCloud,name="wordCloud"),
    # path('wordCloudData/<int:userId>/', wordCloudViews.wordCloudData, name='wordCloudData'),
    path('wordCloud/', wordCloudViews.wordCloud, name='wordCloud'),
    path('wordCloudData/<int:userId>/', wordCloudViews.wordCloudData, name='wordCloudData'),
    path('saveQuestionRecord/', questionAnswerViews.saveQuestionRecord),
    # path('saveAnswer/', questionAnswerViews.saveAnswer),
    # path('learningPath/', learningPathViews.learningPath, name='learningPath'),
    path('learningPath/', learningPathViews.learningPathGraph, name='learningPath'),
    # path('markDownTest/', questionAnswerViews.markDownTest,name="markDownTest"),
    # path('newQuestionAnswer/', questionAnswerViews.toQuestionAnswer, name = 'newQuestionAnswerViews'),
    path('createStudyReport/', questionAnswerViews.createStudyReport, name='createStudyReport'),
    path('get-study-report-ajax/', questionAnswerViews.get_study_report_ajax, name='get_study_report_ajax'),
]
