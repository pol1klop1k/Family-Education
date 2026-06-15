import base64
import io
import subprocess


from django.db.models import OuterRef, Subquery
from django.contrib.auth import authenticate, login
from django.middleware.csrf import get_token
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.renderers import JSONRenderer
from PIL import Image
import requests
import cv2
import numpy as np

from accounting.models import AccountingList
from registration.api import prompts
from registration.api.serializers import (
    AccountingListSerializer,
    AccountingUpdateSerializer,
    DocumentSerializer,
    ExtractDataFromScanSerializer,
    LoginSerializer,
    NotificationCreateSerializer,
    NotificationSerializer,
    NotificationUpdateSerializer,
    SchoolSerializer,
    StudentRetrieveSerializer,
    StudentsListSerializer,
    UploadDocumentSerializer, 
    UserSerializer,
)
from registration.api.renderers import JPEGRenderer
from registration.models import (
    Child,
    DocumentScan,
    Notification,
    School,
)


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is not None:
            login(request, user)
            get_token(request)
            return Response({"detail": "success"})
        return Response(
            {"detail": "Не удалось авторизоваться"},
            status=status.HTTP_403_FORBIDDEN,
        )


class MeView(APIView):
    
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    

class SchoolListView(APIView):

    def get(self, request, *args, **kwargs):
        qs = School.objects.all()
        serializer = SchoolSerializer(qs, many=True)
        return Response(serializer.data)
    

class StudentsListView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = StudentsListSerializer

    def get_queryset(self):
        return (Notification.objects
                .select_related(
                    "student",
                    "applicant",
                    "representative",
                )
                .distinct("student")
                .order_by(
                    "-student_id",
                    "-date",
                )
                )


class StudentRetrieveView(RetrieveAPIView):

    serializer_class = StudentRetrieveSerializer

    def get_object(self):
        return Notification.objects.filter(student_id=self.kwargs["pk"]).latest("-date")


class NotificationView(ListAPIView):

    queryset = Notification.objects.all()

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(student_id=kwargs["pk"])
        serializer = NotificationSerializer(qs, many=True)
        return Response(serializer.data)
    

class UpdateNotificationView(UpdateAPIView):

    queryset = Notification.objects.all()
    serializer_class = NotificationUpdateSerializer


class DocumentsListView(ListAPIView):

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("child_id",)
    queryset = DocumentScan.objects.all()
    serializer_class = DocumentSerializer


class NotificationCreateView(CreateAPIView):

    serializer_class = NotificationCreateSerializer

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs, context={"employee": self.request.user})


def get_device():
    result = subprocess.run(["scanimage", "-L"], capture_output=True, text=True)
    if result.returncode != 0 or "device `" not in result.stdout:
        raise Exception("Не найден подключенный сканер.")
    return result.stdout.split("`")[1].split("'")[0]


def trigger_scan():
    device = get_device()
    if device is None:
        return

    cmd = [
        "scanimage",
        "--device=" + device,
        "--format=pnm",
        "--mode=Color",
        "--resolution=300"
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"Ошибка сканирования: {proc.stderr.decode().strip()}")

    img = Image.open(io.BytesIO(proc.stdout))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()
    buffer.close()

    return image_bytes


def order_points(pts):
    """Упорядочиваем 4 точки: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    """Применяем перспективную трансформацию к найденному контуру"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    # Вычисляем ширину и высоту нового изображения
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    
    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))
    
    # Точки назначения для трансформации
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    
    # Матрица трансформации и применение
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def crop_document(image_bytes, padding=20, min_area_ratio=0.3):
    """
    Находит документ на скане, выравнивает и обрезает фон.
    
    :param image_bytes: байты изображения (JPG/PNG)
    :param padding: отступ в пикселях от края найденного документа
    :param min_area_ratio: минимальная площадь контура относительно изображения (от 0 до 1)
    :return: байты обработанного изображения
    """
    # Конвертируем bytes -> numpy array -> BGR
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Не удалось декодировать изображение")
    
    orig = img.copy()
    ratio = img.shape[0] / 500.0  # Масштабируем для скорости обработки
    img_resized = cv2.resize(img, (int(img.shape[1] / ratio), 500))
    
    # Предобработка: размытие + адаптивный порог (лучше работает при неравномерном свете)
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Адаптивный порог: документ станет белым, фон чёрным (или наоборот)
    thresh = cv2.adaptiveThreshold(blurred, 255, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Поиск контуров
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    min_area = img_resized.shape[0] * img_resized.shape[1] * min_area_ratio
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
            
        # Аппроксимация полигоном (ищем прямоугольник)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        # Если нашли 4 угла — вероятно, это документ
        if len(approx) == 4:
            # Трансформируем точки обратно к оригинальному размеру
            pts = approx.reshape(4, 2).astype("float32")
            pts *= ratio
            warped = four_point_transform(orig, pts)
            
            # Добавляем небольшой отступ (чтобы не обрезать текст по краю)
            h, w = warped.shape[:2]
            warped = warped[padding:h-padding, padding:w-padding]
            
            # Конвертируем BGR -> RGB -> PIL -> bytes
            result_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(result_rgb)
            buf = io.BytesIO()
            pil_img.save(buf, format="JPEG", quality=90)
            return buf.getvalue()
    
    return image_bytes


class ScanView(APIView):
    renderer_classes = [JPEGRenderer, JSONRenderer]

    def post(self, request, *args, **kwargs):
        try:
            image_bytes = trigger_scan()
            cropped_bytes = crop_document(image_bytes)
        except Exception as e:
            raise APIException(e)
        return Response(
            cropped_bytes,
            content_type='image/jpeg',
        )
    
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if response.exception:
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
        return response
    

class UploadScanView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UploadDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        child = Child.objects.get(pk=kwargs["pk"])
        scan = DocumentScan.objects.create(
            file=data["doc"],
            child=child,
            name=data["name"],
        )
        return Response("success")


def resize_image(img_bytes, max_size=700):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    return buf.getvalue()

def extract_id_data(img_bytes: bytes,
                    doc_type: str,
                    model="qwen2.5vl:7b"):
    # Чтение и кодирование изображения
    sampled_image = resize_image(img_bytes)
    img_b64 = base64.b64encode(sampled_image).decode()

    # Промпт для извлечения данных
    if doc_type == "person":
        prompt = prompts.EXTRACT_ID
    elif doc_type == "location":
        prompt = prompts.EXTRACT_LOCATION

    # Запрос к Ollama API
    response = requests.post(
        "http://host.docker.internal:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False,
        }
    )
    return response.json()["response"]


@api_view(["POST"])
def extract_data_from_doc(request, *args, **kwargs):
    serializer = ExtractDataFromScanSerializer(data=request.data)
    serializer.is_valid()
    img_bytes = base64.b64decode(serializer.validated_data["doc_data"])
    response = extract_id_data(img_bytes, serializer.validated_data["data_type"])
    return Response(response)

counter = 0

@api_view(["POST"])
def mock_extract_data(request, *args, **kwargs):
    serializer = ExtractDataFromScanSerializer(data=request.data)
    serializer.is_valid()
    if serializer.validated_data["data_type"] == "person":
        global counter
        counter += 1
        return Response(
            [
            {
                "surname": "Батрак",
                "name": "Игорь",
                "patronymic": "Витальевич",
                "birth_year": "19.10.2004"
            },
            {
                "surname": "Пряжникова",
                "name": "Татьяна",
                "patronymic": "Олеговна",
                "birth_year": "30.09.2004"
            }
            ][counter % 2]
        )

    return Response(
            [
            {
                "location": "мачуги, даунидзе",
            },
            {
                "location": "щенячий ключ, отходная",
            }
            ][counter % 2]
        )


class AccountingView(ListAPIView):
    serializer_class = AccountingListSerializer

    def get_queryset(self):
        qs = AccountingList.objects.select_related("child", "school")
        notifications = (Notification.objects
                         .filter(student_id__in=(i.child.id for i in qs))
                         .distinct("student_id")
                         .order_by("-student_id", "-date")
                         .in_bulk(field_name="student_id")
                         )
        for i in qs:
            i.notification = notifications.get(i.child.pk)
        return qs
        

class AccountingUpdateView(UpdateAPIView):
    queryset = AccountingList.objects.all()
    serializer_class = AccountingUpdateSerializer
