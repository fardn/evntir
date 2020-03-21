from django.contrib.auth.models import User
from django.db import models


class Cities(models.Model):
    """
    Representing Cities
    """
    class Meta:
        verbose_name = 'شهر'
        verbose_name_plural = 'شهر'

    city_name = models.CharField('نام شهر', max_length=50)

    def __str__(self):
        return self.city_name


class Event_types(models.Model):
    """
    Representing Event Types
    """
    class Meta:
        verbose_name = 'نوع'
        verbose_name_plural = 'نوع'

    type_title = models.CharField('عنوان', max_length=50)

    def __str__(self):
        return self.type_title


class Event_organizers(models.Model):
    """
    Representing Event Organizers
    """
    class Meta:
        verbose_name = 'برگزارکننده'
        verbose_name_plural = 'برگزارکننده'

    organizer_name = models.CharField('برگزارکننده', max_length=50)
    organizer_logo = models.ImageField('تصویر', upload_to='main_image/organizers/logo/', null=True, blank=True, default=None)
    organizer_instagram = models.CharField('اینستاگرام', max_length=50, null=True, blank=True)

    def __str__(self):
        return self.organizer_name


class Event_venues(models.Model):
    """
    Representing Event Venue
    """
    class Meta:
        verbose_name = 'محل برگزاری'
        verbose_name_plural = 'محل برگزاری'

    venue_name = models.CharField('نام محل', max_length=100)
    venue_address = models.TextField('آدرس')
    venue_city = models.ForeignKey('Cities', on_delete=models.PROTECT, verbose_name='شهر')
    venue_map_lat = models.CharField('عرض جغرافیایی', max_length=50, null=True, blank=True, default=None)
    venue_map_long = models.CharField('طول جغرافیایی', max_length=50, null=True, blank=True, default=None)

    def __str__(self):
        return self.venue_name


class Guest(models.Model):
    """
    Representing Event Guests
    """
    class Meta:
        verbose_name = 'مهمان'
        verbose_name_plural = 'مهمان'

    guest_name = models.CharField('نام و نام خانوادگی', max_length=50)
    guest_email = models.EmailField('ایمیل', blank=True, null=True)
    guest_website = models.CharField('وبسایت', max_length=50)
    guest_instagram = models.CharField('اینستاگرام', max_length=50)
    guest_image = models.ImageField('تصویر', upload_to='main_image/profiles/avatar/', null=True, blank=True)

    def __str__(self):
        return self.guest_name


class Event(models.Model):
    """
    Representing an Event
    """
    class Meta:
        verbose_name = 'رویداد'
        verbose_name_plural = 'رویداد'

    event_title = models.CharField(max_length=200, verbose_name='عنوان')
    event_start_date = models.DateTimeField('تاریخ و ساعت شروع')
    event_end_date = models.DateTimeField('تاریخ و ساعت پایان')
    event_type = models.ForeignKey('Event_types', on_delete=models.PROTECT, null=True, blank=True, default=None, verbose_name='نوع رویداد')
    event_organizer = models.ForeignKey('Event_organizers', on_delete=models.PROTECT, null=True, blank=True, default=None, verbose_name='برگزارکننده')
    event_venue = models.ForeignKey('Event_venues', on_delete=models.PROTECT, null=True, blank=True, default=None, verbose_name='محل برگزاری')
    event_description = models.TextField('توضیحات')
    event_main_image = models.ImageField('تصویر', upload_to='main_image/', null=True, blank=True)
    event_guests = models.ManyToManyField('Guest', blank=True, default=None)

    def __str__(self):
        return '{} - {} - {}'.format(self.event_title, self.event_organizer, self.event_venue)


class Profile(models.Model):
    """
    Representing user profile
    """

    class Meta:
        verbose_name_plural = 'پروفایل کاربری'
        verbose_name = 'پروفایل کاربری'

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='حساب کاربری')
    mobile = models.CharField('موبایل', max_length=11)
    GENDER_CHOICES = ((1, 'مرد'), (0, 'زن'))
    gender = models.IntegerField('جنسیت', choices=GENDER_CHOICES, null=True, blank=True)
    bday = models.DateField('تاریخ تولد', null=True, blank=True)
    user_image = models.ImageField('', upload_to='main_image/users/avatar/', null=True, blank=True)
    balance = models.IntegerField('اعتبار', default=0)

    def __str__(self):
        return self.user.get_full_name()

    def get_balance_display(self):
        return '{} تومان'.format(self.balance)





