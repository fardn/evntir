from django.contrib.auth.models import User
from django.db import models

from django.shortcuts import get_object_or_404
from django.utils import timezone

from jalali_date import datetime2jalali, date2jalali


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
    type_icon = models.CharField('آیکن', max_length=50, blank=True, null=True, default=None)

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
    organizer_logo = models.ImageField('تصویر', upload_to='main_image/organizers/logo/', null=True, blank=True,
                                       default=None)
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
    guest_image = models.ImageField('تصویر', upload_to='profiles/avatar/', default='profiles/avatar/00.png')

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
    event_type = models.ForeignKey('Event_types', on_delete=models.PROTECT, null=True, blank=True, default=None,
                                   verbose_name='نوع رویداد')
    event_organizer = models.ForeignKey('Event_organizers', on_delete=models.PROTECT, null=True, blank=True,
                                        default=None, verbose_name='برگزارکننده')
    event_venue = models.ForeignKey('Event_venues', on_delete=models.PROTECT, null=True, blank=True, default=None,
                                    verbose_name='محل برگزاری')
    event_description = models.TextField('توضیحات')
    event_main_image = models.ImageField('تصویر', upload_to='main_image/', null=True, blank=True)
    event_guests = models.ManyToManyField('Guest', blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    event_start_date = models.DateTimeField('تاریخ و ساعت شروع', null=True, blank=True)
    event_end_date = models.DateTimeField('تاریخ و ساعت پایان', null=True, blank=True)
    min_price = models.IntegerField('شروع قیمت', null=True, blank=True)
    max_price = models.IntegerField('بیشترین قیمت', null=True, blank=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.event_title, self.event_organizer, self.event_venue)

    def get_start_date(self):
        min_start_date = \
        Time_Slots.objects.filter(event_id_id=self.id).values('event_start_date').order_by('event_start_date')[0]
        return min_start_date['event_start_date']

    def get_end_date(self):
        min_start_date = \
        Time_Slots.objects.filter(event_id_id=self.id).values('event_start_date').order_by('-event_start_date')[0]
        return min_start_date['event_start_date']

    def get_min_price(self):
        min_start_date = \
        Tickets.objects.filter(ticket_time_slot__event_id_id=self.id).values('ticket_price').order_by('ticket_price')[0]
        return min_start_date['ticket_price']

    def get_max_price(self):
        min_start_date = \
        Tickets.objects.filter(ticket_time_slot__event_id_id=self.id).values('ticket_price').order_by('-ticket_price')[
            0]
        return min_start_date['ticket_price']

    def get_price_display(self):
        min_price = self.min_price
        max_price = self.max_price

        if min_price == max_price and min_price == 0:
            return 'رایگان'
        elif min_price == max_price:
            return '{} تومان'.format(min_price)
        else:
            return 'از {} تا {} تومان'.format(min_price, max_price)

    def get_start_date_display(self):
        event_start_date = self.event_start_date
        event_end_date = self.event_end_date

        if event_start_date.date() == event_end_date.date():
            return datetime2jalali(event_start_date).strftime('%Y/%m/%d ساعت %H:%M ')
        else:
            return 'از {}'.format(datetime2jalali(event_start_date).strftime('%Y/%m/%d ساعت %H:%M '))

    def get_published(self):
        try:
            self.event_start_date = self.get_start_date()
            self.event_end_date = self.get_end_date()
            self.min_price = self.get_min_price()
            self.max_price = self.get_max_price()
            self.published = True
            self.save()

        except Exception as e:
            return str(e)


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

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def spend(self, amount):
        if self.balance < amount:
            return False
        self.balance -= amount
        self.save()
        return True


class Time_Slots(models.Model):
    """
    Representing Event time slots
    """

    class Meta:
        verbose_name = 'سانس'
        verbose_name_plural = 'سانس'

    event_id = models.ForeignKey('Event', on_delete=models.CASCADE, verbose_name='شناسه رویداد')
    event_start_date = models.DateTimeField('تاریخ و ساعت شروع')
    event_end_date = models.DateTimeField('تاریخ و ساعت پایان')
    SALE_NOT_STARTED = 1
    SALE_OPEN = 2
    SOLD_OUT = 3
    SALE_CLOSED = 4
    TIME_SLOT_PASSED = 5
    TIME_SLOT_CANCELED = 6
    TIME_SLOT_ARCHIVED = 7
    status_choices = (
        (SALE_NOT_STARTED, 'بلیت فروشی آغاز نشده.'),
        (SALE_OPEN, 'بلیت فروشی آغاز شده.'),
        (SOLD_OUT, 'بلیت‌ها تمام شد.'),
        (SALE_CLOSED, 'بلیت فروشی بسته شد.'),
        (TIME_SLOT_PASSED, 'سانس به پایان رسیده'),
        (TIME_SLOT_CANCELED, 'بلیت لغو شده'),
        (TIME_SLOT_ARCHIVED, 'بلیت حذف شده'),

    )

    time_slot_status = models.IntegerField(choices=status_choices, null=True, blank=True)
    total_seats = models.IntegerField(default=0)
    free_seats = models.IntegerField()

    def __str__(self):
        return '{} - {}'.format(self.event_id.event_title, self.event_start_date)

    def get_tickets(self):
        time_slot_tickets = Tickets.objects.filter(ticket_time_slot_id=self.id).order_by('ticket_order_start_date')
        return time_slot_tickets


class Tickets(models.Model):
    """
    Representing Event time slots tickets
    """

    class Meta:
        verbose_name = 'بلیت'
        verbose_name_plural = 'بلیت'

    ticket_time_slot = models.ForeignKey('Time_Slots', on_delete=models.PROTECT, verbose_name='سانس')
    TICKET_TYPE_CHOICES = ((0, 'رایگان'), (1, 'پولی'), (2, 'حمایتی'))
    ticket_type = models.IntegerField('نوع بلیت', choices=TICKET_TYPE_CHOICES)
    ticket_title = models.CharField('عنوان', max_length=50)
    ticket_description = models.TextField('توضیحات بلیت', null=True, blank=True)
    ticket_seats = models.IntegerField('تعداد بلیت')
    ticket_sold = models.IntegerField('بلیت‌های فروخته شده', default=0)
    ticket_price = models.IntegerField('قیمت بلیت', null=True, blank=True)
    ticket_order_start_date = models.DateTimeField('ساعت شروع فروش بلیت', null=True, blank=True, default=timezone.now)
    ticket_order_end_date = models.DateTimeField('ساعت پایان فروش بلیت', null=True, blank=True)
    ticket_is_passed = models.BooleanField('رویداد گذشته', default=False)
    ticket_is_canceled = models.BooleanField('بلیت لغو شده', default=False)

    SALE_NOT_STARTED = 1
    SALE_OPEN = 2
    SOLD_OUT = 3
    SALE_CLOSED = 4
    TICKET_PASSED = 5
    TICKET_CANCELED = 6
    TICKET_ARCHIVED = 7
    status_choices = (
        (SALE_NOT_STARTED, 'بلیت فروشی آغاز نشده.'),
        (SALE_OPEN, 'بلیت فروشی آغاز شده.'),
        (SOLD_OUT, 'بلیت‌ها تمام شد.'),
        (SALE_CLOSED, 'بلیت فروشی بسته شد.'),
        (TICKET_PASSED, 'رویداد به پایان رسیده'),
        (TICKET_CANCELED, 'بلیت لغو شده'),
        (TICKET_ARCHIVED, 'بلیت حذف شده'),

    )
    ticket_status = models.IntegerField(choices=status_choices, null=True, blank=True)

    def __str__(self):
        return '{} | {} | {} | sold: {} | {}'.format(self.ticket_time_slot, self.ticket_type, self.ticket_price,
                                                     self.ticket_sold, self.ticket_order_start_date)

    def get_free_seats(self):
        return self.ticket_seats - self.ticket_sold

    def get_price(self):
        if self.ticket_type == 2:
            return 'حمایتی'
        if self.ticket_price == 0:
            return 'رایگان'
        if self.ticket_price > 0:
            return '{} تومان'.format(self.ticket_price)

    def get_status(self):
        NOW = timezone.now()
        if self.ticket_status not in (Tickets.TICKET_CANCELED, Tickets.TICKET_ARCHIVED):
            if self.ticket_order_end_date is None:
                self.ticket_order_end_date = self.ticket_time_slot.event_start_date
                self.save()

            if self.ticket_order_start_date > NOW:
                self.ticket_status = Tickets.SALE_NOT_STARTED
                self.save()

            if self.ticket_order_start_date < NOW < self.ticket_order_end_date:
                self.ticket_status = Tickets.SALE_OPEN
                self.save()

            if self.ticket_order_end_date < NOW:
                self.ticket_status = Tickets.SALE_CLOSED
                self.save()

            if self.ticket_time_slot.event_start_date < NOW:
                self.ticket_status = Tickets.TICKET_PASSED
                self.save()

            if self.get_free_seats() == 0:
                self.ticket_status = Tickets.SOLD_OUT
                self.save()

        return self.ticket_status, self.get_ticket_status_display

    def reserve_seats(self, seat_count):
        """
        Reserves one or more seats for a customer
        :param seat_count: An integer as the number of seats to be reserved
        """
        assert isinstance(seat_count, int) and seat_count > 0, 'Number of seats should be a positive integer'
        assert self.ticket_status == Tickets.SALE_OPEN, 'Sale is not open'
        assert self.get_free_seats() >= seat_count, 'Not enough free seats'
        self.ticket_sold += seat_count
        if self.get_free_seats() == 0:
            self.ticket_status = Tickets.SOLD_OUT
        self.save()


class Booking(models.Model):
    class Meta:
        verbose_name = 'رزرو'
        verbose_name_plural = 'رزرو'

    book_number = models.IntegerField('شماره سفارش')
    book_user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='کاربر')
    book_ticket = models.ForeignKey('Tickets', on_delete=models.PROTECT, verbose_name='بلیت')
    book_seats = models.IntegerField('تعداد')
    book_created_at = models.DateTimeField(auto_now_add=True)
    book_total_cost = models.IntegerField('قیمت کل')


def Time_slot_status(time_slot_id):
    NOW = timezone.now()
    this_time_slot = get_object_or_404(Time_Slots, pk=time_slot_id)
    time_slot_tickets = Tickets.objects.filter(ticket_time_slot_id=time_slot_id).order_by(
        'ticket_order_start_date')
    first_ticket_order_start_date = time_slot_tickets[0].ticket_order_start_date

    time_slot_tickets = time_slot_tickets.order_by('-ticket_order_end_date')
    last_ticket_order_end_date = time_slot_tickets[0].ticket_order_end_date

    if first_ticket_order_start_date > NOW:
        this_time_slot.time_slot_status = Time_Slots.SALE_NOT_STARTED
        this_time_slot.save()

    elif last_ticket_order_end_date < NOW:
        this_time_slot.time_slot_status = Time_Slots.SALE_CLOSED
        this_time_slot.save()

    elif this_time_slot.free_seats == 0:
        this_time_slot.time_slot_status = Time_Slots.SOLD_OUT
        this_time_slot.save()

    elif this_time_slot.time_slot_status not in (Time_Slots.TIME_SLOT_CANCELED, Time_Slots.TIME_SLOT_ARCHIVED):
        this_time_slot.time_slot_status = Time_Slots.SALE_OPEN
        this_time_slot.save()

    return this_time_slot.time_slot_status


class Order_item(models.Model):
    class Meta:
        verbose_name = 'آیتم'
        verbose_name_plural = 'آیتم'

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    ticket = models.ForeignKey('Tickets', on_delete=models.CASCADE, verbose_name='بلیت')
    seats = models.IntegerField('تعداد')
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return 'item: {} Ticket of ticket id {}'.format(self.seats, self.ticket.id)

    def get_total_item_price(self):
        return self.seats * self.ticket.ticket_price


class Order(models.Model):
    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبد خرید'

    ref_code = models.CharField(max_length=20, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, verbose_name='رویداد')
    items = models.ManyToManyField('Order_item')
    start_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total_cost(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total

    def get_total_seats(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.seats
        return total

    def get_status_class(self):
        if self.ordered:
            return 'approved-booking'
        else:
            return 'pending-booking'

    def get_event(self):
        event = get_object_or_404(Event, pk=self.event.pk)
        return event
