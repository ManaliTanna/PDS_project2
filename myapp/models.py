from django.db import models

class Hoods(models.Model):
    hood_id = models.AutoField(primary_key=True)
    hood_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'hoods'

class Blocks(models.Model):
    block_id = models.AutoField(primary_key=True)
    block_name = models.CharField(max_length=50, unique=True)
    hood_id = models.ForeignKey(Hoods, on_delete=models.CASCADE, db_column='hood_id')
    block_description = models.TextField(default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    radius = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'blocks'

class Address(models.Model):
    addr_id = models.AutoField(primary_key=True)
    apt_number = models.CharField(max_length=10, blank=True, null=True)
    street_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'address'

class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.TextField(unique=True)
    password = models.TextField(default='test@123')
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField()
    phone_number = models.TextField()
    number_of_family_members = models.IntegerField()
    user_photo = models.BinaryField(null=True, editable=True)
    intro = models.TextField()
    addr_id = models.ForeignKey(Address, on_delete=models.CASCADE, db_column='addr_id',to_field='addr_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'users'

class Membership(models.Model):
    membership_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    block_id = models.ForeignKey(Blocks, on_delete=models.CASCADE, db_column='block_id')
    status = models.CharField(max_length=15, choices=(('approved', 'Approved'), ('not approved', 'Not Approved')))
    permissions = models.CharField(max_length=10, choices=(('read', 'Read'), ('write', 'Write')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'membership'

class Applications(models.Model):
    application_id = models.AutoField(primary_key=True)
    block_id = models.ForeignKey(Blocks, on_delete=models.CASCADE, db_column='block_id')
    applicant_id = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='applicant_id')
    application_status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: 
        db_table = 'applications'

class Votes(models.Model):
    vote_id = models.AutoField(primary_key=True)
    voter_id = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='voter_id')
    application_id = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'votes'

class Friendship(models.Model):
    user_id = models.ForeignKey(Users, related_name='friendship_user', on_delete=models.CASCADE, db_column='user_id')
    friend_id = models.ForeignKey(Users, related_name='friendship_friend', on_delete=models.CASCADE, null=True, db_column='friend_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'friendship'
        unique_together = ('user_id', 'friend_id')

class Neighbors(models.Model):
    user_id = models.ForeignKey(Users, related_name='neighbor_user', on_delete=models.CASCADE, db_column='user_id')
    neighbor_id = models.ForeignKey(Users, related_name='neighbor_neighbor', on_delete=models.CASCADE, db_column='neighbor_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'neighbors'
        unique_together = ('user_id', 'neighbor_id')

class Thread(models.Model):
    thread_id = models.AutoField(primary_key=True)
    thread_title = models.CharField(max_length=100)
    first_sender_id = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='first_sender_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'thread'

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    thread_id = models.ForeignKey(Thread, on_delete=models.CASCADE, db_column='thread_id')
    reply_to_message_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    recipient = models.CharField(max_length=15, choices=(('friend', 'Friend'), ('neighbor', 'Neighbor'), ('block', 'Block'), ('hood', 'Hood')))
    friend_id = models.ForeignKey(Users, related_name='message_friend', on_delete=models.CASCADE, null=True, db_column='friend_id')
    block_id = models.ForeignKey(Blocks, on_delete=models.CASCADE, null=True, db_column='block_id')
    hood_id = models.ForeignKey(Hoods, on_delete=models.CASCADE, null=True, db_column='hood_id')
    text_body = models.TextField()
    addr_id = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, db_column='addr_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'message'
