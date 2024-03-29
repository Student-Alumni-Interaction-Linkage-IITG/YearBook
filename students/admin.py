from django.contrib import admin
from students.models import Profile, Testimonial, ProfileQuestion, ProfileAnswers, PollQuestion, PollAnswer, Announcement, Leaderboard, Team_Member
from import_export.admin import ExportActionMixin

# Register your models here.

class ProfileAdmin(ExportActionMixin, admin.ModelAdmin):
    search_fields = ('user__first_name', 'full_name', 'rollno', 'program', 'department', 'graduating')
    list_display = ('__str__', 'user', 'full_name', 'rollno', 'program', 'department', 'graduating')


class TestimonialAdmin(ExportActionMixin, admin.ModelAdmin):
    search_fields = (
        'given_by__user__username', 'given_to__user__username', 'given_by__user__first_name',
        'given_to__user__first_name',
        'given_by__full_name', 'given_to__full_name')
    list_display = ('__str__', 'given_by', 'given_to', 'favourite')


class ProfileAnswersAdmin(ExportActionMixin, admin.ModelAdmin):
    search_fields = ('profile__user__username', 'profile__user__first_name', 'profile__full_name', 'question__question')
    list_display = ('__str__', 'profile', 'question')


class PollAnswerAdmin(ExportActionMixin, admin.ModelAdmin):
    search_fields = (
        'voted_by__user__username', 'voted_by__user__first_name', 'voted_by__full_name', 'answer__user__username',
        'answer__user__first_name', 'answer__full_name', 'question__question')
    list_display = ('__str__', 'voted_by', 'question', 'answer')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(ProfileQuestion)
admin.site.register(ProfileAnswers, ProfileAnswersAdmin)
admin.site.register(PollQuestion)
admin.site.register(PollAnswer, PollAnswerAdmin),
admin.site.register(Announcement),
admin.site.register(Leaderboard)
admin.site.register(Team_Member)