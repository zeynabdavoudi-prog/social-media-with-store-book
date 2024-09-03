from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth.models import User
from . forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import *
from django.utils.text import slugify
from langdetect import detect
from googletrans import Translator
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from taggit.models import Tag
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from django.db.models import Count
class LoginView(View):
    form_class = UserLoginForm
    template_name = 'book/children/login.html'

    def setup(self, request, *args, **kwargs):
        self.next= request.GET.get('next')
        super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('book:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form=self.form_class()
        return render(request, self.template_name,{'form':form})
    def post(self, request):
        form=self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username_email'], password=cd['password'])
            if user is not None:
                login(request, user)
                if self.next:
                    return redirect(self.next)
                return redirect('book:home')
            messages.error(request,'نام کاربری/ایمیل یا رمز عبور اشتباه است','danger')
            return render(request, self.template_name, {'form': form})
        messages.error(request, 'capchaاشتباه است', 'danger')
        return render(request, self.template_name, {'form': form})

class LogoutView(LoginRequiredMixin,View):
    def get(self, request):
        logout(request)
        return redirect('book:home')

class RegisterView(View):
    form_class =UserRegisterForm
    template_name = 'book/children/register.html'


    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name,{'form':form})
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user= User.objects.create_user(cd['username'], cd['email'], cd['password'])
            Profile.objects.create(user=user)
            messages.success(request,'ثبت نام شما با موفقیت انجام شد',"success")
            login(request, user,backend='django.contrib.auth.backends.ModelBackend')

            return redirect('book:home')
        return render(request, self.template_name,{'form':form})

class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'book/password/password_reset_form.html'
    success_url = reverse_lazy('book:password_reset_done')
    email_template_name = 'book/password/password_reset_email.html'

class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'book/password/password_reset_done.html'

class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'book/password/password_reset_confirm.html'
    success_url = reverse_lazy('book:password_reset_complete')

class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'book/password/password_reset_complete.html'

class TweetView(View):
    template_name = 'book/children/tweet.html'
    form_class = UploadTweet
    def get(self, request,type_tweet=0):

        # show tweet
        six_months_ago = timezone.now() - timedelta(days=180)

        tweets = Tweet.objects.filter(Q(created_at__gte=six_months_ago) | Q(updated_at__gte=six_months_ago)).order_by('-updated_at','-created_at')
        image_tweet=UploadedImageTweet.objects.filter(created_at__gte=six_months_ago)
        tweet_with_image = []
        # tweets = Tweet.objects.all()
        # image_tweet=UploadedImageTweet.objects.all()
        for tweet in tweets:
            for image in image_tweet:
                if tweet.id==image.tweet.id:
                    tweet_with_image.append(tweet.id)

        #profile
        profiles=Profile.objects.all()
        #vote
        user_vote=[]
        #modal votes=Vote.objects.all()
        #upload tweet
        form = self.form_class()
        #show profile user
        if request.user.is_authenticated:

            user_blockf=Block.objects.filter(from_user=request.user)
            blocked_user_idsf = [block.to_user.id for block in user_blockf]
            user_blockt = Block.objects.filter(to_user=request.user)
            blocked_user_idst = [block.from_user.id for block in user_blockt]
            blocked_user_ids=blocked_user_idst+blocked_user_idsf
            tweets = tweets.exclude(user_id__in=blocked_user_ids)

            # shre tweet with chat
            frnds_follower = Relation.objects.filter(from_user=request.user)
            frnds_folower_id = [frnd.to_user.id for frnd in frnds_follower]
            frnds_chat = Mychats.objects.filter(frnd=request.user)
            frnds_chat_id = [frnd.me.id for frnd in frnds_chat]
            frnds_id = frnds_folower_id + frnds_chat_id
            frnds = User.objects.filter(id__in=frnds_id)


            if type_tweet == 1:
                # relation
                relation_list = []
                relations = Relation.objects.filter(from_user=request.user)
                for relation in relations:
                    relation_list.append(relation.to_user.id)
                tweets = []
                # for relation in relation_list:
                #     user=User.objects.get(id=relation)

                    # if Tweet.objects.filter(user=user):
                    #     tweets.append(Tweet.objects.filter(Q(user=user) & (Q(created_at__gte=six_months_ago) | Q(updated_at__gte=six_months_ago))))
                    #     # tweets.append(Tweet.objects.get(user=user))
                    #
                tweets=Tweet.objects.filter(Q(user__in=relation_list) & (Q(created_at__gte=six_months_ago) | Q(updated_at__gte=six_months_ago)))
                tweets = tweets.exclude(user_id__in=blocked_user_ids)
                if (len(tweets)==0):
                    messages.info(request,"توییتی برای نمایش وجود ندارد",'info')
                    return redirect('book:tweet')
                image_tweet=UploadedImageTweet.objects.filter(created_at__gte=six_months_ago)
                tweet_with_image = []
                # image_tweet = UploadedImageTweet.objects.all()
                for tweet in tweets:
                    for image in image_tweet:
                        if tweet.id == image.tweet.id:
                            tweet_with_image.append(tweet.id)


            profile=Profile.objects.get(user=request.user)
            user_vote_tweet=Vote.objects.filter(user=request.user)
            for vote in user_vote_tweet:
                user_vote.append(vote.tweet.id)
            context={'form':form,'tweets':tweets,
                     'image_tweet':image_tweet,
                     'tweet_with_image':tweet_with_image,
                     'profile':profile,'user_vote':user_vote,
                     'profiles':profiles,
                     'frnds':frnds}
        else:
            context={'form':form,'tweets':tweets,
                     'image_tweet':image_tweet,
                     'tweet_with_image':tweet_with_image,
                     'profiles':profiles}

        return render(request, self.template_name,context)

    def post(self,request,type_tweet=0):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            new_tweet=Tweet.objects.create(user=request.user)
            cd=form.cleaned_data
            new_tweet.body=cd['body']
            language=detect(cd['body'])
            if language=='fa':
                translator=Translator()
                translated_text=translator.translate(cd['body'],src='fa',dest='en')
                text=translated_text.text
                new_tweet.slug=slugify(text[:30])
            else:
                new_tweet.slug=slugify(cd['body'][:30])
            all_tags=cd['tags'].split(',')
            for tag in all_tags:
                new_tweet.tags.add(tag)
            new_tweet.save()
            for uploaded_file in request.FILES.getlist('files'):
                UploadedImageTweet.objects.create(file=uploaded_file,tweet=new_tweet )
        previous_page = request.META.get('HTTP_REFERER')
        return redirect(previous_page)




class ProfileView(LoginRequiredMixin,View):
    template_name ='book/children/profile.html'
    def get(self, request,user_id,number_nav=1):
        user = User.objects.get(pk=user_id)
        profile=Profile.objects.get(user=user)
        tweet=Tweet.objects.filter(user=user)
        following=Relation.objects.filter(from_user=user)
        follower=Relation.objects.filter(to_user=user)
        relation_following=[]
        for follow in following:

            relation_following.append(follow.to_user.id)
        following_request_user=Relation.objects.filter(from_user=request.user)
        following_request_user_list=[]
        for follow in following_request_user:
            following_request_user_list.append(follow.to_user.id)
        # button follow and unfollow
        relation_list=[]
        for relation in follower:
            relation_list.append(relation.from_user.id)
        profile_all=Profile.objects.all()
        # block
        # if request user block owner profile
        is_block=False
        if Block.objects.filter(from_user=request.user, to_user=user).exists():
            is_block=True
        #if owner profile block request user
        variable ='f'
        if Block.objects.filter(from_user=user, to_user=request.user).exists():
            variable ='t'
        # list id users that request.user block them
        list_block_requestuser=Block.objects.filter(from_user=request.user)
        list_block_requestuser_id= [block.to_user.id for block in list_block_requestuser ]

        context={'user':user,'profile':profile,
                'tweet':tweet,'following':following,
                 'follower':follower,'relation_list':relation_list,
                 'profile_all':profile_all,'relation_following':relation_following,
                 'following_request_user_list':following_request_user_list,
                 'is_block':is_block,
                 'variable':variable,'list_block_requestuser_id':list_block_requestuser_id}

        tweet_with_image = []
        image_tweet = UploadedImageTweet.objects.all()


        # show tweet user
        if number_nav == 1:
            id=1
            tweets=Tweet.objects.filter(user=user).order_by('-updated_at','-created_at')

            for tweet in tweets:
                for image in image_tweet:
                    if tweet.id == image.tweet.id:
                        tweet_with_image.append(tweet.id)
            context.update({'tweets':tweets,'tweet_with_image':tweet_with_image,'image_tweet':image_tweet,'id':id})

        #show tweets that user like it
        if number_nav == 2:
            id=2
            votes=Vote.objects.filter(user=user)
            vote_list=[]
            for vote in votes:
                vote_list.append(vote.tweet.id)
            tweets=Tweet.objects.filter(id__in=vote_list).order_by('-updated_at','-created_at')


            for tweet in tweets:
                for image in image_tweet:
                    if tweet.id == image.tweet.id:
                        tweet_with_image.append(tweet.id)

            # block

            user_blockf = Block.objects.filter(from_user=user)
            blocked_user_idsf = [block.to_user.id for block in user_blockf]
            user_blockt = Block.objects.filter(to_user=user)
            blocked_user_idst = [block.from_user.id for block in user_blockt]
            blocked_user_ids = blocked_user_idst + blocked_user_idsf
            tweets = tweets.exclude(user_id__in=blocked_user_ids)




            context.update({'tweets':tweets,'tweet_with_image':tweet_with_image,'image_tweet':image_tweet,'id':id})

        if number_nav == 3:
            id=3

            sale_books=SaleBook.objects.filter(user=user)
            context.update({"sale_books":sale_books,'id':id})

        if number_nav == 4:
            id=4
            recommended_book=RecommendedBookUser.objects.filter(user=request.user).order_by('-created_at')
            context.update({'id':id,'recommended_book':recommended_book})

        return render(request, self.template_name,context )

class EditProfileView(LoginRequiredMixin,View):
    template_name ='book/children/editprofile.html'
    form_class = EditProfileForm
    def dispatch(self, request, *args, **kwargs):
        if request.user.id!=kwargs['user_id']:
            messages.error(request, 'شما اجازه دسترسی به این صفحه را ندارید','danger')
            return redirect('book:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self,request,user_id):
        user = User.objects.get(pk=user_id)
        profile=Profile.objects.get(user=user)
        form=self.form_class(instance=profile,initial={'first_name':user.first_name,'last_name':user.last_name})
        return render(request, self.template_name, {'form':form,'profile':profile})

    def post(self,request,user_id):
        user = User.objects.get(pk=user_id)
        profile=Profile.objects.get(user=user)
        form=self.form_class(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            user.first_name=cd['first_name']
            user.last_name=cd['last_name']
            user.save()
            return redirect('book:user_profile', user.id)
        return render(request, self.template_name, {'form': form})

class TweetLikeView(LoginRequiredMixin, View):
    def get(self,request,tweet_id):
        tweet = Tweet.objects.get(pk=tweet_id)
        like=Vote.objects.filter(user=request.user,tweet=tweet)
        if like.exists():
            like.delete()
            return JsonResponse({'response': 'unliked'})

        else:
            Vote.objects.create(user=request.user,tweet=tweet)
            return JsonResponse({'response': 'liked'})


class UserRelationsView(LoginRequiredMixin, View):
    def get(self,request,user_id):
        user=User.objects.get(pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            return JsonResponse({'response': 'unfollow'})
        else:
            Relation.objects.create(from_user=request.user, to_user=user)
            return JsonResponse({'response': 'follow'})



class TweetDetailView( View):
    template_name = 'book/children/tweet_detail.html'
    form_class =CommentCreateForm
    # form_class_reply=CommentReplyForm

    def setup(self,request,*args,**kwargs):
        self.tweet=Tweet.objects.get(pk=kwargs['tweet_id'],slug=kwargs['tweet_slug'])
        self.images = UploadedImageTweet.objects.filter(tweet=self.tweet)
        self.profiles = Profile.objects.all()
        self.votes = Vote.objects.all()
        self.comments=Comment.objects.filter(tweet=self.tweet)
        if request.user.is_authenticated:
            self.user_vote = Vote.objects.filter(user=request.user.id, tweet=self.tweet)
            # relation
            self.relation_list = []
            relations = Relation.objects.filter(from_user=request.user)
            for relation in relations:
                self.relation_list.append(relation.to_user.id)

            # block
            user_blockf = Block.objects.filter(from_user=request.user)
            blocked_user_idsf = [block.to_user.id for block in user_blockf]
            user_blockt = Block.objects.filter(to_user=request.user)
            blocked_user_idst = [block.from_user.id for block in user_blockt]
            self.blocked_user_ids = blocked_user_idst + blocked_user_idsf

            # shre tweet with chat
            frnds_follower = Relation.objects.filter(from_user=request.user)
            frnds_folower_id = [frnd.to_user.id for frnd in frnds_follower]
            frnds_chat = Mychats.objects.filter(frnd=request.user)
            frnds_chat_id = [frnd.me.id for frnd in frnds_chat]
            frnds_id = frnds_folower_id + frnds_chat_id
            self.frnds = User.objects.filter(id__in=frnds_id)



            commnet_like_request_user=TweetCommentLike.objects.filter(user=request.user)
            self.commnet_like_request_user_id = [comment.comment.id for comment in commnet_like_request_user]

            commnet_dislike_request_user = TweetCommentDisLike.objects.filter(user=request.user)
            self.commnet_dislike_request_user_id = [comment.comment.id for comment in commnet_dislike_request_user]

        return super().setup(request,*args,**kwargs)
    def get(self,request,tweet_slug,tweet_id):
        tweet=self.tweet
        votes=self.votes
        images=self.images
        profiles=self.profiles
        form=self.form_class()
        # form_reply=self.form_class_reply()
        comments=self.comments


        if request.user.is_authenticated:
            user_vote=self.user_vote

            # relation
            relation_list =self.relation_list

            # user=User.objects.get(pk=request.user.id)
            context={'tweet':tweet,
                     'images':images,
                     'profiles':profiles,
                     'user_vote':user_vote,
                     'votes':votes,'relation_list':relation_list,
                     'form':form,
                     'comments':comments,
                     # 'form_reply':form_reply,
                     'blocked_user_ids':self.blocked_user_ids,
                     'frnds':self.frnds,
                     'commnet_like_request_user_id':self.commnet_like_request_user_id,
                     'commnet_dislike_request_user_id':self.commnet_dislike_request_user_id}
        else:
            context={'tweet':tweet,'images':images,
                     'profiles':profiles,'votes':votes,
                     'comments':comments}

        return render(request,self.template_name,context)
    @method_decorator(login_required)
    def post(self,request,tweet_slug,tweet_id):
        tweet = self.tweet
        votes = self.votes
        images = self.images
        profiles = self.profiles
        user_vote = self.user_vote
        # relation
        relation_list = self.relation_list
        comments = self.comments
        form=self.form_class(request.POST)
        if form.is_valid():
            # print(form.cleaned_data['parent'])
            new_comment=form.save(commit=False)

            new_comment.user=request.user
            new_comment.tweet=tweet

            new_comment.save()
            return redirect('book:tweet_detail', tweet.slug , tweet.id)

        context={'tweet':tweet,'images':images,
                 'profiles':profiles,'user_vote':user_vote,
                 'votes':votes,'relation_list':relation_list,
                 'form':form,'comments':comments,
                 'blocked_user_ids':self.blocked_user_ids,
                 'frnds':self.frnds,
                 'commnet_like_request_user_id':self.commnet_like_request_user_id,
                 'commnet_dislike_request_user_id':self.commnet_dislike_request_user_id}

        return render(request,self.template_name ,context=context)





class ShareTweetView(LoginRequiredMixin, View):

    form_class=ShareTweetForm
    template_name='book/children/share_tweet.html'
    def get(self,request,tweet_id=None,book_id=None):
        if tweet_id:
            title = 'توییت'
        elif book_id:
            title = 'کتاب'
        sent = False
        form = self.form_class()
        return render(request,self.template_name,{'form':form,'sent':sent,'title':title})
    def post(self,request,tweet_id=None,book_id=None):
        sent=False
        if tweet_id is not None:
            tweet=Tweet.objects.get(id=tweet_id)
            title='توییت'
        elif book_id is not None:
            book=SaleBook.objects.get(id=book_id)
            title='کتاب'

        form=self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            to = cd['to']
            message = cd['message']
            if tweet_id is not None:
                tweet_url=request.build_absolute_uri(tweet.get_absolute_url())
                subject = "{0}شما را به خواندن توییتی از سایت NetBookدعوت کرده است.".format(request.user.first_name)
                msg = ("{0}شما را به خواندن توییتی به ادرس زیر دعوت کرده است{1}{2}{3}{4}".

                       format(request.user.first_name, '\n', message, '\n', tweet_url))
            elif book_id is not None:
                book_url = request.build_absolute_uri(book.get_absolute_url())
                subject = "{0}شما را به خواندن کتابی از سایت NetBookدعوت کرده است.".format(request.user.first_name)
                msg = ("{0}شما را به خواندن کتابی به ادرس زیر دعوت کرده است{1}{2}{3}{4}".

                       format(request.user.first_name, '\n', message, '\n', book_url))


            send_mail(subject,msg,'zeynabdavoudi3@gmail.com',[to],fail_silently=False)
            sent=True

        return render(request,self.template_name,{'sent':sent,'form':form,'title':title})

class AboutUsView(View):
    template_name='book/children/about_us.html'
    def get(self, request):
        return render(request,self.template_name)

class ContactUsView(View):
    template_name='book/children/contact_us.html'
    form_class=ContactUsForm
    def get(self, request):
        sent=False
        form=self.form_class()
        return render(request,self.template_name,{'sent':sent,'form':form})
    def post(self,request):
        sent=False
        form=self.form_class(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            subject=cd['subject']
            message=cd['message']
            phone=cd['phone']
            full_name=cd['full_name']
            email=cd['email']
            msg='name:{0}\nphone:{1}\nemail:{2}\nmessage:\n{3}'.format(full_name,phone,email,message)
            send_mail(subject, msg,'zeynabdavoudi3@gmail.com',['zeynabdavoudi3@gmail.com'],fail_silently=False)
            sent=True
        return render(request,self.template_name,{'sent':sent,'form':form})

class SearchTweetView(View):
    template_name='book/children/search_tweet.html'
    def setup(self, request, *args, **kwargs):
        self.query_name = request.POST.get('search_input')
        if self.query_name:
            request.session['search_input'] = self.query_name
        self.profiles = Profile.objects.all()

        # self.votes = Vote.objects.all()
        if request.user.is_authenticated:
            # relation
            self.relation_list = []
            relations = Relation.objects.filter(from_user=request.user)
            for relation in relations:
                self.relation_list.append(relation.to_user.id)

            self.user_vote = []
            user_vote_tweet = Vote.objects.filter(user=request.user)
            for vote in user_vote_tweet:
                self.user_vote.append(vote.tweet.id)
            # block
            user_blockf = Block.objects.filter(from_user=request.user)
            self.blocked_user_idsf = [block.to_user.id for block in user_blockf]
            user_blockt = Block.objects.filter(to_user=request.user)
            self.blocked_user_idst = [block.from_user.id for block in user_blockt]
            self.blocked_user_ids = self.blocked_user_idst + self.blocked_user_idsf

            # shre tweet with chat
            frnds_follower = Relation.objects.filter(from_user=request.user)
            frnds_folower_id = [frnd.to_user.id for frnd in frnds_follower]
            frnds_chat = Mychats.objects.filter(frnd=request.user)
            frnds_chat_id = [frnd.me.id for frnd in frnds_chat]
            frnds_id = frnds_folower_id + frnds_chat_id
            self.frnds = User.objects.filter(id__in=frnds_id)

        return super().setup(request, *args, **kwargs)

    def post(self,request):
        if self.query_name:
            user_filter=User.objects.annotate(search=SearchVector('username','first_name','last_name')).filter(search=self.query_name)
            tweets=(Tweet.objects.annotate(search=SearchVector('body')).filter(search=self.query_name).order_by('-updated_at','-created_at'))

            # votes=self.votes
            tweet_with_image = []
            image_tweet = UploadedImageTweet.objects.all()
            for tweet in tweets:
                for image in image_tweet:
                    if tweet.id == image.tweet.id:
                        tweet_with_image.append(tweet.id)
            profiles=self.profiles
            if request.user.is_authenticated:
                # block

                tweets = tweets.exclude(user_id__in=self.blocked_user_ids)

                relation_list=self.relation_list
                user_vote=self.user_vote

                context={'user_filter':user_filter,
                         'profiles':profiles,'tweets':tweets,
                         'tweet_with_image':tweet_with_image,
                         'image_tweet':image_tweet,'user_vote':user_vote,
                         'query':self.query_name,'relation_list':relation_list,
                         'blocked_user_idsf':self.blocked_user_idsf,
                         'blocked_user_idst':self.blocked_user_idst,
                         'frnds':self.frnds}
            else:
                blocked_user_idst=['']
                context={'user_filter':user_filter,
                         'profiles':profiles,'tweets':tweets,
                         'tweets_with_image':tweet_with_image,
                         'image_tweet':image_tweet,'query':self.query_name,
                         'blocked_user_idst':blocked_user_idst}

            return render(request,self.template_name,context)
        else:
            return redirect('book:tweet')
    def get(self,request):
            query=request.session.get('search_input')
            user_filter=User.objects.annotate(search=SearchVector('username','first_name','last_name')).filter(search=query)
            tweets=Tweet.objects.annotate(search=SearchVector('body')).filter(search=query).order_by('-updated_at','-created_at')

            tweet_with_image = []
            image_tweet = UploadedImageTweet.objects.all()
            for tweet in tweets:
                for image in image_tweet:
                    if tweet.id == image.tweet.id:
                        tweet_with_image.append(tweet.id)

            profiles = self.profiles


            if request.user.is_authenticated:
                # block

                tweets = tweets.exclude(user_id__in=self.blocked_user_ids)
                relation_list = self.relation_list
                user_vote = self.user_vote
                context={'user_filter':user_filter,
                         'profiles':profiles,'tweets':tweets,
                         'tweet_with_image':tweet_with_image,
                         'image_tweet':image_tweet,'user_vote':user_vote,
                         'query':query,'relation_list':relation_list,
                         'blocked_user_idsf':self.blocked_user_idsf,
                         'blocked_user_idst': self.blocked_user_idst,
                         'frnds':self.frnds}
            else:
                blocked_user_idst = ['']
                context={'user_filter':user_filter,
                         'profiles':profiles,'tweets':tweets,
                         'tweets_with_image':tweet_with_image,
                         'image_tweet':image_tweet,'query':query,
                         'blocked_user_idst':blocked_user_idst}

            return render(request,self.template_name,context)


class SearchTagView(View):
    template_name = 'book/children/search_tag.html'
    def get(self,request,tag_id):
        tag = Tag.objects.get(id=tag_id)

        tweets=Tweet.objects.filter(tags__id=tag_id).order_by('-updated_at','-created_at')

        profiles = Profile.objects.all()

        tweet_with_image = []
        image_tweet = UploadedImageTweet.objects.all()
        for tweet in tweets:
            for image in image_tweet:
                if tweet.id == image.tweet.id:
                    tweet_with_image.append(tweet.id)

        # votes = Vote.objects.all()

        if request.user.is_authenticated:
            # relation
            # relation_list = []
            # relations = Relation.objects.filter(from_user=request.user)
            # for relation in relations:
            #     relation_list.append(relation.to_user.id)

            #block

            user_blockf = Block.objects.filter(from_user=request.user)
            blocked_user_idsf = [block.to_user.id for block in user_blockf]
            user_blockt = Block.objects.filter(to_user=request.user)
            blocked_user_idst = [block.from_user.id for block in user_blockt]
            blocked_user_ids = blocked_user_idst + blocked_user_idsf
            tweets = tweets.exclude(user_id__in=blocked_user_ids)

            # shre tweet with chat
            frnds_follower = Relation.objects.filter(from_user=request.user)
            frnds_folower_id = [frnd.to_user.id for frnd in frnds_follower]
            frnds_chat = Mychats.objects.filter(frnd=request.user)
            frnds_chat_id = [frnd.me.id for frnd in frnds_chat]
            frnds_id = frnds_folower_id + frnds_chat_id
            frnds = User.objects.filter(id__in=frnds_id)

            user_vote = []
            user_vote_tweet = Vote.objects.filter(user=request.user)
            for vote in user_vote_tweet:
                user_vote.append(vote.tweet.id)
            context={'tweets':tweets,
                     'profiles':profiles,
                     'tweet_with_image':tweet_with_image,
                     'image_tweet':image_tweet,
                     'user_vote':user_vote,'tag':tag,
                     'frnds':frnds}
        else:
            context={'tweets':tweets,
                     'profiles':profiles,
                     'tweet_with_image':tweet_with_image,
                     'image_tweet':image_tweet,'tag':tag}

        return render(request,self.template_name,context)

class DeleteTweetView(LoginRequiredMixin,View):
    def get(self,request,tweet_id):
        tweet=Tweet.objects.get(id=tweet_id)
        if request.user.id != tweet.user.id:
            messages.error(request,"شما اجازه حذف این توییت را ندارید",'danger')
            return redirect('book:tweet')
        else:
            tweet.delete()
            messages.success(request,"توییت حذف شد",'success')
            return redirect('book:tweet')

class UpdateTweetView(LoginRequiredMixin,View):
    form_class = UpdateTweetForm
    template_name = 'book/children/update_tweet.html'
    def setup(self, request, *args, **kwargs):
        self.tweet=Tweet.objects.get(id=kwargs['tweet_id'])
        self.images=UploadedImageTweet.objects.filter(tweet=self.tweet)
        return super().setup(request, *args, **kwargs)
    def dispatch(self, request, *args, **kwargs):
        tweet=self.tweet
        if request.user.id != tweet.user.id:
            messages.error(request,'شما اجازه اپدیت این توییت را ندارید','danger')
            return redirect('book:tweet')
        return super().dispatch(request,*args,**kwargs)
    def get(self,request,tweet_id):
        tweet=self.tweet
        images=self.images
        # گرفتن نام تگ‌ها از queryset
        tags_names = list(tweet.tags.values_list('name', flat=True))

        # تبدیل نام تگ‌ها به یک رشته جدا شده با ویرگول
        tags_string = ', '.join(tags_names)
        form=self.form_class(instance=tweet,initial={'tags':tags_string})

        return render(request,self.template_name,{'form':form,'images':images,'tweet':tweet})

    def post(self,request,tweet_id):
        tweet=self.tweet
        images=self.images
        form=self.form_class(request.POST,request.FILES,instance=tweet)
        if form.is_valid():
            new_tweet=form.save(commit=False)
            cd=form.cleaned_data
            language=detect(cd['body'])
            if language=='fa':
                translator=Translator()
                translated_text=translator.translate(cd['body'],src='fa',dest='en')
                text=translated_text.text
                new_tweet.slug=slugify(text[:30])
            else:
                new_tweet.slug=slugify(cd['body'][:30])

            # for tag in tweet.tags.all():
            #     tag.clear()
            tweet.tags.clear()

            tags=cd['tags']
            if tags:
                tags_list = tags.split(',')
                for tag in tags_list:
                    tag = tag.replace(" ", "")
                    new_tweet.tags.add(tag)

            new_tweet.save()

            num_image=cd['num_image']
            if num_image:
                image_id=[]
                for num in num_image:
                    if num != ',':
                        image=images[int(num)-1]
                        image_id.append(image.id)
                for id in image_id:
                    image_delete= UploadedImageTweet.objects.filter(id=id)
                    image_delete.delete()


            if len(request.POST.getlist('all_image'))>0:
                for image in images:
                    image.delete()


            for uploaded_file in request.FILES.getlist('files'):
                UploadedImageTweet.objects.create(file=uploaded_file,tweet=tweet )

            return redirect('book:tweet_detail',tweet.slug, tweet.id)
        return render(request,self.template_name,{'form':form,'images':images,'tweet':tweet})


class BlockUserView(LoginRequiredMixin, View):
    def get(self,request,user_id):
        user = User.objects.get(id=user_id)
        if Block.objects.filter(from_user=request.user,to_user=user).exists():
            # messages.error(request,'شما این کاربر را قبلا مسدود کرده اید.','info')
            # return redirect('book:tweet')
            Block.objects.filter(from_user=request.user, to_user=user).delete()
            return JsonResponse({'response': 'unblock'})
        else:
            Block.objects.create(from_user=request.user,to_user=user)
            if Relation.objects.filter(from_user=request.user,to_user=user).exists():
                Relation.objects.filter(from_user=request.user, to_user=user).delete()
            if Relation.objects.filter(from_user=user, to_user=request.user).exists():
                Relation.objects.filter(from_user=user, to_user=request.user).delete()

            referer = request.META.get('HTTP_REFERER')
            # اگر از صفحه جزئیات آمده باشد
            if 'tweet_detail' in referer:
                messages.success(request,'شما کاربر را مسدود کرده اید.','success')
                return redirect('book:tweet')
            # اگر از صفحه پروفایل آمده باشد
            return redirect(referer)


class ReportView(LoginRequiredMixin, View):
    template_name = 'book/children/report.html'
    form_class=ReportForm
    def get(self,request,user_id,tweet_id='none'):
        form = self.form_class()
        return render(request,self.template_name,{'form':form})
    def post(self,request,user_id,tweet_id='none'):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            to_user=User.objects.get(id=user_id)
            if tweet_id !='none':
                tweet=Tweet.objects.get(id=tweet_id)
                report=Report.objects.create(to_user=to_user,tweet=tweet,from_user=request.user)
                report.body = cd['body']
                report.save()
                return redirect('book:tweet_detail', tweet.slug, tweet.id)
            else:
                report = Report.objects.create(to_user=to_user, from_user=request.user)
                report.body=cd['body']
                report.save()
                return redirect('book:user_profile', to_user.id)
        return render(request,self.template_name,{'form':form})






@login_required
def Chat(request):
    frnd_name = request.GET.get('user',None)
    mychats_data = None
    if frnd_name:
        if User.objects.filter(username=frnd_name).exists() and Mychats.objects.filter(me=request.user,frnd=User.objects.get(username=frnd_name)).exists():
            frnd_ = User.objects.get(username=frnd_name)
            mychats_data = Mychats.objects.get(me=request.user,frnd=frnd_).chats

    # frnds = User.objects.exclude(pk=request.user.id)

    frnds_follower=Relation.objects.filter(from_user=request.user)
    frnds_folower_id=[frnd.to_user.id for frnd in frnds_follower]
    frnds_chat=Mychats.objects.filter(frnd=request.user)
    frnds_chat_id=[frnd.me.id for frnd in frnds_chat]
    frnds_id=frnds_folower_id+frnds_chat_id
    frnds=User.objects.filter(id__in=frnds_id)


    profiles=Profile.objects.all()

    return render(request,'book/children/chat.html',{'chats': mychats_data,'frnds':frnds,'profiles':profiles})


class ShareTweetChatView(LoginRequiredMixin, View):
    def get(self,request,to_user,book_id=None,tweet_id=None):
        if tweet_id is not None:
            tweet=Tweet.objects.get(id=tweet_id)
            url = request.build_absolute_uri(tweet.get_absolute_url())
        if book_id is not None:
            book = SaleBook.objects.get(id=book_id)
            url = request.build_absolute_uri(book.get_absolute_url())

        frnd = User.objects.get(id=to_user)
        mychats, created = Mychats.objects.get_or_create(me=request.user, frnd=frnd)
        # If the object was just created, initialize the 'chats' field as an empty dictionary
        if created:
            mychats.chats = {}
        mychats.chats[str(datetime.datetime.now()) + "1"] = {'user': 'me', 'msg': url}
        mychats.save()
        mychats, created = Mychats.objects.get_or_create(me=frnd, frnd=request.user)
        # If the object was just created, initialize the 'chats' field as an empty dictionary
        if created:
            mychats.chats = {}
        mychats.chats[str(datetime.datetime.now()) + "2"] = {'user': frnd.username, 'msg': url}
        mychats.save()

        return JsonResponse()

class CommentLikeView(LoginRequiredMixin, View):
    def get(self, request,value,comment_id=None,commentbook_id=None):
        if commentbook_id is not None:

            comment = BookComment.objects.get(id=commentbook_id)
            if value=='like':
                if BookCommentLike.objects.filter(user=request.user, comment=comment).exists():
                    BookCommentLike.objects.filter(user=request.user, comment=comment).delete()
                    return JsonResponse({'response': 'unliked'})
                else:
                    if BookCommentDisLike.objects.filter(user=request.user, comment=comment).exists():
                        BookCommentDisLike.objects.filter(user=request.user, comment=comment).delete()
                        BookCommentLike.objects.create(user=request.user, comment=comment)
                        return JsonResponse({'response': 'liked_delete dislike'})
                    else:
                        BookCommentLike.objects.create(user=request.user, comment=comment)
                        return JsonResponse({'response': 'liked'})



            if value == 'dislike':
                if BookCommentDisLike.objects.filter(user=request.user, comment=comment).exists():
                    BookCommentDisLike.objects.filter(user=request.user, comment=comment).delete()
                    return JsonResponse({'response': 'undislike'})
                else:
                    if BookCommentLike.objects.filter(user=request.user, comment=comment).exists():

                        BookCommentLike.objects.filter(user=request.user, comment=comment).delete()

                        BookCommentDisLike.objects.create(user=request.user, comment=comment)
                        return JsonResponse({'response': 'dislike_delete like'})
                    else:
                        BookCommentDisLike.objects.create(user=request.user, comment=comment)
                        return JsonResponse({'response': 'dislike'})

        if comment_id is not None:
            comment = Comment.objects.get(id=comment_id)
            if value == 'like':
                if TweetCommentLike.objects.filter(user=request.user, comment=comment).exists():
                    TweetCommentLike.objects.filter(user=request.user, comment=comment).delete()
                    return JsonResponse({'response': 'unliked'})
                else:
                    if TweetCommentDisLike.objects.filter(user=request.user, comment=comment).exists():
                        TweetCommentDisLike.objects.filter(user=request.user, comment=comment).delete()
                        TweetCommentLike.objects.create(user=request.user, comment=comment)
                        return JsonResponse({'response': 'liked_delete dislike'})
                    else:
                        TweetCommentLike.objects.create(user=request.user, comment=comment)
                        return JsonResponse({'response': 'liked'})

            if value == 'dislike':
                if TweetCommentDisLike.objects.filter(user=request.user, comment=comment).exists():
                    TweetCommentDisLike.objects.filter(user=request.user, comment=comment).delete()
                    return JsonResponse({'response': 'undislike'})
                else:
                    if TweetCommentLike.objects.filter(user=request.user, comment=comment).exists():

                        TweetCommentLike.objects.filter(user=request.user, comment=comment).delete()

                        TweetCommentDisLike.objects.create(user=request.user, comment=comment)
                        return JsonResponse({'response': 'dislike_delete like'})
                    else:
                        TweetCommentDisLike.objects.create(user=request.user, comment=comment)
                        return JsonResponse({'response': 'dislike'})






class CloseNotificationView(LoginRequiredMixin, View):
    def get(self, request,from_user=None,user_salebook=None,book_id=None,cancel_factor_id=None,conformation_factor_id=None):

        if from_user is not None:
            user=User.objects.get(id=from_user)
            relation=Relation.objects.get(from_user=user,to_user=request.user)
            relation.show=True
            relation.save()
        if user_salebook is not None:
            user_book=User.objects.get(id=user_salebook)
            book=SaleBook.objects.get(id=book_id)
            DontShowNotificationRegistrationRequestedBook.objects.create(user_salebook=user_book,user_requested_book=request.user,book=book)
        if cancel_factor_id is not None:
            print('yes1')
            factor=Factor.objects.get(id=cancel_factor_id)
            Cart.objects.get(user=factor.buyer , book=factor.book).delete()
            factor.delete()
            print('yes')
        if conformation_factor_id is not None :
            factor = Factor.objects.get(id=conformation_factor_id)
            print(factor)
            factor.status=True
            factor.save()
        return JsonResponse()



class NotificationView(LoginRequiredMixin, View):
    template_name = 'book/children/notification.html'
    def get(self, request):
        relations_notification=Relation.objects.filter(to_user=request.user,show=False).order_by('-created_at')
        profiles=Profile.objects.all()
        rbooks=RegistrationRequestedBook.objects.filter(user=request.user,status=False)
        salebooks=SaleBook.objects.filter(status=False)
        books_id=[]
        for rbook in rbooks:
            if SaleBook.objects.filter(author=rbook.author,name_book=rbook.name_book,status=False,category=rbook.category).exists():
                book=SaleBook.objects.get(author=rbook.author,name_book=rbook.name_book,category=rbook.category,status=False)

                if not DontShowNotificationRegistrationRequestedBook.objects.filter(user_requested_book=rbook.user, user_salebook=book.user).exists():

                    books_id.append(book.id)
        factors=Factor.objects.filter(status=False,Seller=request.user)
        count=len(books_id)+ relations_notification.count()+factors.count()

        context={'relations_notification':relations_notification,
                 'profiles':profiles,
                 'books_id':books_id,
                 'salebooks':salebooks,
                 'count':count,
                 'factors':factors}

        return render(request,self.template_name,context)



# --------------------------------------------------store------------------------------------------------------
class HomePageView(View):
    def get(self, request):

        return render(request, 'book/child-store/home.html')



class SaleBookView(LoginRequiredMixin, View):
    templates='book/child-store/salebook.html'
    form_class=SaleBookForm
    def get(self,request):
        form = self.form_class()
        return render(request, self.templates,{'form':form})
    def post(self,request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            new_salebook=SaleBook.objects.create(user=request.user)
            cd=form.cleaned_data
            new_salebook.name_book=cd['name_book']
            new_salebook.price=cd['price']

            new_salebook.author=cd['author']
            new_salebook.print_year=cd['print_year']
            new_salebook.period_print=cd['period_print']
            new_salebook.number_of_page=cd['number_of_page']
            new_salebook.book_introduction=cd['book_introduction']
            new_salebook.photo=cd['photo']
            new_salebook.category = cd['category']
            new_salebook.save()


            return redirect('book:home')
        else:
            return render(request, self.templates, {'form':form})



class CategoryView(LoginRequiredMixin,View):
    template_name='book/child-store/category.html'

    def setup(self, request, *args, **kwargs):
        self.categorys=SaleBook.objects.values('category').distinct()
        self.profiles = Profile.objects.all()
        query_name = request.POST.get('search_input')
        self.count=3

        if query_name:
            request.session['search_input'] =query_name



        return super().setup(request, *args, **kwargs)


    def get(self, request,category_name,sort_by=0,query_name=''):
        context={}


        if query_name !='':
            query_name = request.session.get('search_input')
            buy_books = SaleBook.objects.annotate(search=SearchVector('name_book','author','user__username')).filter(
                search=query_name, status=False, category=category_name).order_by('-created_at')
            context.update({'query_name':query_name})
        else:

            buy_books = SaleBook.objects.filter(category=category_name, status=False).order_by('-created_at')
        book_votes_user_list=[]
        for book in buy_books:
            if BookVote.objects.filter(book=book,user=request.user).exists():
                book_votes_user_list.append(book.id)

        if sort_by==0:
            buy_books=buy_books.order_by('-created_at')
            sort='جدید ترین'
        if sort_by==1:
            buy_books = buy_books.order_by(
                Cast('price', output_field=IntegerField()))
            sort='ارزانترین'
        if sort_by==2:
            buy_books = buy_books.order_by(
                Cast('price', output_field=IntegerField()))
            buy_books=buy_books.reverse()

            sort='گرانترین'
        if sort_by==3:
            sort="امتیاز"
            buy_books = buy_books.annotate(
                total_votes=Count('bvote')).order_by('-total_votes')


        context.update({'buy_books':buy_books,
                 'category_name':category_name,
                 'profiles':self.profiles,
                 'sort':sort,
                 'categorys':self.categorys,
                 'book_votes_user_list':book_votes_user_list,
                'count':self.count
                 })

        return render(request, self.template_name,context )
    def post(self,request,category_name,sort_by=0,query_name=''):

        query_name = request.session.get('search_input')
        buy_books = SaleBook.objects.annotate(search=SearchVector('name_book','author','user__username')).filter(
            search=query_name,status=False,category=category_name).order_by('-created_at')

        book_votes_user_list = []
        for book in buy_books:
            if BookVote.objects.filter(book=book, user=request.user).exists():
                book_votes_user_list.append(book.id)

        context = {
                   'category_name': category_name,
                   'profiles': self.profiles,
                   'buy_books':buy_books,
                    'query_name':query_name,
                    'categorys':self.categorys,
                    'book_votes_user_list': book_votes_user_list,
            'count': self.count
        }

        return render(request, self.template_name, context)


class BookLikeView(LoginRequiredMixin, View):
    def get(self, request,book_id):
        book = SaleBook.objects.get(id=book_id)
        if BookVote.objects.filter(user=request.user, book=book).exists():
            BookVote.objects.filter(user=request.user, book=book).delete()
            return JsonResponse({'response': 'unliked'})
            # referer = request.META.get('HTTP_REFERER')
            # return redirect(referer)
        else:
            BookVote.objects.create(user=request.user, book=book)
            return JsonResponse({'response': 'liked'})
            # referer = request.META.get('HTTP_REFERER')
            # return redirect(referer)


class DetailSaleBookView(LoginRequiredMixin,View):
    template_name='book/child-store/detail_salebook.html'
    form_class = BookCommentCreateForm
    def setup(self, request, *args, **kwargs):
        self.book = SaleBook.objects.get(id=kwargs['book_id'])
        self.like_count = BookVote.objects.filter(book=self.book).count()
        self.user_liked_book = False
        if BookVote.objects.filter(book=self.book, user=request.user).exists():
            self.user_liked_book = True
        self.comments = BookComment.objects.filter(book=self.book)
        # shre tweet with chat
        frnds_follower = Relation.objects.filter(from_user=request.user)
        frnds_folower_id = [frnd.to_user.id for frnd in frnds_follower]
        frnds_chat = Mychats.objects.filter(frnd=request.user)
        frnds_chat_id = [frnd.me.id for frnd in frnds_chat]
        frnds_id = frnds_folower_id + frnds_chat_id
        self.frnds = User.objects.filter(id__in=frnds_id)
        self.profiles = Profile.objects.all()
        self.blocked_user_ids=[]

        commnet_like_request_user = BookCommentLike.objects.filter(user=request.user)
        commnet_dislike_request_user = BookCommentDisLike.objects.filter(user=request.user)

        self.commnet_like_request_user_id = [comment.comment.id for comment in commnet_like_request_user]
        self.commnet_dislike_request_user_id = [comment.comment.id for comment in commnet_dislike_request_user]



        similar_books_1 = SaleBook.objects.filter(category=self.book.category , author=self.book.author)
        similar_books_2 = SaleBook.objects.filter(name_book__in=self.book.name_book)
        similar_books_4=SaleBook.objects.filter(author=self.book.author)
        similar_books_3=SaleBook.objects.filter(category=self.book.category)

        combined_books = list(similar_books_1) + list(similar_books_2) + list(similar_books_3) + list(similar_books_4)

        # حذف تکرارها
        self.unique_books = list(set(combined_books))
        if len(self.unique_books) > 10:
            self.unique_books = self.unique_books[:10]


        return super().setup(request, *args, **kwargs)
    def get(self,request,book_id):
        book=self.book
        form = self.form_class()
        context= {'book':book,
                  'like_count':self.like_count,
                  'user_liked_book':self.user_liked_book
                  ,'frnds':self.frnds,'profiles':self.profiles,
                  'comments':self.comments,
                  'form':form,
                  'blocked_user_ids':self.blocked_user_ids,
                  'commnet_like_request_user_id':self.commnet_like_request_user_id,
                  'unique_books':self.unique_books,
                  'commnet_dislike_request_user_id':self.commnet_dislike_request_user_id,
                 }

        return render(request,self.template_name,context)

    def post(self,request,book_id):

        form = self.form_class(request.POST)
        if form.is_valid():

            new_comment = form.save(commit=False)

            new_comment.user = request.user
            new_comment.book = self.book

            new_comment.save()
            return redirect('book:detail_salebook',self.book.id)

        context = {'book': self.book,
                   'like_count': self.like_count,
                   'user_liked_book': self.user_liked_book
                   , 'frnds': self.frnds, 'profiles': self.profiles,
                   'comments': self.comments,
                   'form': form,
                   'blocked_user_ids': self.blocked_user_ids,
                   'commnet_like_request_user_id': self.commnet_like_request_user_id,
                   'unique_books': self.unique_books,
                   'commnet_dislike_request_user_id': self.commnet_dislike_request_user_id,

                   }

        return render(request, self.template_name, context)

class SearchBookView(LoginRequiredMixin,View):
    templates = 'book/child-store/serch_book.html'

    def setup(self, request, *args, **kwargs):
        self.profiles = Profile.objects.all()
        query_name = request.POST.get('search_input')

        if query_name:
            self.search=query_name
            request.session['search_input'] =query_name
        else:
            self.search = request.session.get('search_input')


        self.buy_books = SaleBook.objects.annotate(search=SearchVector
        ('name_book', 'author','user__username')).filter(
            search=self.search, status=False).order_by('-created_at')

        self.book_votes_user_list = []
        for book in self.buy_books:
            if BookVote.objects.filter(book=book, user=request.user).exists():
                self.book_votes_user_list.append(book.id)

        return super().setup(request, *args, **kwargs)
    def get(self, request, sort_by=0):
        if sort_by==0:
            buy_books=self.buy_books.order_by('-created_at')
            sort='جدید ترین'
        if sort_by==1:
            buy_books = self.buy_books.order_by(
                Cast('price', output_field=IntegerField()))
            sort='ارزانترین'
        if sort_by==2:
            buy_books = self.buy_books.order_by(
                Cast('price', output_field=IntegerField()))
            buy_books=buy_books.reverse()

            sort='گرانترین'
        if sort_by==3:
            sort="امتیاز"
            buy_books = self.buy_books.annotate(
                total_votes=Count('bvote')).order_by('-total_votes')
        context={'buy_books': buy_books,
                 'sort':sort,
                 'profiles':self.profiles
                 ,'book_votes_user_list':self.book_votes_user_list
                 ,'search':self.search}
        return render(request,self.templates,context )

    def post(self, request,sort_by=0):
        context = {'buy_books': self.buy_books,
                   'profiles': self.profiles
                   ,'book_votes_user_list':self.book_votes_user_list
                   ,'search':self.search}
        return render(request, self.templates, context)

class DeleteBookView(LoginRequiredMixin,View):
    def get(self,request,book_id):


        book=SaleBook.objects.get(id=book_id)
        if request.user.id != book.user.id:
            messages.error(request, "شما اجازه حذف این کتاب را ندارید", 'danger')

            referer = request.META.get('HTTP_REFERER')
            return redirect(referer)

        else:
            book.delete()
            messages.success(request, "کتاب حذف شد", 'success')

            return redirect('book:home')

class UpdateBookView(LoginRequiredMixin,View):
    form_class = UpdateBookForm
    template_name = 'book/child-store/update_book.html'

    def setup(self, request, *args, **kwargs):

        self.book = SaleBook.objects.get(id=kwargs['book_id'])
        self.image=self.book.photo
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        book = self.book
        if request.user.id != book.user.id:
            messages.error(request, 'شما اجازه اپدیت این کتاب را ندارید', 'danger')
            return redirect('book:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self,request,book_id):

       form=self.form_class(instance=self.book)
       return render(request, self.template_name,{'form':form,'image':self.image,'id':self.book.id})

    def post(self,request,book_id):
        form = self.form_class(request.POST, request.FILES, instance=self.book)
        if form.is_valid():
            form.save()
            return redirect('book:detail_salebook',self.book.id)

        else:

            return render(request, self.template_name, {'form': form,'image':self.image,'id':self.book.id})


class WeblogView(LoginRequiredMixin,View):
    def get(self, request,name_weblog):
       if name_weblog=='children_book':
           return render(request,'book/weblog/childern_book.html')
       if name_weblog=='habit_reading_book':
           return render(request,'book/weblog/habit_reading_book.html')
       if name_weblog=='take_breath_away':
           return render(request,'book/weblog/take_breath_away.html')
       if name_weblog == 'why_read_book':
           return render(request, 'book/weblog/why_read_book.html')


class RecommendedBookUserView(LoginRequiredMixin,View):
    template_name='book/child-store/recommended_book_user.html'
    form_class=RecommendedBookUserForm

    def get(self,request):
        form=self.form_class()

        return render(request,self.template_name,{'form':form})
    def post(self,request):
        form=self.form_class(request.POST, request.FILES)
        if form.is_valid():
            cd=form.cleaned_data
            new_recommended_book=RecommendedBookUser.objects.create(user=request.user)
            new_recommended_book.author=cd['author']
            new_recommended_book.photo=cd['photo']
            new_recommended_book.book_name=cd['book_name']
            new_recommended_book.body=cd['body']
            new_recommended_book.save()
            return redirect('book:user_profile',request.user.id)
        return render(request,self.template_name,{'form':form})

class DetailRecommendedBookUserView(LoginRequiredMixin,View):
    template_name='book/child-store/detail_recommended_book_user.html'
    def get(self,request,book_id):

        recommended_book=RecommendedBookUser.objects.get(id=book_id)

        if SaleBook.objects.filter(author=recommended_book.author , name_book=recommended_book.book_name,status=False,user=recommended_book.user).exists():
            book=SaleBook.objects.get(author=recommended_book.author , name_book=recommended_book.book_name,status=False,user=recommended_book.user)
            return render(request, self.template_name, {'recommended_book': recommended_book, 'book': book})

        elif SaleBook.objects.filter(author=recommended_book.author , name_book=recommended_book.book_name,status=False).exists():
            book=SaleBook.objects.get(author=recommended_book.author , name_book=recommended_book.book_name,status=False)
            return render(request, self.template_name, {'recommended_book': recommended_book, 'book': book})

        else:

            return render(request,self.template_name,{'recommended_book':recommended_book})

class DeleteRecommendedBookUserView(LoginRequiredMixin,View):
    def get(self,request,book_id):
        recommended_book=RecommendedBookUser.objects.get(id=book_id)
        if request.user.id == recommended_book.user.id:
            recommended_book.delete()
            return redirect('book:user_profile_nav', request.user.id ,4)
        else:
            messages.error(request,'شما مجاز به حذف این کتاب نیستید','danger')
            return redirect('book:home')

class UpdateRecommendedBookUserView(LoginRequiredMixin,View):
    template_name='book/child-store/update_recommendedbookuser.html'
    form_class=UpdateRecommendedBookUserForm
    def setup(self,request,*args,**kwargs):
        self.book=RecommendedBookUser.objects.get(id=kwargs['book_id'])
        return super().setup(request, *args, **kwargs)
    def get(self,request,book_id):
        form=self.form_class(instance=self.book)
        return render(request,self.template_name,{'form':form,'book':self.book})
    def post(self,request,book_id):
        form=self.form_class(request.POST, request.FILES,instance=self.book)
        if form.is_valid():

            update_recommendedbook=form.save(commit=False)
            update_recommendedbook.user=request.user
            update_recommendedbook.save()
            return redirect('book:detail_recommendedbookuser',self.book.id)

        return render(request, self.template_name, {'form': form,'book':self.book})

class RegistrationRequestedBookView(LoginRequiredMixin,View):
    template_name='book/child-store/registration_requested_book.html'
    form_class = RegistrationRequestedBookForm

    def get(self,request):
        form=self.form_class()
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form=self.form_class(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            book=RegistrationRequestedBook.objects.create(user=request.user)
            book.name_book=cd['name_book']
            book.author=cd['author']
            book.print_year=cd['print_year']
            book.category=cd['category']
            book.Description=cd['Description']
            book.save()

            return redirect('book:home')
        else:
            return render(request, self.template_name, {'form': form})


class ShowRequestedBookView(LoginRequiredMixin,View):
    template_name='book/child-store/show_requested_book.html'
    def get(self,request):
        requested_books=RegistrationRequestedBook.objects.filter(status=False).order_by('-created_at')
        return render(request,self.template_name,{"requested_books":requested_books})
    def post(self,request):
        query_name = request.POST.get('search_input')
        requested_books=RegistrationRequestedBook.objects.annotate(search=SearchVector('name_book')).filter(search=query_name , status=False).order_by('-created_at')
        return render(request, self.template_name, {"requested_books": requested_books})

class DetailRequestedBookView(LoginRequiredMixin,View):
    def get(self, request,book_id):
        book=RegistrationRequestedBook.objects.get(id=book_id)
        return  render(request,'book/child-store/detail_requested_book.html',{'book':book})

class DeleteRequestedBookView(LoginRequiredMixin,View):
    def get(self,request,book_id):
        requested_book=RegistrationRequestedBook.objects.get(id=book_id)
        if request.user.id == requested_book.user.id:
            requested_book.delete()
            return redirect('book:show_requested_book')
        else:
            messages.error(request,'شما مجاز به حذف این آگهی نیستید','danger')
            return redirect('book:home')

class UpdateRequestedBookView(LoginRequiredMixin,View):
    template_name = 'book/child-store/update_requested_book.html'
    form_class = UpdateRequestedBookForm

    def setup(self, request, *args, **kwargs):
        self.book = RegistrationRequestedBook.objects.get(id=kwargs['book_id'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, book_id):
        form = self.form_class(instance=self.book)
        return render(request, self.template_name, {'form': form,'book':self.book})

    def post(self, request, book_id):
        form = self.form_class(request.POST, instance=self.book)
        if form.is_valid():
            update_requestedbook = form.save(commit=False)
            update_requestedbook.user = request.user
            update_requestedbook.save()
            return redirect('book:detail_requested_book', self.book.id)

        return render(request, self.template_name, {'form': form,'book':self.book})


from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

@require_POST
def add_to_cart(request):
    if request.user.is_authenticated:
        book_id = request.POST.get('book_id')
        book = get_object_or_404(SaleBook, id=book_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, book=book)
        msg=f' کتاب {cart_item.book.name_book} به سبد خرید شما اضافه شد '
        if not created:
            msg=f' کتاب {cart_item.book.name_book} از سبد خرید شما حذف شد '
            cart_item.delete()

        cart_count = Cart.objects.filter(user=request.user).count()
        return JsonResponse({'cart_count': cart_count,'msg':msg})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=403)



class ShowDetailCartView(LoginRequiredMixin,View):
    template_name = 'book/child-store/detail_cart.html'
    def get(self, request):
        books=Cart.objects.filter(user=request.user).order_by('-created_at')
        factor_books=Factor.objects.filter(status=False,buyer=request.user)
        factor_books_id=[]
        for factor_book in factor_books:
            factor_books_id.append(factor_book.book.id)
        conform_factor=Factor.objects.filter(status=True,buyer=request.user)
        factor_confirm_id = []
        for factor in conform_factor:
            factor_confirm_id.append(factor.book.id)

        return render(request,self.template_name,{'books':books,'factor_books_id':factor_books_id,'factor_confirm_id':factor_confirm_id})

class DeleteItemCartView(LoginRequiredMixin,View):
    def get(self,request,book_id):
        book=Cart.objects.get(id=book_id)
        if book.user != request.user:
            messages.error(request, "شما اجازه دسترسی ندارید", 'danger')
            return redirect('book:home')
        else:
            if Factor.objects.filter(buyer=book.user,book=book.book).exists():
                Factor.objects.filter(buyer=book.user, book=book.book).delete()

            book.delete()
            cart_count = Cart.objects.filter(user=request.user).count()

            return JsonResponse({'cart_count': cart_count})


class FactorView(LoginRequiredMixin,View):
    def get(self,request,id_seller,cart_id):
        book=Cart.objects.get(id=cart_id).book
        seller=User.objects.get(id=id_seller)
        if Factor.objects.filter(book=book,buyer=request.user,Seller=seller).exists():
            Factor.objects.filter(book=book, buyer=request.user, Seller=seller).delete()
            # referer = request.META.get('HTTP_REFERER')
            # return redirect(referer)
            return JsonResponse({'response': 'delete'})

        Factor.objects.create(book=book,buyer=request.user,Seller=seller)
        # referer = request.META.get('HTTP_REFERER')
        # return redirect(referer)
        return JsonResponse({'response': 'create'})

class BuyingSellingGuideView(LoginRequiredMixin,View):
    template_name='book/child-store/buying_selling_guide.html'
    def get(self,request):
        return render(request,self.template_name)

import re

class GiveAddressUserView(LoginRequiredMixin,View):
    template_name='book/child-store/give_address.html'
    def setup(self, request, *args, **kwargs):
        self.location=Profile.objects.get(user=request.user).Location
        return super().setup(request, *args, **kwargs)

    def get(self,request):
        return render(request,self.template_name,{'location':self.location})
    def post(self,request):
        new_location = request.POST.get('location')
        pattern = r'^[^_]+_[^_]+_[^_]+_[^_]+_[0-9]{10}$'  # Adjust regex pattern as needed

        if re.match(pattern, new_location):
            profile = Profile.objects.get(user=request.user)
            profile.Location = new_location
            profile.save()
            return render(request, self.template_name, {'location': new_location})
        else:
            error_message = "آدرس باید به صورت استان_شهر_خیابان_کوچه_کدپستی وارد شود و کدپستی باید ۱۰ رقمی باشد."
            return render(request, self.template_name, {'location': self.location, 'error': error_message})

