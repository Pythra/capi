from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import View, UpdateView, DeleteView

from .forms import UserRegisterForm, AnnouncementForm, PostForm, WithdrawForm, ProfileForm
from .models import Profile, Announcement, Comment, Reply, Post, Withdraw, Deposit, Wallet, Plans
from .tokens import account_activation_token
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

from chat.models import Message



def index(request):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '15',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '43be9fd4-af5b-4dbe-9379-6f749d993f8d',
    }

    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        coins = response.json()['data']
    except ConnectionError as e:
        print(e)
        coins = "No response"

    ann = Announcement.objects.all
    posts = Post.objects.all
    plans = Plans.objects.all
    if request.user.is_authenticated:
        user = Profile.objects.get(user=request.user)
        capital = float(request.user.profile.balance)
        balance = float(request.user.profile.balance)
        pot = float(user.pot)
        com = float(request.user.profile.commission)
        withdraw = 0.8*balance
        plans = Plans.objects.all
        my_wallets = Wallet.objects.filter(owner=request.user) 
        context = {'ann': ann, 'posts': posts, 'coins': coins, 'capital': capital, 'plans':plans,
                    'withdraw': withdraw, 'com':com}
        return render(request, 'cap/index.html', context) 
 
    context = {'ann': ann, 'posts': posts, 'coins': coins, 'plans':plans }
    return render(request, 'cap/index.html', context)


class SignUpView(View):
    form_class = UserRegisterForm
    template_name = 'cap/signup.html'
    

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()

            return redirect('login')

        return render(request, self.template_name, {'form': form})


class ActivateAccount(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            login(request, user)
            messages.success(request, ('Your account have been confirmed.'))
            return redirect('home')
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('home')


def announcement_form(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = AnnouncementForm()
    context = {'form': form}
    return render(request, 'cap/announcement_form.html', context)


@login_required
def profile_form(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if profile_form.is_valid():
            profile_form.save()
            return HttpResponseRedirect(reverse('home'))

    else:
        profile_form = ProfileForm(instance=request.user.profile)

    context = {
        'p_form': profile_form
    }
    return render(request, 'cap/profile_form.html', context)


def post_list(request):
    posts = Post.objects.filter(status=1).order_by('-created_on')
    paginator = Paginator(posts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'posts': posts, 'page_obj': page_obj}
    if request.user.is_authenticated:
        note_comments = Comment.objects.filter(post__creator=request.user, not_status='unseen').exclude(
            name=request.user)
        note_mentions = Comment.objects.filter(body__icontains=request.user, not_status='unseen').exclude(
            name=request.user)
        note_replies = Reply.objects.filter(comment__name=request.user, not_status='unseen')
        context = {'note_comments': note_comments, 'note_mentions': note_mentions, 'note_replies': note_replies,
                   'posts': posts, 'page_obj': page_obj}
    return render(request, 'cap/post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.visits = post.visits + 1
    post.save()
    post = get_object_or_404(Post, slug=slug)
    context = {'post': post, 'slug': slug, 'visits': post.visits,
               }
   
    return render(request, 'cap/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = PostForm()
    context = {'form': form}
    if request.user.is_authenticated:
        note_comments = Comment.objects.filter(post__creator=request.user, not_status='unseen').exclude(
            name=request.user)
        note_mentions = Comment.objects.filter(body__icontains=request.user, not_status='unseen').exclude(
            name=request.user)
        note_replies = Reply.objects.filter(comment__name=request.user, not_status='unseen')
        context = {'note_comments': note_comments, 'note_mentions': note_mentions, 'note_replies': note_replies,
                   'form': form}
    return render(request, 'cap/post_form.html', context)


class PostUpdate(UpdateView, LoginRequiredMixin):
    template_name = 'cap/post_update.html'
    model = Post
    form_class = PostForm


class PostDelete(DeleteView, LoginRequiredMixin):
    model = Post
    success_url = reverse_lazy('home')


@login_required
def settings(request):
    context = {}
    return render(request, 'cap/settings.html', context)


@login_required
def trade(request):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '12',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '43be9fd4-af5b-4dbe-9379-6f749d993f8d',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        coins = response.json()['data']
    except ConnectionError as e:
        coins = "No response"

    context = {'coins': coins}
    return render(request, 'cap/trade.html', context)



def payment(request):
    context = {}
    return render(request, 'cap/payment.html', context)
 

@login_required
def buy(request):
    cash =  float(request.POST.get('cash'))
    price = request.POST.get('price')
    name = request.POST.get('name')
    sym = request.POST.get('sym')
    bal = request.user.profile.balance
    buy = float(price)/float(cash)
    context = {'name':name, 'buy':buy, 'cash':cash, 'price':price, 'sym':sym, 'bal':bal}
    return render(request, 'cap/buy.html', context)


@login_required
def wallets(request):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '12',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '43be9fd4-af5b-4dbe-9379-6f749d993f8d',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        coins = response.json()['data']
    except ConnectionError as e:
        coins = "No response"
 
    cash =  request.POST.get('cash')
    price = request.POST.get('price')
    name = request.POST.get('name')
    sym = request.POST.get('sym')
    bal = request.user.profile.balance
    user = Profile.objects.get(user=request.user)
    user.balance = float(user.balance) - float(cash)
    user.save()
    buy = request.POST.get('buy')
    wallets = Wallet.objects.filter(owner=request.user)
    try:
        wallet = Wallet.objects.get(owner=request.user, crypto=name)
        wallet.total = float(wallet.total) + float(buy)
        wallet.save()
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(owner=request.user, crypto=name, total=buy, cost=cash)
        wallet.save()
    context = {'name':name, 'buy':buy, 'cash':cash, 'price':price, 'wallets':wallets, 'sym':sym, 'bal':bal,
            'coins': coins
    }
    return render(request, 'cap/wallets.html', context)


@login_required
def my_wallets(request):
    wallets = Wallet.objects.filter(owner=request.user)

    context = {'wallets':wallets}
    return render(request, 'cap/my_wallets.html', context)


def terms(request): 
    return render(request, 'cap/includes/terms.html')


def faq(request): 
    return render(request, 'cap/includes/faq.html')



@login_required
def plan_detail(request): 
    plan =  request.POST.get('plan')
    cost =  request.POST.get('cost')
    earn =  request.POST.get('earn')
    user = Profile.objects.get(user=request.user)
    pot = float(user.pot)
    pot = pot + float(earn)
    user.balance = float(user.balance) - float(cost)
    user.pot = pot
    user.plan = plan
    user.save() 
    context = {'plan':plan, 'cost':cost, 'earn':earn}
    return render(request, 'cap/includes/plan_detail.html', context)


@login_required
def admin(request):
    profiles = Profile.objects.all().order_by('-joined')

    context = { 'profiles':profiles
        }
    return render(request, 'cap/admin.html', context)


class ProfileUpdate(UpdateView, LoginRequiredMixin):
    template_name = 'cap/profile_update.html'
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy('admin')


class ProfileDelete(DeleteView, LoginRequiredMixin):
    model = Profile
    success_url = reverse_lazy('admin')





