
from django.shortcuts import redirect
from django.contrib import messages
from django.http.response import JsonResponse
from django.views.generic import TemplateView
from django import forms


class EditableListView(TemplateView):
    model = None
    form_class = None
    template_name = ""
    success_url = ""
    form_new = None
    form_list = []

    def get(self, request, *args, **kwargs):

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # 新規作成フォームの生成
        self.form_new = self.form_class()
        for key in self.form_new.fields.keys():
            self.form_new.fields[key].widget.attrs['id'] = 'id_' + \
                key+"_new"

            # クエリパラメータを初期値にセット
            value = self.request.GET.get(key)
            self.form_new.fields[key].initial = value

            # コンボボックスのQuerySetを各フォームで定義する。
            queryset = self.form_new.get_query(key)
            if queryset is not None:
                self.form_new.fields[key].queryset = queryset

        # リスト用フォームの生成
        self.form_list = []
        for x in self.model.objects.all():
            form = self.form_class(instance=x)
            # 主キー用の非表示コンポーネント
            form.fields['pk'] = forms.IntegerField(
                initial=x.pk, widget=forms.NumberInput({"style": "display:none"}))

            # idを設定
            for key in form.fields.keys():
                form.fields[key].widget.attrs['id'] = 'id_'+key+'_'+str(x.pk)

            self.form_list.append(form)

        context['form_new'] = self.form_new
        context['form_list'] = self.form_list

        return context

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')

        if request.POST.get('action') == 'delete':
            obj = self.model.objects.get(pk=pk)
            obj.delete()

            messages.success(request, "データを削除しました")

            # Deleteの場合、redirectが効かないので、ブラウザ側でリロードする。
            return JsonResponse({'success': True})

        else:
            if pk is None:
                # 新規登録
                try:
                    form = self.form_class(request.POST)

                    if form.is_valid():
                        form.save()
                        messages.success(request, "データを新規に作成しました")

                except ValueError as e:
                    messages.error(request, '項目をすべて入力してください')

                finally:
                    return redirect(self.success_url)

            else:
                # 更新
                obj = self.model.objects.get(pk=pk)
                form = self.form_class(request.POST, instance=obj)

                form.save()

                messages.success(request, "データを更新しました")
                return redirect(self.success_url)
