from django.contrib import admin
from . models import *
from mptt.admin import MPTTModelAdmin

# admin.site.register(Tweet)
@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('user','created_at','tweet_id')
    list_filter = ('user','created_at')
    search_fields = ('body',)
    prepopulated_fields = {'slug': ('body',)}
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at','-updated_at')

    def tweet_id(self, obj):
        return obj.id



@admin.register(UploadedImageTweet)
class UploadedImageTweetAdmin(admin.ModelAdmin):
    list_display = ('tweet', 'tweet_id')

    def tweet_id(self, obj):
        return obj.tweet.id


admin.site.register(Profile)
admin.site.register(Vote)
# admin.site.register(Relation)
@admin.register(Relation)
class UploadedImageTweetAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user','show')
admin.site.register(Block)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'tweet_id', 'created_at' ]

    def tweet_id(self, obj):
        if obj.tweet:
            return obj.tweet.id
        return 'No tweet available'

admin.site.register(Comment, MPTTModelAdmin)

@admin.register(Mychats)
class MychatAdmin(admin.ModelAdmin):
    list_display = ('id','me','frnd','chats')

admin.site.register(TweetCommentDisLike)
admin.site.register(TweetCommentLike)
admin.site.register(BookVote)
admin.site.register(BookComment)
admin.site.register(BookCommentLike)
admin.site.register(BookCommentDisLike)
admin.site.register(RecommendedBookUser)
admin.site.register(RegistrationRequestedBook)
admin.site.register(DontShowNotificationRegistrationRequestedBook)
admin.site.register(Cart)


@admin.register(SaleBook)
class UploadedImageTweetAdmin(admin.ModelAdmin):
    list_display = ('user', 'status','name_book','category')

@admin.register(Factor)
class UploadedImageTweetAdmin(admin.ModelAdmin):
    list_display = ('buyer','Seller','book','status')