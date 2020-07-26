# -*- coding: utf-8 -*-

import datetime
import json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views.generic import ListView
from .forms import SignUpForm
from .models import Employee
from .models import Request
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
#from django.contrib.auth.forms import UserCreationForm


# PENDING = "PENDING"
PENDING = "Pending Approval"
APPROVED = "Approved"
REJECTED = "Rejected"


class MainView(TemplateView):

    @csrf_exempt
    @method_decorator(login_required)
    def get(self, request):
        
        #Get time in required format
        fmt = '%Y%m%d'
        today = datetime.datetime.now().strftime(fmt)


@login_required()
@csrf_exempt
def registration(request):
    
    # response html for employee and manager   
    template_response_employee = 'registration.html'

    username = request.user.username
    details = Employee.objects.filter(employeeID=username).values_list(
        "employeeName")
    fullname = details[0][0]
    return render(request, template_response_employee, {'employeeID': username,
                                                        'fullname': fullname})


@login_required()
@csrf_exempt
def createRequest(request):
    
    #Response to be sent to this
    template_response = 'acknowledge.html'
    
    #Update Employee Table with the record.
    id = request.user.username
    purpose = request.POST.get('purpose')
    area = request.POST.get('area')
    zone = request.POST.get('zone')
    status=PENDING
    # Date
    fmt = '%Y-%m-%d'
    today = datetime.datetime.now().strftime(fmt)
    
    managerDetails = Employee.objects.filter(employeeID=id).values_list('mgrID', 'mgrName', 'employeeName')
    managerID = managerDetails[0][0]
    managerName = managerDetails[0][1]
    username = managerDetails[0][2]
    
    record = Request(employeeID=id, username=username, managerID=managerID, managerName=managerName, date=today, zone=zone, purpose=purpose, status=status)
    record.save()
    
    return render(request, template_response, {'employeeID': id, 'username': username, 'managerID': managerID, 'managerName': managerName, 'date': today, 'zone': zone, 'purpose': purpose, 'status': status})


@login_required()
@csrf_exempt
def updateRequest(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    import datetime
    empid = eval(body['data'])[0]
    req = Request.objects.filter(employeeID=empid)
    action = body['action']
    status = PENDING
    if action == 'approve':
        status = APPROVED
    if action == 'reject':
        status = REJECTED

    req.update(status=status)
    return redirect("/dashboard")


@login_required()
@csrf_exempt
def dashboard(request):
    # response html for employee and manager
    emp_dashboard_template = "emp_home.html"
    mgr_dashboard_template = 'mgr_home.html'

    username = request.user.username
    details = Employee.objects.filter(employeeID=username).values_list(
        "employeeName",
        "mgrID",
        "mgrName"
    )
    name = details[0][0]
    manager_id = details[0][1]

    if manager_id == "NA":
        # IF there is no managerID that means he/she is a manager.
        pending_reqs = Request.objects.filter(
            managerID=username).values_list('employeeID', 'username', 'date',
                                            'zone', 'purpose', 'status')
        return render(request, mgr_dashboard_template,
                      {'pendingApproval': pending_reqs,
                       'length_records': len(pending_reqs)})
    else:
        return render(request, emp_dashboard_template, {'fullname': name})


class RequetsView(ListView):
    model = Request
    # paginate_by = 10
    template_name = "requests.html"

    def get_queryset(self):
        return Request.objects.filter(employeeID=self.request.user.username)
