
"""
django-t2s -- a very simple usage django utility for t2s

Copyright (C) 2014 - Yorkie, Firmus Asia
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of the libEtPan! project nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.
 *
THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""

from django.db import models
from django.db.models.fields import CharField
from django.contrib import admin
from ckeditor.fields import RichTextField
from lang import SUPPORTED_LANG, is_traditional
from opencc import convert


class Model(models.Model):
  """
  T2S Extension Class
  Usage:
    class YourModel(t2s.Model):
      ...
  """
  lang = models.IntegerField(default=1, choices=SUPPORTED_LANG)

  def getLanguageDisplay(self):
    return SUPPORTED_LANG[self.lang][1]

  @classmethod
  def getFields(cls):
    return cls._meta.fields

  @classmethod
  def cloneWithSimplified(cls, **kwargs):
    """
    XXX(Yorkie): currently cannot filter the invalid field, will
    support later.

    Description:
    XX.cloneWithSimplified(title=1, name=2)
    if XX doesn't define title filed, now it(program) will breaks,
    if we support the filter, this error will be ignored.
    """
    fields = {}
    for name, value in kwargs.items():
      fields[name] = convert(value)
    fields['lang'] = 2
    inst, r = cls.objects.get_or_create(**fields)
    # inst.save()
    return r

  class Meta:
    abstract = True


class ModelAdmin(admin.ModelAdmin):
  """
  T2S ModelAdmin Class
  Just set `modifyDate` and `createDate` related stuffs
  Usage:
  class YourModelAdmin(t2s.ModelAdmin):
    ...
  """
  def __init__(self, model, admin_site):
    self.coverCondition = False
    self._modifyDate = None
    self._createDate = None
    self._hasModifyDate = False
    self._hasCreateDate = False
    self._textFields = []

    for field in model.getFields():
      if not self._hasModifyDate:
        self._hasModifyDate = (field.name == 'modify_date' or field.name == 'modifyDate')
      if not self._hasCreateDate:
        self._hasCreateDate = (field.name == 'create_date' or field.name == 'createDate')
      if type(field) is CharField or type(field) is RichTextField:
        self._textFields.append(field.name)
    self.coverCondition = self._hasModifyDate and self._hasCreateDate;
    super(ModelAdmin, self).__init__(model, admin_site)


  """
  Override `save_model`
  """
  def save_model(self, request, obj, form, change):
    model = self.model
    lang = form.cleaned_data.get('lang')
    fields = {}
    for name in self._textFields:
      text = form.cleaned_data.get(name)
      setattr(obj, name, convert(text, config='s2t'))
      fields[name] = text

    if is_traditional(lang):
      model.cloneWithSimplified(**fields)
    return super(ModelAdmin, self).save_model(request, obj, form, change)

  class Meta:
    abstract = True
