from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField


SEE = [
    ('unseen', 'unseen'),
    ('present', 'present'),
    ('seen', 'seen'),
]

STATUS = (
    (0, "Draft"),
    (1, "Publish")
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True) 
    pot = models.PositiveIntegerField(default=0, null=True,) 
    plan = models.CharField(max_length=20, blank=True, null=True, )
    balance = models.DecimalField(default=10.00, max_digits=8, decimal_places=2, blank=True, null=True,)
    capital = models.DecimalField(default=0.00, max_digits=8, decimal_places=2, blank=True, null=True,)
    commission = models.DecimalField(default=0.00, max_digits=8, decimal_places=2, blank=True, null=True,)
    email_confirmed = models.BooleanField(default=False)
    joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['joined']

    def __str__(self):
        return str(self.user)

    @receiver(post_save, sender=User)
    def update_profile_signal(sender, instance, created, **kwargs):
        user = instance
        if created:
            profile = Profile(user=user)
            profile.save()


class Plans(models.Model):
    profile = models. ManyToManyField(Profile, related_name='plans', null=True, blank=True)
    name = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    daily = models.PositiveIntegerField()
    weekly = models.PositiveIntegerField()
    monthly = models.PositiveIntegerField()
    annually = models.PositiveIntegerField()
    period = models.TextField(default="1year")
    tag = models.TextField()

    def __str__(self):
        return self.name



class Announcement(models.Model):
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=70, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    post_pic = models.ImageField(upload_to='post_pics/', null=True, blank=True)
    like = models.ManyToManyField(User, blank=True, related_name='post_likes')
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=1)
    not_status = models.CharField(max_length=10, choices=SEE, default='unseen')
    visits = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    not_status = models.CharField(max_length=10, choices=SEE, default='unseen')
    body = models.TextField()
    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
    dp = models.ImageField(upload_to="comment_dp", null=True)
    comment_pic = models.ImageField(upload_to='comment_pics/', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    visits = models.IntegerField(default=0)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('comment_detail', args=[str(self.id)])


class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    name = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    dp = models.ImageField(upload_to="comment_dp", null=True)
    comment_pic = models.ImageField(upload_to='comment_pics/', null=True, blank=True)
    likes = models.ManyToManyField(User, blank=True, related_name='reply_likes')
    created_on = models.DateTimeField(auto_now_add=True)
    not_status = models.CharField(max_length=10, choices=SEE, default='unseen')


class Wallet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=9, decimal_places=4)
    cost = models.DecimalField(default=0.00, max_digits=8, decimal_places=2, blank=True, null=True,)
    price = models.DecimalField(default=0.00, max_digits=8, decimal_places=2, blank=True, null=True,)

    def __str__(self):
        return self.crypto


class Deposit(models.Model):
    depositor = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    crypto = models.CharField(max_length=100)
    created_on = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.amount


class Withdraw(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=36, blank=True, null=True)
    cc_number = CardNumberField('card number')
    cc_expiry = CardExpiryField('expiration date')
    cc_code = SecurityCodeField('security code')

    def __str__(self):
        return self.name