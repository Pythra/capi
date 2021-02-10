from django.contrib import admin
from .models import Profile, Announcement, Post, Withdraw, Wallet, Deposit

admin.site.register(Profile)
admin.site.register(Announcement)
admin.site.register(Post)
admin.site.register(Withdraw)
admin.site.register(Wallet)
admin.site.register(Deposit)
