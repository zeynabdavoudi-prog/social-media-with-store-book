from django import forms
from captcha.fields import CaptchaField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from mptt.forms import TreeNodeChoiceField

from book.models import *


class UserLoginForm(forms.Form):
    username_email = forms.CharField()
    password = forms.CharField()
    captcha = CaptchaField()
class UserRegisterForm(forms.Form):
    username = forms.CharField(label="نام کاربری")
    email = forms.EmailField(label="ایمیل")
    password = forms.CharField(widget=forms.PasswordInput(),label="رمز عبور")
    password2 = forms.CharField(widget=forms.PasswordInput(),label="تکرار رمز عبور")

    def clean_email(self):
        email = self.cleaned_data['email']
        user= User.objects.filter(email=email).exists()
        if user :
            raise ValidationError('این ایمیل از قبل وحود دارد ')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        user= User.objects.filter(username=username).exists()
        if user:
            raise ValidationError("این نام کاربری از قبل وجود دارد")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        password_alpha=0
        for pw in password:
            if pw.isalpha():
                password_alpha=1
        if password_alpha ==  0 or len(password) < 8:
            raise ValidationError("رمز عبور شما باید حداقل شامل 8 کاراکتر باشد و تماما عددی نباشد ")
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValidationError("رمز عبور  ها یکسان نیستند")
        return password2

# tweet
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
class UploadTweet(forms.Form):
    files = MultipleFileField(required=False)
    body = forms.CharField()
    tags = forms.CharField(required=False)


class EditProfileForm(forms.ModelForm):
    first_name=forms.CharField(required=False,label="نام ",widget=forms.TextInput(attrs={"class":" form-control"}))
    last_name=forms.CharField(required=False,label="نام خانوادگی:",widget=forms.TextInput(attrs={"class":" form-control"}) )
    class Meta:
        model = Profile
        fields = ['background_image_profile', 'file','bio','date_of_birth','Location']
        widgets = {
            'bio': forms.Textarea(attrs={'required': False,'class':' form-control','cols': 3, 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'required': False,'class':' form-control','placeholder': 'لطفا تاریخ را به صورت yyyy-mm-ddوارد کنید','pattern': '\\d{4}-\\d{1,2}-\\d{1,2}', 'oninvalid': 'this.setCustomValidity("تاریخ موردنظر اشتباه است. لطفاً یک تاریخ معتبر به فرمت yyyy-mm-dd وارد کنید.")', 'oninput': 'setCustomValidity("")' }),
            'Location': forms.DateInput(attrs={'required': True,'class':' form-control', 'oninvalid': 'this.setCustomValidity("لطفا فیلد مکان را پر کنید")','oninput': 'setCustomValidity("")'}),
        }
        labels={'background_image_profile':'عکس نمایه','file':'عکس پروفایل',
                'date_of_birth':'تاریخ تولد','bio':"بیوگرافی",'Location':'مکان'}



class ShareTweetForm(forms.Form):
    message=forms.CharField(label='متن ایمیل ')
    to=forms.EmailField(label='ایمیل')

class ContactUsForm(forms.Form):
    message=forms.CharField(label='توضیحات')
    email=forms.EmailField(label='ایمیل ')
    subject=forms.CharField(label='عنوان')
    phone=forms.CharField(label='شماره تلفن',max_length=11,required=False)
    full_name=forms.CharField(label='نام و نام خانوادگی')

    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("شماره تلفن معتبر وارد کنید")
            if len(phone) != 11:
                raise forms.ValidationError('شماره تلفن معتبر وارد کنید')
            else:
                return phone


class UpdateTweetForm(forms.ModelForm):

    tags=forms.CharField(required=False,widget=forms.TextInput(attrs={'class':' form-control border-black text-edit ','placeholder':'برچسب ها را با کاما(,)از یکدیگر جدا کنید'}))
    files=MultipleFileField(required=False)
    num_image=forms.CharField(required=False)


    class Meta:
        model=Tweet
        fields=['body']
        widgets={'body':forms.Textarea(attrs={'required':True,'class':' form-control border-black text-edit fs-5','cols': 3, 'rows': 7,'placeholder':'این فیلد اجباری است'})}
        labels={'body':'متن پیام'}




class ReportForm(forms.Form):
    body=forms.CharField(label="علت ریپورت")



class CommentCreateForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent'].widget.attrs.update(
            {'class': 'd-none'})
        self.fields['parent'].label = ''
        self.fields['parent'].required = False

    class Meta:
        model = Comment
        fields = ('parent', 'body')

        widgets = {


            'body': forms.Textarea(attrs={'class':" w-100 p-3 fs-5 textarea_tweet_detail ",
                                          'rows':7,'cols':8,'placeholder':'نظر خود را بنویسید...'}),

        }
        labels = {'body': 'متن پیام'}

    def save(self, *args, **kwargs):
        Comment.objects.rebuild()
        return super(CommentCreateForm, self).save(*args, **kwargs)


# ------------------------------------------------store book-------------------------------------------------------
class SaleBookForm(forms.Form):
    name_book=forms.CharField(label='اسم کتاب')
    price=forms.CharField(label='قیمت')
    author=forms.CharField(label='مولف')
    print_year=forms.CharField(label='سال چاپ')
    period_print=forms.CharField(label='نوبت چاپ')
    number_of_page=forms.CharField(label='تعداد صفحات')
    category=forms.CharField(label='موضوع و دسته بندی')
    book_introduction=forms.CharField(widget=forms.Textarea(),label='معرفی کتاب')
    photo=forms.ImageField(label='عکس')

    def clean_price(self):
        price = self.cleaned_data['price']
        if not price.isnumeric():
            raise ValidationError('قیمت را به درستی وارد کنید ')
        return price

    def clean_print_year(self):
        print_year = self.cleaned_data['print_year']
        if not print_year.isnumeric() :
            raise ValidationError('سال چاپ را به درستی وارد کنید ')
        if len(print_year)!=4:
            raise ValidationError('سال چاپ را به درستی وارد کنید ')

        return print_year

    def clean_period_print(self):
        period_print = self.cleaned_data['period_print']
        if not period_print.isnumeric() :
            raise ValidationError('نوبت چاپ را به درستی وارد کیند ')
        return period_print

    def clean_number_of_page(self):
        number_of_page = self.cleaned_data['number_of_page']
        if not number_of_page.isnumeric() :
            raise ValidationError('تعداد صفحات را به درستی وارد کنید ')
        return number_of_page

class BookCommentCreateForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset= BookComment.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent'].widget.attrs.update(
            {'class': 'd-none'})
        self.fields['parent'].label = ''
        self.fields['parent'].required = False

    class Meta:
        model = BookComment
        fields = ('parent', 'body')

        widgets = {


            'body': forms.Textarea(attrs={'class':" w-100 p-3 fs-5 textarea_tweet_detail ",
                                          'rows':7,'cols':8,'placeholder':'نظر خود را بنویسید...'}),

        }
        labels = {'body': 'متن پیام'}

    def save(self, *args, **kwargs):
        BookComment.objects.rebuild()
        return super(BookCommentCreateForm, self).save(*args, **kwargs)

class UpdateBookForm(forms.ModelForm):



    class Meta:
        model=SaleBook

        fields=['name_book','price','author','print_year'
            ,'period_print','number_of_page','category','book_introduction','photo']

        labels={'name_book':'اسم کتاب'
                ,'price':"قیمت کتاب",'author':'نویسنده'
                ,'print_year':'سال تولید'
                ,'period_print':'نوبت چاب'
                ,'number_of_page':'تعداد صفحات کتاب'
                ,'category':'دسته بندی'
                ,'book_introduction':'معرفی کتاب'
                ,'photo':'عکس'}

        widgets={'photo':forms.FileInput(attrs={'required':'true','class':'form-control'}),
                 'book_introduction':forms.Textarea(attrs={'required':True,'class':' form-control border-black text-edit fs-5','cols': 3, 'rows': 7,'placeholder':'این فیلد اجباری است'})
                 ,'name_book':forms.TextInput(attrs={'required':True,'class':' form-control border-black text-edit fs-5','placeholder':'این فیلد اجباری است'})
                 ,'author':forms.TextInput(attrs={'required':True,'class':' form-control border-black text-edit fs-5','placeholder':'این فیلد اجباری است'})
                 ,'price':forms.TextInput(attrs={'required':True,'class':' form-control border-black text-edit fs-5','placeholder':'این فیلد اجباری است'})
                 ,'print_year':forms.TextInput(attrs={'required':True,'class':' form-control border-black text-edit fs-5','placeholder':'این فیلد اجباری است'})
                 ,'period_print':forms.TextInput(attrs={'required':True,'class':' form-control border-black text-edit fs-5','placeholder':'این فیلد اجباری است'})
                 ,'number_of_page':forms.TextInput(attrs={'required':True,'class':' form-control border-black text-edit fs-5','placeholder':'این فیلد اجباری است'})}

    def clean_price(self):
        price = self.cleaned_data['price']
        if not price.isnumeric():
            raise ValidationError('قیمت را به درستی وارد کنید ')
        return price

    def clean_print_year(self):
        print_year = self.cleaned_data['print_year']
        if not print_year.isnumeric() :
            raise ValidationError('سال چاپ را به درستی وارد کنید ')
        if len(print_year)!=4:
            raise ValidationError('سال چاپ را به درستی وارد کنید ')

        return print_year

    def clean_period_print(self):
        period_print = self.cleaned_data['period_print']
        if not period_print.isnumeric() :
            raise ValidationError('نوبت چاپ را به درستی وارد کیند ')
        return period_print

    def clean_number_of_page(self):
        number_of_page = self.cleaned_data['number_of_page']
        if not number_of_page.isnumeric() :
            raise ValidationError('تعداد صفحات را به درستی وارد کنید ')
        return number_of_page

class RecommendedBookUserForm(forms.Form):
    photo = forms.ImageField(required=False,label='عکس کتاب')
    body = forms.CharField(widget=forms.Textarea(),label="معرفی کتاب")
    author = forms.CharField(label='نویسنده کتاب')
    book_name=forms.CharField(label='نام کتاب')

class UpdateRecommendedBookUserForm(forms.ModelForm):
    class Meta:
        model=RecommendedBookUser
        fields=['photo','author','book_name','body']
        labels={'photo':'عکس','author':'نام نویسنده','book_name':'نام کتاب','body':'معرفی کتاب'}

        widgets = {'photo': forms.FileInput(attrs={'required': 'false', 'class': 'form-control'}),
                   'book_name':forms.TextInput(attrs={"class" : "form-control border border-black"}),
                   'author':forms.TextInput(attrs={"class" : "form-control border border-black"}),
                   'body':forms.Textarea(attrs={'class':"form-control border border-black"})}


class RegistrationRequestedBookForm(forms.Form):
    name_book=forms.CharField(label='اسم کتاب')
    author=forms.CharField(label='نویسنده')
    print_year=forms.CharField(required=False,label='سال چاپ')
    category=forms.CharField(label='موضوع و دسته بندی')
    Description=forms.CharField(widget=forms.Textarea(),label='توضیحات')


    def clean_print_year(self):
        print_year = self.cleaned_data['print_year']
        if print_year:
            if not print_year.isnumeric() :
                raise ValidationError('سال چاپ را به درستی وارد کنید ')
            if len(print_year)!=4:
                raise ValidationError('سال چاپ را به درستی وارد کنید ')

            return print_year

class UpdateRequestedBookForm(forms.ModelForm):
    class Meta:
        model=RegistrationRequestedBook
        fields = ['category', 'author', 'name_book', 'print_year','Description']
        labels = {'category': 'دسته بتدی', 'author': 'نام نویسنده', 'name_book': 'نام کتاب', 'print_year': ' سال چاپ' ,
                  'Description':'توضیحات'}

        widgets = {'Description': forms.Textarea(
                       attrs={'required': True, 'class': ' form-control border-black  fs-5', 'cols': 3,
                              'rows': 7, 'placeholder': 'این فیلد اجباری است'})
            , 'name_book': forms.TextInput(
                attrs={'required': True, 'class': ' form-control border-black  fs-5',
                       'placeholder': 'این فیلد اجباری است'})
            , 'author': forms.TextInput(attrs={'required': True, 'class': ' form-control border-black  fs-5',
                                               'placeholder': 'این فیلد اجباری است'})

            , 'print_year': forms.TextInput(
                attrs={'required': False, 'class': ' form-control border-black  fs-5'
                       })
           }

    def clean_print_year(self):
        print_year = self.cleaned_data['print_year']
        if print_year:
            if not print_year.isnumeric():
                raise ValidationError('سال چاپ را به درستی وارد کنید ')
            if len(print_year) != 4:
                raise ValidationError('سال چاپ را به درستی وارد کنید ')

            return print_year




