from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from .models import Customer

def customer_profile(sender, instance, created, **kwargs):
    group = Group.objects.filter(name="customer")

    print(type(group))

    if not group.exists():
        print("Group does not exits")
        group = Group.objects.create(name='customer')
    else:
        print("Group exits")
    
    if created:
        if instance.email != 'admin@admin.com':
            instance.groups.add(group[0])

        Customer.objects.create(user=instance, name=instance.username)

        print("Profile was created")

post_save.connect(customer_profile, sender=User)



    # groups = Group.objects.all()
    # print("Groups: ", groups)
    # for c in groups:
    #     if c.name == 'customer':
    #         print()

    # if 'customer' not in groups:
    #     print("customer not in groups")
    #     Group.objects.create(name='customer')
    # else:
    #     print("Customer in groups")
    
    # if created:
    #     group = Group.objects.get(name='customer')
    #     if instance.email != 'admin@admin.com':
    #         instance.groups.add(group)

    #     Customer.objects.create(user=instance, name=instance.username)

    #     print("Profile was created")

post_save.connect(customer_profile, sender=User)
