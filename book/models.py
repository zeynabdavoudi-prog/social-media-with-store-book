from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return f'{self.user.username}-{self.id}'

    def get_absolute_url(self):
        return reverse('book:tweet_detail',args=[self.slug,self.id])

class UploadedImageTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='imagetweet/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.tweet.id)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='profile/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    background_image_profile=models.ImageField(upload_to='background_image_profile/', null=True, blank=True)
    Location=models.CharField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}'

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='uvote')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE,related_name='tvote')

    def __str__(self):
        return f'{self.user} - {self.tweet.slug}'

class Comment(MPTTModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='ucomments')
    tweet= models.ForeignKey(Tweet, on_delete=models.CASCADE,related_name='comments')
    parent = TreeForeignKey('self', on_delete=models.CASCADE,null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField(max_length=500)


    class MPTTMeta:
        order_insertion_by = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.body[:30]}'

class TweetCommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='utclvote')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='ctclvote')

    def __str__(self):
        return f'{self.user} - {self.comment.body[:20]}'

class TweetCommentDisLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='utcdlvote')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='ctcdlvote')

    def __str__(self):
        return f'{self.user} - {self.comment.body[:20]}'
class Relation(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='followers')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='following')
    created_at = models.DateTimeField(auto_now_add=True)
    show=models.BooleanField(default=False)
    def __str__(self):
        return f'{self.from_user} following {self.to_user}'

class Block(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fblock')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tblock')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.from_user} block {self.to_user}'

class Report(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='freport')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='treport')
    created_at = models.DateTimeField(auto_now_add=True)
    tweet= models.ForeignKey(Tweet, on_delete=models.CASCADE,related_name='rtweet', null=True ,blank=True)
    body = models.TextField()
    def __str__(self):
        return f'{self.from_user} report {self.to_user}'

class Mychats(models.Model):
    me = models.ForeignKey(to=User,on_delete=models.CASCADE,related_name='it_me')
    frnd = models.ForeignKey(to=User,on_delete=models.CASCADE,related_name='my_frnd')
    chats = models.JSONField(default=dict)

# store book
class SaleBook(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='usbook')
    name_book=models.CharField()
    price=models.CharField()
    author=models.CharField()
    print_year=models.CharField(max_length=4)
    period_print=models.CharField()
    number_of_page=models.CharField()
    photo=models.ImageField(upload_to='photosalebook/')
    category=models.CharField()
    book_introduction=models.TextField()
    status=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name_book} از دسته بندی {self.category}'

    def get_absolute_url(self):
        return reverse('book:detail_salebook',args=[self.id])

class BookVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='ubvote')
    book = models.ForeignKey(SaleBook, on_delete=models.CASCADE,related_name='bvote')

    def __str__(self):
        return f'{self.user} - {self.book.name_book}'

class BookComment(MPTTModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='ubcomments')
    book= models.ForeignKey(SaleBook, on_delete=models.CASCADE,related_name='bcomments')
    parent = TreeForeignKey('self', on_delete=models.CASCADE,null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField(max_length=500)

class BookCommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ubclvote')
    comment = models.ForeignKey(BookComment, on_delete=models.CASCADE, related_name='cbclvote')

    def __str__(self):
        return f'{self.user} - {self.comment.body[:20]}'

class BookCommentDisLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ubcdvote')
    comment = models.ForeignKey(BookComment, on_delete=models.CASCADE, related_name='cbcdvote')

    def __str__(self):
        return f'{self.user} - {self.comment.body[:20]}'

class RecommendedBookUser(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    photo=models.ImageField(upload_to='recommendenbookuser/',blank=True,null=True)
    author=models.CharField()
    book_name=models.CharField()
    body=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.user} - {self.body[:20]}'



# store book
class RegistrationRequestedBook(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='ubook')
    name_book=models.CharField()
    author=models.CharField()
    print_year=models.CharField(max_length=4,null=True,blank=True)
    category=models.CharField()
    Description=models.TextField()
    status=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.name_book} از دسته بندی {self.category}'

class DontShowNotificationRegistrationRequestedBook(models.Model):
    user_requested_book=models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_requested_book')
    user_salebook=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_salebook")
    book=models.ForeignKey(SaleBook,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user_requested_book.username} کتاب {self.book.name_book}از {self.user_salebook.username}را دید.'


class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE ,related_name='cart_user')
    book=models.ForeignKey(SaleBook,on_delete=models.CASCADE,related_name='cart_book')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} کتاب {self.book.name_book} را به سبد خرید خود اضافه کرد'



class Factor(models.Model):
    buyer=models.ForeignKey(User,on_delete=models.CASCADE ,related_name='buyer_user')
    Seller=models.ForeignKey(User,on_delete=models.CASCADE ,related_name='Seller_user')
    book=models.ForeignKey(SaleBook,on_delete=models.CASCADE,related_name='factor_book')
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.BooleanField(default=False)

    def __str__(self):
        return f'ارسال فاکتور از {self.buyer.username} به {self.Seller.username} برای کتاب {self.book.name_book} '

