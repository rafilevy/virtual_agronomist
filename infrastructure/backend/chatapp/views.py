from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status, serializers, mixins
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import models
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from .pipeline import shared_pipeline
from .models import PreTrainingData
import json
import os
from atomicwrites import atomic_write


def index(request):
    return render(request, 'chatapp/index.html', context={})


@login_required
def insights(request):
    return render(request, 'chatapp/admin.html', context={})


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class DebugabbleView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication) if settings.DEBUG else (
        SessionAuthentication, BasicAuthentication)


def get_training_response():
    return Response({
        "training": shared_pipeline.trainer.training,
        "count": PreTrainingData.objects.filter(seen=True).count(),
        "round": shared_pipeline.trainer.round - 1
    })


class FeedbackView(DebugabbleView):
    permission_classes = (IsAdminUser,)

    def get(self, request, format='json'):
        out = {"data": []}
        for pretrain_object in PreTrainingData.objects.filter(seen=False)[:10]:
            user_data = json.loads(pretrain_object.user_data)
            out["data"].append({"key": pretrain_object.pk, **user_data})
        return Response(out)

    def post(self, request, format='json'):
        try:
            new_choice = int(request.data["choice"])
            obj = PreTrainingData.objects.get(id=int(request.data["key"]))
            user_data = json.loads(obj.user_data)
            user_data["choice"] = new_choice
            obj.user_data = json.dumps(user_data)
            obj.seen = True
            obj.save()
        except:
            pass
        return get_training_response()

    def delete(self, request):
        try:
            obj = PreTrainingData.objects.get(id=int(request.body))
            obj.delete()
        except:
            pass
        return get_training_response()


class TrainView(DebugabbleView):
    permission_classes = (IsAdminUser,)

    def get(self, request, format='json'):
        return get_training_response()

    def post(self, request, format='json'):
        try:
            objs = PreTrainingData.objects.filter(seen=True).all()
            assert len(objs) > 0
            shared_pipeline.trainer.train(objs)
        except Exception as e:
            print(str(e))
            pass
        return get_training_response()


class ReLoadDocumentsView(DebugabbleView):
    permission_classes = (IsAdminUser,)

    def post(self, request, format='json'):
        try:
            shared_pipeline.re_process_documents()
        except Exception as e:
            print(str(e))
            pass
        return Response("OK!", status=status.HTTP_201_CREATED)


class DataUpdateView(DebugabbleView):
    permission_classes = (IsAdminUser,)

    def post(self, request, format='json'):
        def update_file(filename, f):
            if f not in request.FILES:
                return
            with atomic_write(filename, mode='wb+', overwrite=True) as destination:
                for chunk in request.FILES[f].chunks():
                    destination.write(chunk)

        update_file('knowledgeBase/english_contractions.json', "parser")
        update_file('knowledgeBase/pressure_score.csv', 'pressure_score')
        update_file('knowledgeBase/categories.csv', 'categories')
        shared_pipeline.question_generator.update_components()
        return Response("OK!", status=status.HTTP_201_CREATED)


class DocumentWrapper(models.Model):
    name = models.TextField()
    is_table = models.BooleanField()
    index = models.IntegerField()


class DocumentWrapSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField('get_obj_url')
    name = serializers.CharField(read_only=True)
    is_table = serializers.BooleanField(read_only=True)
    index = serializers.IntegerField(read_only=True)

    class Meta:
        model = DocumentWrapper
        fields = ("index", "name", "is_table", "url")
        lookup_field = "index"

    def get_obj_url(self, obj):
        path = "table" if obj.is_table else "document"
        return f'data/{path}/{obj.index}/'


class DocumentWrapDetailSerializer(DocumentWrapSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = DocumentWrapper
        fields = ("index", "name", "is_table", "files")
        lookup_field = "index"

    def get_files(self, obj):
        path = "tables" if obj.is_table else "text"
        out = [f'static/{path}/{obj.name}']
        if obj.is_table:
            extra = obj.name.replace('.csv', '.txt')
            out.append(f'static/{path}/{extra}')
        return out


class TableListView(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication) if settings.DEBUG else (
        SessionAuthentication, BasicAuthentication)
    serializer_class = DocumentWrapSerializer
    detail_serializer_class = DocumentWrapDetailSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = "index"

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'detail_serializer_class'):
                return self.detail_serializer_class

        return super().get_serializer_class()

    def get_queryset(self):
        tables = [file for file in os.listdir(
            "knowledgeBase/tables") if ".csv" in file]
        return [DocumentWrapper(name=file, index=i, is_table=True) for (i, file) in enumerate(tables)]

    def get_object(self):
        queryset = self.get_queryset()
        return queryset[int(self.kwargs["index"])]

    def create(self, request):
        def update_file(filename, f):
            if f not in request.FILES:
                return
            name = request.FILES["csv"].name.replace(".csv", "")
            f_obj = request.FILES[f]
            with atomic_write(f'{filename}/{name}.{f}', mode='wb+', overwrite=True) as destination:
                for chunk in f_obj.chunks():
                    destination.write(chunk)
        update_file('knowledgeBase/tables', "csv")
        update_file('knowledgeBase/tables', "txt")
        return Response("OK!", status=status.HTTP_201_CREATED)

    def destroy(self, request, index=None):
        queryset = self.get_queryset()
        obj = queryset[int(index)]
        try:
            os.remove(f'knowledgeBase/tables/{obj.name}')
            extra = obj.name.replace('.csv', '.txt')
            os.remove(f'knowledgeBase/tables/{extra}')
        except:
            pass
        return Response("OK!", status=status.HTTP_204_NO_CONTENT)


class DocumentListView(TableListView):
    def get_queryset(self):
        docs = [file for file in os.listdir(
            "knowledgeBase/text") if ".txt" in file]
        return [DocumentWrapper(name=file, index=i, is_table=False) for (i, file) in enumerate(docs)]

    def create(self, request):
        def update_file(filename, f):
            if f not in request.FILES:
                return
            f_obj = request.FILES[f]
            with atomic_write(f'{filename}/{f_obj.name}', mode='wb+', overwrite=True) as destination:
                for chunk in f_obj.chunks():
                    destination.write(chunk)
        update_file('knowledgeBase/text', "file")
        return Response("OK!", status=status.HTTP_201_CREATED)

    def destroy(self, request, index=None):
        queryset = self.get_queryset()
        obj = queryset[int(index)]
        try:
            os.remove(f'knowledgeBase/text/{obj.name}')
        except:
            pass
        return Response("OK!", status=status.HTTP_204_NO_CONTENT)
