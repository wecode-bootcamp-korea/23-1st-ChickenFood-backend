import json
import re
import bcrypt
import jwt

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Q

from chickenfood.settings import SECRET_KEY
from members.models       import Member
from members.utils        import login_decorator

class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)
            
        if not (data.get('name') and data.get('email') and data.get('password') and data.get('phone_number')):
            return JsonResponse({"message": "KEY_ERROR"}, status=400)
            
        data['phone_number'] = data['phone_number'].replace("-", "")

        if not (re.match('^(?=.*[a-zA-Z]+).{1,}$', data['name']) and
                    re.match('^\w+@\w+\.\w+$', data['email']) and
                    re.match('\S{8,}', data['password']) and
                    re.match('\d{10,11}', data['phone_number'])):
            return JsonResponse({"message": "INVALID_FORMAT"}, status=400)
 
        if data.get('recommender'):
            if not Member.objects.filter(name=data.get('recommender')).exists():
                return JsonResponse({"message": "INVALID_RECOMMENDER"}, status=400)
            recommender = Member.objects.get(name=data.get('recommender'))
        else:
            recommender = None

        q = Q(name=data['name']) | Q(email=data['email']) | Q(phone_number=data['phone_number'])

        if Member.objects.filter(q).exists():
            return JsonResponse({"message": "EXIST_MEMBER"}, status=400)

        Member.objects.create(
                name         = data['name'],
                email        = data['email'],
                password     = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                phone_number = data['phone_number'],
                address      = data.get('address'),
                recommender  = recommender
        )

        return JsonResponse({"message": "SUCCESS"}, status=201)

class SignInView(View):
    def post(self, request):
        data = json.loads(request.body)

        if not (data.get('member') and data.get('password')):
            return JsonResponse({"message": "KEY_ERROR"}, status=401)

        member = data['member'].replace("-", "")
 
        q = Q(name=member) | Q(phone_number=member)

        if not Member.objects.filter(q).exists():
            return JsonResponse({"message": "INVALID_MEMBER"}, status=401)

        if not bcrypt.checkpw(data['password'].encode('utf-8'), Member.objects.get(q).password.encode('utf-8')):
            return JsonResponse({"message": "INVALID_MEMBER"}, status=401)
 
        token = jwt.encode({'id': Member.objects.get(q).id}, SECRET_KEY, algorithm='HS256')

        return JsonResponse({"message": "SUCCESS", "token": token}, status=200)

class MemberCheckView(View):
    def post(self, request):
        data = json.loads(request.body)
        
        if not data.get('name'):
            return JsonResponse({"message": "KEY_ERROR"}, status=400)
        
        if Member.objects.filter(name=data.get('name')).exists():
            return JsonResponse({"message": "EXIST_MEMBER"}, status=400)

        return JsonResponse({"message": "SUCCESS"}, status=200)

class MemberView(View):
    @login_decorator
    def get(self, request):
        information = {
            "id"             : request.member.id,
            "name"           : request.member.name,
            "email"          : request.member.email,
            "phone_number"   : request.member.phone_number,
            "address"        : request.member.address,
            "recommender_id" : request.member.recommender
        }
        return JsonResponse({"result": information}, status=200)
