#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Liangwei_site.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


    # from search.models import SportType
    # sports = ['Ski','Rock Climbing','Tennis','Badminton','Swimming','Table Tennis','Gym','Basketball','Baseball','football',
    #           'Horse Riding']
    # for s in sports:
    #     q = SportType(name=s)
    #     q.save()


