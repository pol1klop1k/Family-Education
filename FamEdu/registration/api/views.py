import base64
import io
import subprocess


from django.db.models import OuterRef, Prefetch, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView 
from rest_framework.renderers import JSONRenderer
from PIL import Image
import requests
import cv2
import numpy as np

from registration.api.filters import StudentFilterSet
from registration.api import prompts
from registration.api.serializers import (
    ExtractDataFromScanSerializer,
    NotificationSerializer,
    SchoolSerializer,
    StudentRetrieveSerializer,
    StudentsListSerializer, 
    UserSerializer,
)
from registration.api.renderers import JPEGRenderer
from registration.models import (
    Child,
    Notification,
    School,
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
    filterset_class = StudentFilterSet
    serializer_class = StudentsListSerializer

    def get_queryset(self):
        subq = (Notification.objects
                .filter(
                    student_id=OuterRef("pk"),
                )
                .order_by("-date"))
        q = Child.objects.annotate(
            notification_id=Subquery(subq.values("pk")[:1]),
            grade=Subquery(subq.values("grade")[:1]),
        )
        return q

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        notifications = Notification.objects.in_bulk(
            id_list=[i.notification_id for i in qs],
            field_name="pk",
        )
        for child in qs:
            child.notification = notifications.get(child.notification_id)
        
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class StudentRetrieveView(RetrieveAPIView):

    queryset = Child.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.notification = instance.notifications.latest("date")
        serializer = StudentRetrieveSerializer(instance)
        return Response(serializer.data)


class NotificationView(ListAPIView):

    queryset = Notification.objects.all()

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(student_id=kwargs["pk"])
        serializer = NotificationSerializer(qs, many=True)
        return Response(serializer.data)


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
    
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
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