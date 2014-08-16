
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

from time import gmtime, strftime
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
  update_keys = None

  def getLanguageDisplay(self):
    return SUPPORTED_LANG[self.lang][1]

  def getSimplifiedObject(self):
    """
    if you don't have `title` field or don't want to let this field
    `title` be the key of language exchange, you should overwrite this
    method
    """
    simplifiedTitle = convert(self.title, config='t2s')
    return self.__class__.objects.filter(lang=2, title=simplifiedTitle)[0]

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
    fields = { 'defaults':{} }
    for name, value in kwargs.items():
      val = value
      if type(value) == str or type(value) == unicode:
        val = convert(value, config='t2s')
      try:
        cls.update_keys.index(name)
        fields[name] = val
      except ValueError:
        fields['defaults'][name] = val
      except AttributeError:
        fields[name] = val
    fields['lang'] = 2
    del fields['defaults']['id']
    obj, isNew = cls.objects.get_or_create(**fields)
    
    for name, value in kwargs.items():
      item = getattr(obj, name)
      if isinstance(item, Model):
        setattr(obj, name, item.getSimplifiedObject())
    return (obj, isNew)

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
    self._baseFields = []
    self._richTextFields = []

    for field in model.getFields():
      if not self._hasModifyDate:
        self._hasModifyDate = field.name == 'modify_date'
      if not self._hasCreateDate:
        self._hasCreateDate = field.name == 'create_date'
      if type(field) is RichTextField:
        self._richTextFields.append(field)
      else:
        self._baseFields.append(field)
    self.coverCondition = self._hasModifyDate and self._hasCreateDate;
    super(ModelAdmin, self).__init__(model, admin_site)

  """
  Override `save_model`
  """
  def save_model(self, request, obj, form, change):
    cur_time = gmtime()
    model = self.model
    lang = form.cleaned_data.get('lang')
    fields = {}

    for field in self._baseFields:
      val = form.cleaned_data.get(field.name)
      fields[field.name] = val

    if not lang:
      lang = self.__lang__(form)
    obj.lang = fields['lang'] = lang

    if self._hasModifyDate:
      fields['modify_date'] = strftime("%Y-%m-%d %H:%M:%S", cur_time)
    if self._hasCreateDate:
      fields['create_date'] = strftime("%Y-%m-%d %H:%M:%S", cur_time)

    if is_traditional(lang):
      """
      convert value to simplifiedObj first
      """
      simplifiedObj, isNew = model.cloneWithSimplified(**fields)
      if (not (self._hasModifyDate and
        not isNew and simplifiedObj.modify_date > obj.modify_date)):
        for field in self._richTextFields:
          text = form.cleaned_data.get(field.name)
          setattr(simplifiedObj, field.name, convert(text))
          fields[field.name] = text
        simplifiedObj.save()

      """
      convert value to traditional
      """
      for name, value in fields.items():
        if type(value) == str or type(value) == unicode:
          setattr(obj, name, convert(value, config='s2t'))

    if self._hasModifyDate:
      obj.modify_date = strftime("%Y-%m-%d %H:%M:%S", cur_time)
    if self._hasCreateDate and not obj.create_date:
      obj.create_date = strftime("%Y-%m-%d %H:%M:%S", cur_time)

    return super(ModelAdmin, self).save_model(request, obj, form, change)

  class Meta:
    abstract = True
