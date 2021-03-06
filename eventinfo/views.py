from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import register
from django.urls import reverse
from django.core.paginator import Paginator
from django.template.loader import render_to_string

from django.contrib import messages
from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from eventinfo.models import Event, Event_types, Time_Slots, Tickets, Time_slot_status, Booking, Order_item, Order, \
    Event_organizers, Profile, Digital_links
from eventinfo.forms import EventSearchForm, ProfileForm, UserForm, BookingForm, SignupForm, PasswordResetRequestForm, \
    SetPasswordForm

import random
import string

from eventinfo.tokens import account_activation_token


def event_list(request):
    search_form = EventSearchForm(request.GET)
    events = Event.objects.filter(published=True)
    # events = Event.objects.all()

    is_bookmarked = False

    if search_form.is_valid():
        events = events.filter(event_title__contains=search_form.cleaned_data['q'])
        if search_form.cleaned_data['event_type']:
            events = events.filter(event_type=search_form.cleaned_data['event_type'])
        # TODO: get time slots for every events

        if search_form.cleaned_data['sort']:
            if search_form.cleaned_data['sort'] == 'date-desc':
                events = events.order_by('-event_start_date')
            if search_form.cleaned_data['sort'] == 'date-asc':
                events = events.order_by('event_start_date')

    paginator = Paginator(events, 2)
    page = request.GET.get('page')
    events = paginator.get_page(page)

    types = Event_types.objects.all()
    context = {
        'events_page': 'class=current',
        'search_form': search_form,
        'events': events,
        'types': types,

    }

    return render(request, 'eventinfo/events.html', context)


def event_detail(request, event_id):
    booking_form = BookingForm(request.GET)
    event = get_object_or_404(Event, pk=event_id)
    guests = event.event_guests.all()
    time_slots = Time_Slots.objects.filter(event_id=event_id).order_by('event_start_date')
    tickets = Tickets.objects.filter(ticket_time_slot__event_id=event_id)
    time_slot_status = Time_slot_status(4)
    is_bookmarked = False
    if request.user.is_authenticated:
        order_qs = Order.objects.filter(user=request.user, ordered=False, event=event)
        if event.bookmarks.filter(id=request.user.id).exists():
            is_bookmarked = True
    else:
        order_qs = None

    context = {
        'booking_form': booking_form,
        'guests': guests,
        'event': event,
        'time_slots': time_slots,
        'tickets': tickets,
        'time_slot_status': time_slot_status,
        'order_qs': order_qs,
        'is_bookmarked': is_bookmarked,
        'total_bookmarks': event.get_total_bookmarks(),
    }
    if event.is_unlimited:
        digital_link = Digital_links.objects.get(event_id=event_id)
        context['digital_link'] = digital_link

    return render(request, 'eventinfo/event.html', context)


@login_required
def booking_tickets(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    time_slots = Time_Slots.objects.filter(event_id=event_id).order_by('event_start_date')
    tickets = Tickets.objects.filter(ticket_time_slot__event_id=event_id)
    time_slot_status = Time_slot_status(4)
    order_qs = Order.objects.filter(user=request.user, ordered=False, event=event)

    context = {
        'event': event,
        'time_slots': time_slots,
        'tickets': tickets,
        'time_slot_status': time_slot_status,
        'order_qs': order_qs,
    }

    if request.method == 'POST':
        try:
            for key, value in request.POST.items():
                if key.isdigit():
                    ticket = get_object_or_404(Tickets, pk=key)
                    seats = int(value)
                    ticket.check_reserve_expire()
                    assert ticket.ticket_status == ticket.SALE_OPEN, 'وضعیت'
                    assert ticket.get_free_seats() >= seats, 'ظرفیت {}'.format(ticket.id)
                    add_to_cart(request, ticket.id, seats)
            assert order_qs.exists(), 'هیچ بلیتی انتخاب نکرده‌اید.'

        except Exception as e:
            context['error'] = str(e)
            return render(request, 'eventinfo/booking_tickets.html', context)
        else:
            return redirect("eventinfo:booking_checkout", event_id=event_id)

    return render(request, 'eventinfo/booking_tickets.html', context)


def validate_email_address(email):
    '''
    This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.
    '''
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def reset_password(request):
    form = PasswordResetRequestForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        '''
        A normal post request which takes input from field "email_or_username" (in ResetPasswordRequestForm).
        '''
        form = PasswordResetRequestForm(request.POST)
        try:
            if form.is_valid():
                data = form.cleaned_data["email_or_username"]
                if validate_email_address(data) is True:
                    '''
                    If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
                    '''
                    associated_users = User.objects.filter(Q(email=data) | Q(username=data))
                    current_site = get_current_site(request)
                    if associated_users.exists():
                        for user in associated_users:
                            c = {
                                'email': user.email,
                                'domain': current_site.domain,
                                'site_name': 'eventinfo.ir',
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'user': user,
                                'token': default_token_generator.make_token(user),
                                'protocol': 'http',
                                }

                            subject = 'Reset your Eventinfo account password.'
                            email = render_to_string('eventinfo/account/password_reset_email.html', c)
                            email = EmailMessage(subject, email, to=[user.email])
                            email.send()
                            messages.success(request, 'An email has been sent to ' + data +". Please check its inbox to continue reseting password.")
                    else:
                        messages.error(request, 'No user is associated with this email address')
                else:
                    '''
                    If the input is an username, then the following code will lookup for users associated with that user. If found then an email will be sent to the user's address, else an error message will be printed on the screen.
                    '''
                    associated_users = User.objects.filter(username=data)
                    current_site = get_current_site(request)
                    if associated_users.exists():
                        for user in associated_users:
                            c = {
                                'email': user.email,
                                'domain': current_site.domain,
                                'site_name': 'eventinfo.ir',
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'user': user,
                                'token': default_token_generator.make_token(user),
                                'protocol': 'http',
                                }

                            subject = 'Reset your Eventinfo account password.'
                            email = render_to_string('eventinfo/account/password_reset_email.html', c)
                            email = EmailMessage(subject, email, to=[user.email])
                            email.send()
                            messages.success(request, 'Email has been sent to ' + data +"'s email address. Please check its inbox to continue reseting password.")
                    else:
                        messages.error(request, 'This username does not exist in the system.')

        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'eventinfo/account/reset_password.html', context)


def reset_password_confirm(request, uidb64, token):
    form = SetPasswordForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        UserModel = get_user_model()
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = UserModel._default_manager.get(pk=uid)

        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset.')
            else:
                messages.error(request, 'Password reset has not been unsuccessful.')
        else:
            messages.error(request, 'The reset password link is no longer valid.')

    return render(request, 'eventinfo/account/reset_password_confirm.html', context)


def login_view(request):
    form = SignupForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        if request.POST.get('submit') == 'ورود':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('eventinfo:index')
            else:

                # TODO: LOAD ERROR MESSAGES IN POPUP FORM

                context = {
                    'user': username,
                    'error': False,
                    'message': 'کاربری با این مشخصات یافت نشد.',

                }
                return render(request, 'eventinfo/account/login.html/', context)

        elif request.POST.get('submit') == 'ثبت نام':
            form = SignupForm(request.POST)
            try:
                if form.is_valid():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    current_site = get_current_site(request)
                    mail_subject = 'Activate your Eventinfo account.'
                    message = render_to_string('eventinfo/account/acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    })
                    to_email = form.cleaned_data.get('email')
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()

                    context['error'] = True
                    context['message'] = 'برای تکمیل ثبت‌نام، لطفا ایمیل خودتون را تایید کنید.'

                else:
                    context = {
                        'form': form,
                        'error': False,
                        'message': form.errors,
                    }

            except Exception as e:
                context['error'] = False
                context['message'] = str(e)

            return render(request, 'eventinfo/account/login.html', context)

    else:
        if request.user.is_authenticated:
            return redirect('eventinfo:index')

        else:
            context = {
                'form': form
            }

    return render(request, 'eventinfo/account/login.html/', context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        Profile.objects.create(user=user, user_image='profiles/avatar/00.png')
        login(request, user)
        context = {
            'error': True,
            'message': 'ایمیل شما تایید شد، به ایونت‌اینفو خوش آمدید!',
        }
        return render(request, 'eventinfo/account/dashboard.html', context)
    else:
        context = {
            'error': False,
            'message': 'کد تایید ایمیل معتبر نمی‌باشد. لطفا مجددا تلاش کنید.',
        }

        return render(request, 'eventinfo/account/login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('eventinfo:event_list'))


@login_required
def account_profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, files=request.FILES, instance=request.user.profile)
        user_form = UserForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if request.POST.get('submit') == 'ذخیره تنظیمات':
            try:
                profile_form.save() and user_form.save()
                context = {
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'password_form': password_form,
                    'message': 'پروفایل با موفقیت ویرایش شد.',
                    'error': True
                }

            except:
                context = {
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'password_form': password_form,
                    'message': 'خطا در ویرایش اطلاعات',
                    'error': False
                }

        elif request.POST.get('submit') == 'تغییر رمز عبور':
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                context = {
                    'message': 'رمز عبور با موفقیت ویرایش شد.',
                    'error': True,
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'password_form': password_form,
                }
            else:
                context = {
                    'message': 'خطا در تغییر رمز عبور',
                    'error': False,
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'password_form': password_form,
                }


    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        password_form = PasswordChangeForm(request.user)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form,
        }

    context['account_profile'] = 'class=active'
    return render(request, 'eventinfo/account/profile.html', context)


@login_required
def account_bookings(request):
    orders = Order.objects.filter(user=request.user).order_by('-updated_at')

    context = {
        'account_bookings': 'class=active',
        'orders': orders
    }
    return render(request, 'eventinfo/account/dashboard-bookings.html', context)


@login_required
def account_invoice(request, ref_code):
    order = get_object_or_404(Order, ref_code=ref_code)
    if request.user == order.user:
        context = {
            'order': order
        }
    else:
        context = {

        }

    return render(request, 'eventinfo/account/dashboard-invoice.html', context)


@login_required
def account_dashboard(request):
    user = request.user
    # TODO: recent activities order_by
    recent_activities = user.bookmarks.all()[:5]
    orders = Order.objects.filter(user=request.user).order_by('-updated_at')[:4]

    context = {
        'account_dashboard': 'class=active',
        'orders': orders,
        'recent_activities': recent_activities,
    }

    return render(request, 'eventinfo/account/dashboard.html', context)


@login_required
def account_bookmarks(request):
    user = request.user
    bookmarks = user.bookmarks.all()
    context = {
        'account_bookmarks': 'class=active',
        'bookmarks': bookmarks,

    }

    return render(request, 'eventinfo/account/dashboard-bookmarks.html', context)


def index(request):
    search_form = EventSearchForm(request.GET)
    events = Event.objects.filter(published=True)
    event_type_list = events.values('event_type', 'event_type__type_icon', 'event_type__type_title').annotate(
        count=Count('event_type')).order_by()
    types = Event_types.objects.all()
    context = {
        'index_page': 'class=current',
        'search_form': search_form,
        'event_type_list': event_type_list,
        'events': events,
        'types': types,
    }

    return render(request, 'eventinfo/index.html', context)


@login_required
def booking_confirmation(request, event_id):
    if request.method == 'POST':
        order = Order.objects.get(user=request.user, ordered=False)

        # TODO: booking model needs additional filed for changed user profile
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        email = request.POST['email']
        mobile = request.POST['mobile']

        context = {
            'order': order,
            'first_name': first_name,
        }

        try:
            assert request.user.profile.spend(order.get_total_cost()), messages.error(request, 'موجودی حساب شما کافی نیست.')
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.ticket.reserve_seats(item.seats)
                item.save()
            order.ordered = True
            # order.payment = payment
            order.ref_code = create_ref_code()
            ordered_date = timezone.now()
            order.ordered_date = ordered_date
            order.save()

        except Exception as e:
            messages.error(request, str(e))
            

        return render(request, 'eventinfo/booking_confirmation.html', context)

    else:
        return redirect("eventinfo:index:")


@login_required
def add_to_cart(request, ticket_id, seats):
    ticket = get_object_or_404(Tickets, pk=ticket_id)
    event_id = ticket.ticket_time_slot.event_id.pk
    event = get_object_or_404(Event, pk=event_id)
    order_item, created = Order_item.objects.get_or_create(
        ticket=ticket,
        user=request.user,
        ordered=False,
        defaults={'seats': seats}
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.event == event:
            if order.items.filter(ticket_id=ticket.id).exists():
                diff_seats = seats - order_item.seats
                ticket.ticket_reserved += diff_seats
                ticket.save()
                order_item.seats = seats
                order_item.save()
                messages.info(request, "This item quantity was updated.")
            else:
                order.items.add(order_item)
                ticket.ticket_reserved += seats
                ticket.save()
                messages.info(request, "This item was added to your cart.")

        else:
            order.delete()
            order = Order.objects.create(user=request.user, event=event)
            order.items.add(order_item)
            ticket.ticket_reserved += seats
            ticket.save()
            messages.info(request, "This item was added to your cart.")

    else:
        order = Order.objects.create(user=request.user, event=event)
        order.items.add(order_item)
        ticket.ticket_reserved += seats
        ticket.save()
        messages.info(request, "This item was added to your cart.")

    if order_item.seats == 0:
        order_item.delete()

    if order.items.count() == 0:
        order.delete()


@login_required
def remove_card(request):

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    next = request.GET.get('next')
    if order_qs.exists():
        order = order_qs[0]
        items = order.items.all()
        for item in items:
            item.ticket.ticket_reserved -= item.seats
            item.ticket.save()
            item.delete()
        order.delete()
        messages.info(request, "Order was removed.")
        return redirect(next)
    else:
        messages.info(request, "You do not have an active order")
        return redirect(next)


@login_required
def booking_checkout(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    order = Order.objects.get(user=request.user, ordered=False)
    context = {
        'event': event,
        'order': order,
    }
    return render(request, 'eventinfo/booking_checkout.html', context)


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def organizer_profile(request, organizer_id):
    organizer = get_object_or_404(Event_organizers, pk=organizer_id)
    organizer_events = Event.objects.filter(event_organizer=organizer)
    context = {
        'organizer': organizer,
        'organizer_events': organizer_events,

    }

    return render(request, 'eventinfo/pages-organizer-profile.html', context)


@login_required
def bookmark_toggle(request):
    event_id = request.POST.get('event_id')
    event = get_object_or_404(Event, pk=event_id)

    if event.bookmarks.filter(id=request.user.id).exists():
        event.bookmarks.remove(request.user)
        is_bookmarked = False
    else:
        event.bookmarks.add(request.user)
        is_bookmarked = True
    context = {
        'event': event,
        'is_bookmarked': is_bookmarked,
        'total_bookmarks': event.get_total_bookmarks(),
    }

    if request.is_ajax():
        html = render_to_string('eventinfo/widgets/event_bookmark.html', context, request=request)
        return JsonResponse({'form': html})


def terms(request):
    context = {

    }

    return render(request, 'eventinfo/pages-terms.html', context)


def contact(request):
    context = {}

    if request.user.is_authenticated:
        user = request.user
        name_placeholder = user.get_full_name
        email_placeholder = user.email
        context = {
            'name_placeholder': name_placeholder,
            'email_placeholder': email_placeholder,
        }

    if request.method == 'POST':

        mail_subject = 'Message From Eventinfo.ir Contact Page'
        message = render_to_string('eventinfo/contact_page_email.html', {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'subject': request.POST.get('subject'),
            'comments': request.POST.get('comments'),
        })
        to_email = 'eventinfo.ir@gmail.com'
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        try:
            email.send()
            context['error'] = True
            context['message'] = 'پیام شما با موفقیت ارسال شد.'

        except:
            context = {
                'error': False,
                'message': 'خطا! لطفا مجددا تلاش کنید.',
                'name_placeholder': request.POST.get('name'),
                'email_placeholder': request.POST.get('email'),
                'subject_placeholder': request.POST.get('subject'),
                'comments_placeholder': request.POST.get('comments'),
            }

    return render(request, 'eventinfo/pages-contact.html', context)
