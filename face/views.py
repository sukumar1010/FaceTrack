from django.shortcuts import render,redirect
from django.contrib.auth import login, logout
import rest_framework
from rest_framework.views import APIView
from .forms import loginOrRegister,UpdatePasswordForm
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer,AttendanceSerializer,AttendanceMarkSerializer,UpdatePasswordSerializer,AdminLoginSerializer
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Attendance,Users,FaceProfile
from django.contrib.auth.decorators import login_required
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import time
from django.utils import timezone
import numpy as np
from deepface import DeepFace
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
import cv2
from django.views.decorators.cache import never_cache
from django.http import Http404

DeepFace.build_model('Facenet512')

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    

def loginn(request):
    form = loginOrRegister()
    return render(request,'login.html',{'form':form})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        password_change_required = False
        
        if user.check_password(settings.DEFAULT_USER_PASSWORD):
            password_change_required = True

        
        tokens = get_tokens_for_user(user)
        login(request, user)

        return Response(
            {"tokens": tokens,'password_change_required':password_change_required},
            
            status=status.HTTP_200_OK
        )
    


@login_required(login_url="show_login")
def update_password_view(request):
    if request.method == "POST":
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()

            
            return redirect("show_login")
    else:
        form = UpdatePasswordForm()

    return render(request, "update_password.html", {"form": form})

@never_cache
@login_required(login_url='show_login')
def home(request):
    return render(request, 'home.html')




@method_decorator(login_required(login_url='show_login'), name='dispatch')
class UserDashboardAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        if "HTTP_AUTHORIZATION" not in request.META:
            raise Http404

        user = request.user

        attendances = Attendance.objects.filter(
            user=user
        ).order_by("-date_time")

        serializer = AttendanceSerializer(attendances, many=True)

        return Response({
            "is_authenticated": True,
            "user": user.email,
            "attendance": serializer.data
        })


def logout_view(request):
    logout(request)
    return redirect("show_login")



def cosine_similarity(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

from PIL import Image
import io



class MarkAttendanceAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = AttendanceMarkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data["image"]

        # ⏰ Time restriction
        # now = timezone.localtime().time()
        # print("_____________________________",now)
        # if not (time(8, 0) <= now <= time(11, 0)):
        #     return Response(
        #         {"status": "time_not_allowed"},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        # 📸 Extract face embedding
        try:
            image = serializer.validated_data["image"]

            file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
           
            
            captured_embedding = DeepFace.represent(
                img_path=img,
                model_name="Facenet512",
                detector_backend="opencv",
                enforce_detection=True
            )[0]["embedding"]
        except Exception:
            return Response(
                {"message": "no_face_detected"},
                status=status.HTTP_400_BAD_REQUEST
            )

        THRESHOLD = 0.6
        best_score = 0
        matched_user = None

        # 🔍 Compare against all stored faces
        for profile in FaceProfile.objects.select_related("user"):
            score = cosine_similarity(profile.embedding, captured_embedding)
            # print("Similarity:", score, "User:", profile.user.email)

            if score > best_score:
                best_score = score
                matched_user = profile.user

        if best_score < THRESHOLD:
            return Response(
                {"status": "face_not_matched"},
                status=status.HTTP_200_OK
            )

        # 📅 Prevent duplicate attendance
        today = timezone.localdate()
        if Attendance.objects.filter(
            user=matched_user,
            date_time__date=today
        ).exists():
            return Response(
                {"status": "already_marked","email": matched_user.email,},
                status=status.HTTP_200_OK
            )

        # ✅ Mark attendance
        Attendance.objects.create(
            user=matched_user,
            is_present=True
        )

        return Response(
            {
                "status": "present",
                "email": matched_user.email,
                "confidence": round(best_score, 3)
            },
            status=status.HTTP_201_CREATED
        )


        
class AdminEnrollUserAPIView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        email = request.data.get("email")
        image = request.FILES.get("image")

        if not email or not image:
            return Response(
                {"message": "Email and face image are required"},
                status=400
            )

        # 1️⃣ Create user (or get if exists)
        if Users.objects.filter(email=email).exists():
            return Response({
            "email": email,
        }, status=400)

        # ✅ STEP 2: Create user
        user = Users.objects.create(
            email=email,
            password=make_password(settings.DEFAULT_USER_PASSWORD),
            is_active=True
        )
        
        file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        try:
            embedding = DeepFace.represent(
                img_path=img,
                model_name="Facenet512",
                detector_backend="opencv",
                enforce_detection=True
            )[0]["embedding"]
        except Exception as e:
            return Response(
                {"message": "Face processing failed"},
                status=400
            )
        # 3️⃣ Store / update face profile
        
        FaceProfile.objects.update_or_create(
            user=user,
            defaults={"embedding": embedding}
        )

        return Response({
            "message": "User created and face enrolled successfully",
            "email": user.email,
            "default_password": settings.DEFAULT_USER_PASSWORD
        }, status=201)
        
        

def adminLoginPage(request):
    form = loginOrRegister()
    return render(request,'adminLogin.html',{'form':form})


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data

        # 🔐 Create session
        login(request, user)

        return Response(
            {"message": "Admin login successful"},
            status=status.HTTP_200_OK
        )


@login_required(login_url='adminLoginPage')
def adminDashboard(request):
    return render(request, 'adminDashboard.html',{'adminUserId':request.user})


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {"message": "Admin logged out successfully"},
            status=status.HTTP_200_OK
        )