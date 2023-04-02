from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Testimonial, PollAnswer, PollQuestion, ProfileAnswers, ProfileQuestion, Profile, Announcement, Leaderboard, Team_Member
from django.db.models.functions import Length, Lower
from PIL import Image, ImageOps
import os
import re
from yearbook.settings import BASE_DIR, MEDIA_ROOT, POLL_STOP, PORTAL_STOP, PRODUCTION
import collections
from datetime import timedelta
from functools import wraps
from django.contrib import messages

# Create your views here.

profile_pic_upload_folder = os.path.join(MEDIA_ROOT, Profile.profile_pic.field.upload_to)

def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    # print("Emojis Removed :)")
    return emoji_pattern.sub(r'', string)

def votes_sort_key(item):
    return len(item[1])

def nominees_sort_key(item):
    return item.full_name

def is_edited(func ):
    @wraps(func)
    def wrapper(request,  *args, **kwargs):
        user = User.objects.filter(username=request.user.username).first()
        profile = Profile.objects.filter(user=user).first()
        if user.is_superuser:
                return func(request,  *args, **kwargs)
        if profile.gmailid == "" or profile.address == "" or len(profile.phoneno) != 10 :
            messages.warning(request, "Please update all the required profile fields (i.e., phone number, address and gmail id) to continue!" )
            errors = [0, 0]
            context = {
                'updated': False,
                'user': user,
                'profile': profile,
                'errors': errors,
                'logged_in': True
            }
            return render(request, 'editprofile.html', context)
            # return render(request, 'editprofile.html')
        else :
            return func(request,  *args, **kwargs)
    
    return wrapper
        


@login_required
@is_edited
def home(request):
    # print("hii")
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            logged_in = True
        else:
            logged_in = False
        if logged_in:
            user = User.objects.filter(username=request.user.username).first()
            poll_questions = PollQuestion.objects.all().order_by("question")
            polls = {}
            if user.is_superuser:
                for question in poll_questions:
                    answers = PollAnswer.objects.filter(question=question)
                    answers_count = answers.count()
                    poll_dict = {}
                    for answer in answers:
                        if answer.answer in poll_dict.keys():
                            poll_dict[answer.answer].append(answer.voted_by)
                        else:
                            poll_dict[answer.answer] = [answer.voted_by]
                    polls[(question, answers_count)] = sorted(poll_dict.items(), key=votes_sort_key, reverse=True)
                context = {
                    'user': user,
                    'logged_in': logged_in
                }
                return render(request, 'admin_home.html', context)
            else:
                user_profile = Profile.objects.filter(user=user).first()
                if not user_profile.graduating:
                    context = {
                        'user': user,
                        'user_profile': user_profile,
                        'logged_in': logged_in
                    }
                    return render(request, 'polls.html', context)
                else:
                    testimonials = Testimonial.objects.filter(given_to=user_profile).order_by('-id')
                    #                    for question in poll_questions:
                    #                        answers = PollAnswer.objects.filter(question=question)
                    #                        myanswer = answers.filter(voted_by=user_profile).first()
                    #                        if myanswer:
                    #                            myanswer = myanswer.answer
                    #                        else:
                    #                            myanswer = None
                    #                        poll_nominees = []
                    #                        for answer in answers:
                    #                            if answer.answer not in poll_nominees:
                    #                                poll_nominees.append(answer.answer)
                    #                        polls[(question, myanswer)] = sorted(poll_nominees, key=nominees_sort_key)
                    context = {
                        'testimonials': testimonials,
                        'user': user,
                        'user_profile': user_profile,
                        'logged_in': logged_in
                    }
                    return render(request, 'home.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    else:
        return error404(request)


@login_required
@is_edited
def profile(request, username):
    
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            user = User.objects.filter(username=request.user.username).first()
            user_profile = Profile.objects.filter(user=user).first()
            profile_user = User.objects.filter(username=username).first()
            if profile_user:
                if profile_user.is_superuser:
                    return error404(request)
                if profile_user == user:
                    myprofile = True
                else:
                    myprofile = False
                profile = Profile.objects.filter(user=profile_user).first()
                if not profile.graduating:
                    context = {
                        'logged_in': True,
                        'user': user,
                        'myprofile': myprofile,
                        'profile': profile
                    }
                    return render(request, 'profile.html', context)
                else:
                    testimonials = Testimonial.objects.filter(given_to=profile).order_by('-favourite',
                                                                                         Length('content').desc(),
                                                                                         '-id')
                    profile_questions = ProfileQuestion.objects.all()
                    profile_answers = ProfileAnswers.objects.filter(profile=profile)
                    mytestimonial = testimonials.filter(given_by=user_profile).first()
                    answers = {}
                    for question in profile_questions:
                        answers[question] = profile_answers.filter(question=question).first()
                    profiles = []
                    for i in testimonials:
                        profiles.append(i.given_by)
                        print(i.given_by)
                    print("Heko")
                    testimonials = zip(testimonials,profiles)
                    context = {
                        'logged_in': True,
                        'myprofile': myprofile,
                        'user': user,
                        'testimonials': testimonials,
                        'mytestimonial': mytestimonial,
                        'profile': profile,
                        'answers': answers
                    }
                    return render(request, 'profile.html', context)
            else:
                return error404(request)
        else:
            profile_user = User.objects.filter(username=username).first()
            if profile_user:
                if profile_user.is_superuser:
                    return error404(request)
                profile = Profile.objects.filter(user=profile_user).first()
                if not profile.graduating:
                    context = {
                        'logged_in': False,
                        'profile': profile
                    }
                    return render(request, 'profile.html', context)
                else:
                    testimonials = Testimonial.objects.filter(given_to=profile).order_by('-id')
                    profile_questions = ProfileQuestion.objects.all()
                    profile_answers = ProfileAnswers.objects.filter(profile=profile)
                    answers = {}
                    for question in profile_questions:
                        answers[question] = profile_answers.filter(question=question).first()
                    context = {
                        'logged_in': False,
                        'testimonials': testimonials,
                        'profile': profile,
                        'answers': answers
                    }
                    return render(request, 'profile.html', context)
            else:
                return error404(request)
    else:
        return error404(request)


@login_required
@is_edited
def search(request):
    print("hiisasaa")
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            user = User.objects.filter(username=request.user.username).first()
            key = request.GET.get("key", "")
            json = request.GET.get("json", "")
            if key and key != "":
                profiles = Profile.objects.filter(user__first_name__contains=key.upper(), graduating=True)
            else:
                if json != "1":
                    return HttpResponseRedirect(reverse('home'))
                else:
                    return JsonResponse([], safe=False)
            profile_values = []
            page_profiles = profiles.exclude(user=user)
            more_profiles = False
            if page_profiles.count() > 20:
                more_profiles = True
            if json == "1":
                for profile in profiles[:10]:
                    profile_values.append({'username': profile.user.username, 'name': profile.full_name})
                return JsonResponse(profile_values, safe=False)
            else:
                context = {
                    'logged_in': True,
                    'user': user,
                    'profiles': page_profiles[:20],
                    'more_profiles': more_profiles
                }
                return render(request, 'search.html', context)
        else:
            key = request.GET.get("key", "")
            if key and key != "":
                profiles = Profile.objects.filter(user__first_name__contains=key.upper(), graduating=True)
            else:
                return HttpResponseRedirect(reverse('home'))
            more_profiles = False
            if profiles.count() > 20:
                more_profiles = True
            context = {
                'logged_in': False,
                'profiles': profiles[:20],
                'more_profiles': more_profiles
            }
            return render(request, 'search.html', context)
    else:
        return error404(request)


def login(request):
    if request.method == 'GET':
        # profile = Profile.objects.filter(user=user).first()
        # if profile.gmailid == "":
        #     user = User.objects.filter(username=request.user.username).first()
        #     context = {
        #         'logged_in': True,
        #         'user': user,
        #         'production': PRODUCTION
        #     }
        #     return render(request, 'editprofile.html', context)

        if request.user and not request.user.is_anonymous :
            user = User.objects.filter(username=request.user.username).first()
            context = {
                'logged_in': True,
                'user': user,
                'production': PRODUCTION
            }
            return render(request, 'login.html', context)
        else:
            next = request.GET.get('next', "/yearbook")
            context = {
                'logged_in': False,
                'next': next,
                'production': PRODUCTION
            }
            return render(request, 'login.html', context)
    else:
        return error404(request)


@login_required

def edit_profile(request):
    if request.method == 'GET':
        user = User.objects.filter(username=request.user.username).first()
        profile = Profile.objects.filter(user=user).first()
        errors = [0, 0]
        if user.is_superuser:
            return error404(request)
        context = {
            'updated': False,
            'user': user,
            'profile': profile,
            'errors': errors,
            'logged_in': True
        }
        return render(request, 'editprofile.html', context)
    else:
        if not PORTAL_STOP:
            user = User.objects.filter(username=request.user.username).first()
            profile = Profile.objects.filter(user=user).first()
            new_name = request.POST.get("name", "")
            errors = [0, 0, 0,0,0]
            if user.is_superuser:
                return error404(request)
            if len(new_name) < 50 and new_name != "":
                profile.full_name = new_name
            else:
                errors[0] = 1
            new_bio = request.POST.get("bio", "")
            new_bio = remove_emoji(new_bio)
            if len(new_bio) <= 500:
                profile.bio = new_bio
            else:
                errors[1] = 1
            new_mailid = request.POST.get("mailid", "")
            if len(new_mailid) <= 60:
                profile.gmailid = new_mailid
            else:
                errors[2] = 1
            new_address = request.POST.get("address", "")
            if len(new_address) <= 500:
                profile.address = new_address
            else:
                errors[3] = 1
            new_phoneno = request.POST.get("phoneno", "")
            if len(new_phoneno) == 10:
                profile.phoneno = new_phoneno
            else:
                errors[4] = 1
            profile.save()
            context = {
                'updated': True,
                'profile': profile,
                'errors': errors,
                'logged_in': True
            }
            if errors[0] + errors[1] + errors[2] + errors[3] + errors[4] == 0:
                return render(request, 'editprofile.html', context)
            else:
                context['updated'] = False
                return render(request, 'editprofile.html', context)
        else:
            return JsonResponse({'status': 0, 'error': "Sorry, all changes to the portal have been stopped."})


@login_required
def upload_profile_pic(request):
    if request.method == 'POST':
        if not PORTAL_STOP:
            user = User.objects.filter(username=request.user.username).first()
            profile = Profile.objects.filter(user=user).first()
            try:
                x = request.POST.get("x", "")
                x = float(x)
            except:
                return JsonResponse({'status': 0,
                                     'error': "Wrong crop details\nPlease provide an image which is larger than 500x500\nUse JPEG or PNG format"})
            try:
                y = request.POST.get("y", "")
                y = float(y)
            except:
                return JsonResponse({'status': 0,
                                     'error': "Wrong crop details\nPlease provide an image which is larger than 500x500\nUse JPEG or PNG format"})
            try:
                height = request.POST.get("height", "")
                height = float(height)
            except:
                return JsonResponse({'status': 0,
                                     'error': "Wrong crop details\nPlease provide an image which is larger than 500x500\nUse JPEG or PNG format"})
            try:
                width = request.POST.get("width", "")
                width = float(width)
            except:
                return JsonResponse({'status': 0,
                                     'error': "Wrong crop details\nPlease provide an image which is larger than 500x500\nUse JPEG or PNG format"})
            if width < 490 or height < 490:
                return JsonResponse({'status': 0,
                                     'error': "Wrong image size\nPlease provide an image which is larger than 500x500\nUse JPEG or PNG format"})
            try:
                uploaded_pic = request.FILES["profile_pic"]
                image = Image.open(uploaded_pic)
                image = ImageOps.exif_transpose(image)
                cropped_image = image.crop((x, y, width + x, height + y))
                resized_image = cropped_image.resize((500, 500), Image.ANTIALIAS)
            except:
                return JsonResponse({'status': 0,
                                     'error': "Error processing image\nPlease provide an image which is larger than 500x500\nUse JPEG or PNG format"})
            extension = uploaded_pic.name.split('.')[-1]
            profile_pic_path = os.path.join(profile_pic_upload_folder, user.username + '.' + extension.lower())
            resized_image.save(profile_pic_path)
            profile.profile_pic = os.path.join(Profile.profile_pic.field.upload_to,
                                               user.username + '.' + extension.lower())
            profile.save()
            return JsonResponse({'status': 1, 'message': "Profile Pic Changed Successfully"})
        else:
            return JsonResponse({'status': 0, 'error': "Sorry, all changes to the portal have been stopped."})
    else:
        return error404(request)


@login_required
@is_edited
def add_testimonial(request, username):
    if request.method == 'GET':
        return error404(request)
    else:
        if not PORTAL_STOP:
            given_by = User.objects.filter(username=request.user.username).first()
            given_by_profile = Profile.objects.filter(user=given_by).first()
            given_to = User.objects.filter(username=username).first()
            if given_to:
                if given_to == given_by:
                    return JsonResponse({'status': 0, 'error': "You can't write a testimonial for yourself"})
                given_to_profile = Profile.objects.filter(user=given_to).first()
                if not given_to_profile.graduating:
                    return JsonResponse(
                        {'status': 0, 'error': "You can't write a testimonial for non-graduating batch"})
                content = request.POST.get("content", "")
                content = remove_emoji(content)
                if len(content) <= 400 and content != "":
                    old_testimonial = Testimonial.objects.filter(given_to=given_to_profile,
                                                                 given_by=given_by_profile).first()
                    if old_testimonial:
                        old_testimonial.content = content
                        old_testimonial.save()
                        return JsonResponse({'status': 1, 'message': "edited"})
                    else:
                        Testimonial.objects.create(given_to=given_to_profile, given_by=given_by_profile,
                                                   content=content)
                        return JsonResponse({'status': 1, 'message': "added"})
                else:
                    return JsonResponse({'status': 0, 'error': "Testimonial size is " + str(
                        len(content)) + " characters, while maximum size allowed is 400 characters."})
            else:
                return JsonResponse({'status': 0, 'error': "User doesn't exist"})
        else:
            return JsonResponse({'status': 0, 'error': "Sorry, all changes to the portal have been stopped."})


@login_required
@is_edited
def delete_testimonial(request):
    if request.method == 'GET':
        return error404(request)
    else:
        if not PORTAL_STOP:
            user = User.objects.filter(username=request.user.username).first()
            testimonial_id = request.POST.get("testimonial_id", "-1")
            if not testimonial_id.isdecimal():
                return JsonResponse({'status': 0, 'error': "Testimonial doesn't exist"})
            testimonial = Testimonial.objects.filter(id=int(testimonial_id)).first()
            if testimonial:
                if user == testimonial.given_to.user or user == testimonial.given_by.user:
                    testimonial.delete()
                    return JsonResponse({'status': 1, 'message': "Testimonial deleted successfully"})
                else:
                    return JsonResponse({'status': 0, 'error': "You are not authorised to delete this"})
            else:
                return JsonResponse({'status': 0, 'error': "Testimonial doesn't exist"})
        else:
            return JsonResponse({'status': 0, 'error': "Sorry, all changes to the portal have been stopped."})


@login_required
@is_edited
def favourite_testimonial(request):
    if request.method == 'GET':
        return error404(request)
    else:
        if not PORTAL_STOP:
            user = User.objects.filter(username=request.user.username).first()
            user_profile = Profile.objects.filter(user=user).first()
            testimonial_id = request.POST.get("testimonial_id", "-1")
            if not testimonial_id.isdecimal():
                return JsonResponse({'status': 0, 'error': "Testimonial doesn't exist"})
            testimonial = Testimonial.objects.filter(id=int(testimonial_id)).first()
            if testimonial:
                if user == testimonial.given_to.user:
                    if testimonial.favourite:
                        testimonial.favourite = False
                        testimonial.save()
                        return JsonResponse({'status': 1, 'message': "Testimonial removed from favourites"})
                    else:
                        if Testimonial.objects.filter(given_to=user_profile, favourite=True).count() < 3:
                            testimonial.favourite = True
                            testimonial.save()
                            return JsonResponse({'status': 1, 'message': "Testimonial added to favourites"})
                        else:
                            return JsonResponse({'status': 0, 'error': "You can have only 3 favourite testimonials"})
                else:
                    return JsonResponse({'status': 0, 'error': "You are not authorised to favourite this testimonial"})
            else:
                return JsonResponse({'status': 0, 'error': "Testimonial doesn't exist"})
        else:
            return JsonResponse({'status': 0, 'error': "Sorry, all changes to the portal have been stopped."})


@login_required
@is_edited
def change_answer(request, username):
    if request.method == 'GET':
        return error404(request)
    else:
        if not PORTAL_STOP:
            user = User.objects.filter(username=request.user.username).first()
            profile_user = User.objects.filter(username=username).first()
            if user == profile_user:
                question_id = request.POST.get("question_id", "-1")
                profile = Profile.objects.filter(user=user).first()
                if not profile.graduating:
                    return JsonResponse({'status': 0, 'error': "Non-graduating batch can't answer profile questions"})
                if not question_id.isdecimal():
                    return JsonResponse({'status': 0, 'error': "Question doesn't exist"})
                new_answer = request.POST.get("answer", -1)
                if new_answer == -1:
                    return JsonResponse({'status': 0, 'error': "Answer size out of bounds"})
                if len(new_answer) <= 300:
                    question = ProfileQuestion.objects.filter(id=int(question_id)).first()
                    if question:
                        answer = ProfileAnswers.objects.filter(question=question, profile=profile).first()
                        if answer:
                            answer.answer = new_answer
                            answer.save()
                            return JsonResponse({'status': 1, 'message': "edited"})
                        else:
                            ProfileAnswers.objects.create(question=question, profile=profile, answer=new_answer)
                            return JsonResponse({'status': 1, 'message': "added"})
                    else:
                        return JsonResponse({'status': 0, 'error': "Question doesn't exist"})
                else:
                    return JsonResponse({'status': 0, 'error': "Answer size is " + str(
                        len(new_answer)) + " characters, while maximum size allowed is 300 characters."})
            else:
                return JsonResponse({'status': 0, 'error': "You are not authorised to change this"})
        else:
            return JsonResponse({'status': 0, 'error': "Sorry, all changes to the portal have been stopped."})


@login_required
@is_edited
def add_vote(request):
    if request.method == 'GET':
        return error404(request)
    else:
        if not POLL_STOP:
            user = User.objects.filter(username=request.user.username).first()
            user_profile = Profile.objects.filter(user=user).first()
            if not user_profile.graduating:
                return JsonResponse({'status': 0, 'error': "Non-graduating batch can't vote for polls"})
            vote_username = request.POST.get('voting_to', "")
            vote_user = User.objects.filter(username=vote_username).first()
            question_id = request.POST.get('question_id', "-1")
            origin = request.POST.get('origin', "polls")
            if not question_id.isdecimal():
                return JsonResponse({"status": 0, "error": "Poll doesn't exist"})
            poll_question = PollQuestion.objects.filter(id=int(question_id)).first()
            if not poll_question:
                return JsonResponse({"status": 0, "error": "Poll doesn't exist"})
            if not vote_user:
                return JsonResponse({"status": 0, "error": "Nominated user doesn't exist"})
            if origin != "home" and origin != "polls":
                origin = "polls"
            poll_answer = PollAnswer.objects.filter(voted_by=user_profile, question=poll_question).first()
            if poll_answer:
                poll_answer.answer = Profile.objects.filter(user=vote_user).first()
                poll_answer.save()
                return HttpResponseRedirect(reverse(origin))
            else:
                PollAnswer.objects.create(voted_by=user_profile, question=poll_question,
                                          answer=Profile.objects.filter(user=vote_user).first())
                return HttpResponseRedirect(reverse(origin))
        else:
            return JsonResponse({'status': 0, 'error': "Sorry, the polls have been freezed."})


def error404(request):
    if request.user and not request.user.is_anonymous:
        user = User.objects.filter(username=request.user.username).first()
        context = {
            'logged_in': True,
            'user': user
        }
        return render(request, '404.html', context)
    else:
        return render(request, '404.html')


@login_required
@is_edited
def polls(request):
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            logged_in = True
        else:
            logged_in = False
        if logged_in:
            user = User.objects.filter(username=request.user.username).first()
            poll_questions = PollQuestion.objects.all().order_by("question")
            polls = {}
            if user.is_superuser:
                for question in poll_questions:
                    answers = PollAnswer.objects.filter(question=question)
                    answers_count = answers.count()
                    poll_dict = {}
                    for answer in answers:
                        if answer.answer in poll_dict.keys():
                            poll_dict[answer.answer].append(answer.voted_by)
                        else:
                            poll_dict[answer.answer] = [answer.voted_by]
                    polls[(question, answers_count)] = sorted(poll_dict.items(), key=votes_sort_key, reverse=True)
                context = {
                    'polls': polls,
                    'user': user,
                    'logged_in': logged_in
                }
                return render(request, 'admin_home.html', context)
            else:
                user_profile = Profile.objects.filter(user=user).first()
                if not user_profile.graduating:
                    context = {
                        'user': user,
                        'user_profile': user_profile,
                        'logged_in': logged_in
                    }
                    return render(request, 'polls.html', context)
                else:
                    for question in poll_questions:
                        answers = PollAnswer.objects.filter(question=question)
                        myanswer = answers.filter(voted_by=user_profile).first()
                        if myanswer:
                            myanswer = myanswer.answer
                        else:
                            myanswer = None
                        poll_nominees = []
                        for answer in answers:
                            if answer.answer not in poll_nominees:
                                poll_nominees.append(answer.answer)
                        polls[(question, myanswer)] = sorted(poll_nominees, key=nominees_sort_key)
                    context = {
                        'polls': polls,
                        'user': user,
                        'user_profile': user_profile,
                        'logged_in': logged_in
                    }
                    return render(request, 'polls.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    else:
        return error404(request)


@login_required
@is_edited
def write_testimonial(request):
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            logged_in = True
        else:
            logged_in = False
        if logged_in:
            user = User.objects.filter(username=request.user.username).first()
            profiles = Profile.objects.filter(graduating=True).order_by(Lower("full_name"))
            user_profile = Profile.objects.filter(user=user).first()
            testimonials = Testimonial.objects.filter(given_by=user_profile).order_by('-id')
            context = {
                'user': user,
                'profiles': profiles,
                'logged_in': logged_in,
                'testimonials': testimonials
            }
            return render(request, 'write_testimonial.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    else:
        return error404(request)


def team(request):
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            logged_in = True
        else:
            logged_in = False
        if logged_in:
            user = User.objects.filter(username=request.user.username).first()
            members = Team_Member.objects.all().order_by('position')
            context = {
                'user': user,
                'logged_in': logged_in,
                'team_members': members
            }
            print(members)
            return render(request, 'team_mem.html', context)
        else:
            members = Team_Member.objects.all().order_by('position')
            context = {
                'logged_in': logged_in,
                'team_members': members
            }
            return render(request, 'team_mem.html', context)
    else:
        return error404(request)


@login_required
@is_edited
def leaderboard(request):
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            logged_in = True
        else:
            logged_in = False
        if logged_in:
            user = User.objects.filter(username=request.user.username).first()

            lead = (Leaderboard.objects.all().order_by('-pub_date'))[0]
            sorted_d = []
            sorted_d.append((lead.profile_0,lead.cnt_0))
            sorted_d.append((lead.profile_1,lead.cnt_1))
            sorted_d.append((lead.profile_2,lead.cnt_2))
            sorted_d.append((lead.profile_3,lead.cnt_3))
            sorted_d.append((lead.profile_4,lead.cnt_4))
            sorted_d.append((lead.profile_5,lead.cnt_5))
            sorted_d.append((lead.profile_6,lead.cnt_6))
            sorted_d.append((lead.profile_7,lead.cnt_7))
            sorted_d.append((lead.profile_8,lead.cnt_8))
            sorted_d.append((lead.profile_9,lead.cnt_9))
            last_updated = (lead.pub_date + timedelta(hours=5,minutes=30)).strftime("%H:%M, %b %d")
            announce=list(Announcement.objects.all().order_by('-pub_date'))

            context = {
                'user': user,
                'logged_in': logged_in,
                'lead_dict': sorted_d,
                'announce_list': announce,
                'last_updated': last_updated
            }
            return render(request, 'leaderboard.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    else:
        return error404(request)

# @login_required
@is_edited
def leaderboardnew(request):
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            logged_in = True
        else:
            logged_in = False
        if logged_in:
            user = User.objects.filter(username=request.user.username).first()

            lead = (Leaderboard.objects.all().order_by('-pub_date'))[0]
            sorted_d = []
            sorted_d.append((lead.profile_0,lead.cnt_0))
            sorted_d.append((lead.profile_1,lead.cnt_1))
            sorted_d.append((lead.profile_2,lead.cnt_2))
            sorted_d.append((lead.profile_3,lead.cnt_3))
            sorted_d.append((lead.profile_4,lead.cnt_4))
            sorted_d.append((lead.profile_5,lead.cnt_5))
            sorted_d.append((lead.profile_6,lead.cnt_6))
            sorted_d.append((lead.profile_7,lead.cnt_7))
            sorted_d.append((lead.profile_8,lead.cnt_8))
            sorted_d.append((lead.profile_9,lead.cnt_9))
            last_updated = (lead.pub_date + timedelta(hours=5,minutes=30)).strftime("%H:%M, %b %d")
            announce=list(Announcement.objects.all().order_by('-pub_date'))

            context = {
                'user': user,
                'logged_in': logged_in,
                'lead_dict': sorted_d,
                'announce_list': announce,
                'last_updated': last_updated
            }
            return render(request, 'leaderboardnew.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    else:
        return error404(request)


@login_required
@is_edited
def update_leaderboard(request):
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            logged_in = True
        else:
            logged_in = False
        if logged_in:
            user = User.objects.filter(username=request.user.username).first()
            if user.is_superuser:
                given_to_list = [testi.given_to for testi in Testimonial.objects.all()]
                given_to_counter = collections.Counter(given_to_list)
                sorted_d = sorted(given_to_counter.items(), key=lambda x: x[1], reverse=True)
                if len(sorted_d)>10:
                    sorted_d=sorted_d[0:10]
                while len(sorted_d)<10:
                    sorted_d.append(sorted_d[len(sorted_d)-1])
                
                Leaderboard.objects.create(
                    profile_0=sorted_d[0][0],
                    profile_1=sorted_d[1][0],
                    profile_2=sorted_d[2][0],
                    profile_3=sorted_d[3][0],
                    profile_4=sorted_d[4][0],
                    profile_5=sorted_d[5][0],
                    profile_6=sorted_d[6][0],
                    profile_7=sorted_d[7][0],
                    profile_8=sorted_d[8][0],
                    profile_9=sorted_d[9][0],
                    cnt_0=sorted_d[0][1],
                    cnt_1=sorted_d[1][1],
                    cnt_2=sorted_d[2][1],
                    cnt_3=sorted_d[3][1],
                    cnt_4=sorted_d[4][1],
                    cnt_5=sorted_d[5][1],
                    cnt_6=sorted_d[6][1],
                    cnt_7=sorted_d[7][1],
                    cnt_8=sorted_d[8][1],
                    cnt_9=sorted_d[9][1])
                
            return HttpResponseRedirect(reverse('leaderboard'))
        else:
            return HttpResponseRedirect(reverse('login'))
    else:
        return error404(request)


@login_required
@is_edited
def auto_mark_favs(request):
    if request.method == 'GET':
        if request.user and not request.user.is_anonymous:
            logged_in = True
        else:
            logged_in = False
        if logged_in:
            user = User.objects.filter(username=request.user.username).first()
            if user.is_superuser:
                # main code
                # print("Started")
                all_profiles = Profile.objects.all()
                for pro in all_profiles:
                    if pro.graduating:
                        # print(pro.full_name)
                        testimonials = Testimonial.objects.filter(given_to=pro).order_by('-favourite',Length('content').desc(),'-id')[:3]
                        fav_cnt=0
                        for tes in testimonials:
                            if tes.favourite:
                                fav_cnt+=1
                            # print("    "+tes.given_by.full_name+" "+str(tes.favourite))
                        if fav_cnt==0:
                            for tes in testimonials:
                                tes.favourite=True
                                tes.save()
                        # for tes in testimonials:
                        #     print("    "+tes.given_by.full_name+" "+str(tes.favourite))
                        
            return HttpResponseRedirect(reverse('leaderboard'))
        else:
            return HttpResponseRedirect(reverse('login'))
    else:
        return error404(request)