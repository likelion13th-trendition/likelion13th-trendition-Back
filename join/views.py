import logging

from rest_framework import status, generics
from rest_framework.response import Response
from .authentication import BearerTokenAuthentication

from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

# Create your views here.

#회원가입
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

#로그인
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = [BearerTokenAuthentication]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data
        return Response({"token": token.key}, status=status.HTTP_200_OK)


#팔로잉
class FollowView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    def post(self, request, username):
        logging.info(f"Request headers: {request.headers}")
        logging.info(f"User type: {type(request.user)}")

        if request.user.is_authenticated:
            you = get_object_or_404(CustomUser, username=username)  
            me = request.user

            logging.info(f"Before following: {me.following.all()}") # 팔로우 전 following 상태
            if you in me.following.all():
                me.following.remove(you)
                you.follower.remove(me)
                return Response("언팔로우 했습니다.", status=status.HTTP_200_OK)
            else:
                me.following.add(you)
                you.follower.add(me)
                logging.info(f"After following: {me.following.all()}") # 팔로우 후 following 상태
                return Response("팔로우 했습니다.", status=status.HTTP_200_OK)
        else:
            return Response("로그인이 필요한 서비스입니다.", status=status.HTTP_401_UNAUTHORIZED)

#마이페이지
class MyPageView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    def get(self, request):
        if request.user.is_authenticated:
            serializer = MyPageSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response({'error': '로그인이 필요한 서비스입니다.'})
        
#내가 팔로우하는 유저 목록
class FollowingUsersView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    def get(self, request, *args, **kwargs):
        following_users = [user.username for user in request.user.following.all()] 
        return Response(following_users)

#나를 팔로우하는 유저 목록
class FollowerUsersView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    def get(self, request, *args, **kwargs):
        follower_users = [user.username for user in request.user.follower.all()]  
        return Response(follower_users)

#유저 검색
class SearchView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    def get(self, request): 
        keyword = request.query_params.get('keyword')  
        if keyword:
            users = CustomUser.objects.filter(username__icontains=keyword)  
            serializer = MyPageSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "검색어가 없습니다."})
