#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sys
import yaml
import io
from importlib import import_module

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError

try:
  from __main__ import display
except ImportError:
  from ansible.utils.display import Display
  display = Display()

# YAML可読性向上のためアンカーとエイリアスを無効化
class NoAliasDumper(yaml.Dumper):
  def ignore_aliases(self, data):
    return True


####################################################
class ActionModule(ActionBase):
  ita_role_adpater_prep_main = None
  ita_role_adpater_post_main = None
  ita_role_adpater_prep_dict = None
  ita_role_adpater_post_dict = None
  ita_role_adpater_prep_list = None
  ita_role_adpater_post_list = None
  ita_role_adpater_task_vars = {}

  ####################################################
  # Action Plugin メイン関数
  def run(self, tmp=None, task_vars=None):
    # お約束
    if task_vars is None:
        task_vars = dict()
    result = super(ActionModule, self).run(tmp, task_vars)
    if self._play_context.check_mode:
        result['skipped'] = True
        result['msg'] = "skipped, this module does not support check_mode."
        return result

    # パラメータ取込み
    paramname = self._task.args.get('paramname', None)
    paramdata = self._task.args.get('paramdata', None)
    addinsdir = self._task.args.get('addinsdir', None)

    # パラメータチェック
    if paramname is None or paramdata is None:
        result['failed'] = True
        result['msg'] = "paramname and paramdata is required."
        return result

    # タスク変数取込み
    for temp in task_vars:
      if temp.startswith('VAR_') or \
         temp.startswith('i_')   or \
         temp.startswith('__')   or \
         temp == 'inventory_hostname':
        self.ita_role_adpater_task_vars[temp] = task_vars[temp]

    # 個別処理用関数定義
    if addinsdir:
      if addinsdir[-1:] == "/":
        addinsdir = addinsdir[:-1]
      sys.path.append(addinsdir)

      # addins.py をインポート、無ければエラー
      try:
        temp = import_module("addins")
      except ModuleNotFoundError:
        result['failed'] = True
        result['msg'] = 'Error: no addins.py in {}'.format(addinsdir)
        return result

      # addins.py に関数が定義されていれば読込み、無ければ空の無名関数を定義
      try:
        self.ita_role_adpater_prep_main = getattr(temp, 'prep_main')
      except AttributeError:
        display.verbose("Not use prep_main", caplevel=2)
        self.ita_role_adpater_prep_main = lambda key, value, task_vars : (value, None)

      try:
        self.ita_role_adpater_post_main = getattr(temp, 'post_main')
      except AttributeError:
        display.verbose("Not use post_main", caplevel=2)
        self.ita_role_adpater_post_main = lambda key, value, task_vars : (value, None)

      try:
        self.ita_role_adpater_prep_dict = getattr(temp, 'prep_dict')
      except AttributeError:
        display.verbose("Not use prep_dict", caplevel=2)
        self.ita_role_adpater_prep_dict = lambda key, value, task_vars : (value, None)

      try:
        self.ita_role_adpater_post_dict = getattr(temp, 'post_dict')
      except AttributeError:
        display.verbose("Not use post_dict", caplevel=2)
        self.ita_role_adpater_post_dict = lambda key, value, task_vars : (value, None)

      try:
        self.ita_role_adpater_prep_list = getattr(temp, 'prep_list')
      except AttributeError:
        display.verbose("Not use prep_list", caplevel=2)
        self.ita_role_adpater_prep_list = lambda key, value, task_vars : (value, None)

      try:
        self.ita_role_adpater_post_list = getattr(temp, 'post_list')
      except AttributeError:
        display.verbose("Not use post_list", caplevel=2)
        self.ita_role_adpater_post_list = lambda key, value, task_vars : (value, None)

    else:
      # addinsdir が未指定ならすべて空の無名関数を定義
      self.ita_role_adpater_prep_main = lambda key, value, task_vars : (value, None)
      self.ita_role_adpater_post_main = lambda key, value, task_vars : (value, None)
      self.ita_role_adpater_prep_dict = lambda key, value, task_vars : (value, None)
      self.ita_role_adpater_post_dict = lambda key, value, task_vars : (value, None)
      self.ita_role_adpater_prep_list = lambda key, value, task_vars : (value, None)
      self.ita_role_adpater_post_list = lambda key, value, task_vars : (value, None)

    # ITAで実行時、user_filesフォルダ配下に変換前の収集データを出力
    if '__workflowdir__' in self.ita_role_adpater_task_vars:
      temp = self.ita_role_adpater_task_vars['__workflowdir__'] + "/" + paramname + "_ita.tmp"
      os.makedirs(self.ita_role_adpater_task_vars['__workflowdir__'] ,exist_ok=True)
      with io.open(temp, 'wb') as fp:
        fp.write(yaml.dump(
          {paramname+"_ITA":paramdata},
          Dumper=NoAliasDumper,
          allow_unicode=True,
          encoding='utf-8',
          default_flow_style=False,
          explicit_start=True,
          width=10000
        ))

    # 変換処理実行開始
    try:
      paramdata = self.convert_entry(paramname, paramdata)
    except:
      import traceback
      result['failed'] = True
      result['msg'] = traceback.format_exc()
      return result

    # ITAで実行時、user_filesフォルダ配下に変換後の収集データを出力
    if '__workflowdir__' in self.ita_role_adpater_task_vars:
      temp = self.ita_role_adpater_task_vars['__workflowdir__'] + "/" + paramname + "_org.tmp"
      os.makedirs(self.ita_role_adpater_task_vars['__workflowdir__'] ,exist_ok=True)
      with io.open(temp, 'wb') as fp:
        fp.write(yaml.dump(
          {paramname:paramdata},
          Dumper=NoAliasDumper,
          allow_unicode=True,
          encoding='utf-8',
          default_flow_style=False,
          explicit_start=True,
          width=10000
        ))

    return dict(paramdata=paramdata)

  ####################################################
  # 変換処理の入口
  def convert_entry(self, key, src):
    dst = None
    temp = src

    # 個別処理 prep_main を呼び出し
    temp, flag = self.ita_role_adpater_prep_main(key, temp, self.ita_role_adpater_task_vars)

    # 終了時ステータスが process_skip であればデータ出力をスキップ
    if flag == 'process_skip':
      return dst

    # 終了時ステータスが convert_skip であれば共通の変換処理をスキップ
    if flag != 'convert_skip':
      # 変換メイン関数の呼び出し
      temp = self.convert_main(key, temp)

    # post_mainが定義されていれば呼び出し
    temp, flag = self.ita_role_adpater_post_main(key, temp, self.ita_role_adpater_task_vars)

    # 終了時ステータスが process_skip であればデータ出力をスキップ
    if flag == 'process_skip':
      return dst

    # 値を追加
    dst = temp

    return dst

  ####################################################
  # 変換処理の本体
  def convert_main(self, key, src):

    # 辞書の処理
    if isinstance(src, dict):
      dst = {}
      for key in src:
        temp = src[key]

        # 個別処理 prep_dict を呼び出し
        temp, flag = self.ita_role_adpater_prep_dict(key, temp, self.ita_role_adpater_task_vars)

        # 終了時ステータスが process_skip であればデータ出力をスキップ
        if flag == 'process_skip':
          continue

        # undefined扱いのnullをスキップ
        # （必要なnullをスキップしないよう、共通変換処理前に配置が必須）
        if isinstance(temp, type(None)):
          continue

        # 終了時ステータスが convert_skip であれば共通の変換処理をスキップ
        if flag != 'convert_skip':
          # 配下の要素を処理するため再帰呼び出し
          temp = self.convert_main(key, temp)

        # 個別処理 post_dict を呼び出し
        temp, flag = self.ita_role_adpater_post_dict(key, temp, self.ita_role_adpater_task_vars)

        # 終了時ステータスが process_skip であればデータ出力をスキップ
        if flag == 'process_skip':
          continue

        # 中身が空になった辞書はundefined扱いとするためスキップ
        if isinstance(temp, dict) and len(temp) == 0:
          continue

        # 値を追加
        dst[key] = temp

      return dst

    # リストの処理
    if isinstance(src, list):
      dst = []
      for entry in src:
        temp = entry

        # 個別処理 prep_list を呼び出し
        temp, flag = self.ita_role_adpater_prep_list(key, temp, self.ita_role_adpater_task_vars)

        # 終了時ステータスが process_skip であればデータ出力をスキップ
        if flag == 'process_skip':
          continue

        # 終了時ステータスが convert_skip であれば共通の変換処理をスキップ
        if flag != 'convert_skip':
          # 配下の要素を処理するため再帰呼び出し
          temp = self.convert_main(key, temp)

        # 個別処理 post_list を呼び出し
        temp, flag = self.ita_role_adpater_post_list(key, temp, self.ita_role_adpater_task_vars)

        # 終了時ステータスが process_skip であればデータ出力をスキップ
        if flag == 'process_skip':
          continue

        # 中身が空になった辞書はundefined扱いとするためスキップ
        if isinstance(temp, dict) and len(temp) == 0:
          continue

        # 値を追加
        dst.append(temp)

      return dst

    # 値の処理
    if src == '<NULL>':
      # NULL文字列をnullに変換
      dst = None
    else:
      # その他はそのまま返却する
      dst = src

    return dst
