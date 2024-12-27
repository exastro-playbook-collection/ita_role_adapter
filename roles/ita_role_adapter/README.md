# Ansible Role: setup_paragen

## Trademarks

* Linuxは、Linus Torvalds氏の米国およびその他の国における登録商標または商標です。
* RedHat、RHEL、CentOSは、Red Hat, Inc.の米国およびその他の国における登録商標または商標です。
* Windows、PowerShellは、Microsoft Corporation の米国およびその他の国における登録商標または商標です。
* Ansibleは、Red Hat, Inc.の米国およびその他の国における登録商標または商標です。
* pythonは、Python Software Foundationの登録商標または商標です。
* NECは、日本電気株式会社の登録商標または商標です。
* その他、本ロールのコード、ファイルに記載されている会社名および製品名は、各社の登録商標または商標です。

## Description

本ロールではパラメータ生成共通部品を指定したAnsibleサーバーにインストールします。

パラメータ生成共通部品とは、収集ロールを利用するために必要となるモジュールで以下機能を有します。
1. 構築済みサーバーから収集した設定情報から必要な値を抽出する
2. 抽出した値をパラメータ変数とマッピング（Key/Value）する
3. マッピングしたパラメータをYAML形式で出力する

### Notes

AnsibleサーバーにPython2、Python3を両方ともインストールしている環境で本Roleを利用してインストールすると、ansibleが動作するPythonとパラメータ生成共通部品インストール先Pythonが食い違ってしまい、正しく動作しない場合があります  
上記のような環境では本Roleでインストール後、以下の方法で正しくパラメータ共通部品がインストールされているかご確認ください  

* インストール状況確認手順  
1. ansible --version を実行し、ansibleが動作しているPythonがPython2かPython3かを確認する  
2. Python2の場合はpip2 list、Python3の場合はpip3 listを実行し、parametergenerateパッケージが存在することを確認する  
3. ansibleが動作しているPythonパッケージにparametergenerateが存在しなかった場合、以下の手動インストール手順でインストールを行ってください  

* 手動インストール手順  
1. Ansibleサーバーでカレントフォルダを以下に移動  
   <setup_paragenロールフォルダ>/files/  
2. 以下コマンドを実行（既に存在している場合は上書きコピー）  
    sudo mkdir -p /usr/share/ansible/plugins/action/  
    sudo cp action_plugins/parameter_generate.py /usr/share/ansible/plugins/action/parameter_generate.py  
3. 以下コマンドを実行  
    - ansibleがPython2で動作している場合  
        sudo pip2 install parametergenerate/  
    - ansibleがPython3で動作している場合  
        sudo pip3 install parametergenerate/  

## Supports

パラメータ生成共通部品は以下環境での動作をサポートします。

- Ansibleサーバー（本ロールのインストール先）
  - OS：RHEL7.5（CentOS7.5）
  - Ansible：Version 2.7
  - Python：2.7 or 3.6
- 対象ホスト側（パラメータ生成共通部品の解析対象）
  - 利用する収集ロールに準拠します

## Requirements

* 本ロールではインストール先にあらかじめAnsibleがインストールされている必要があります。
* 本ロールはインストール先のsudo実行権限を持つユーザーで実行する必要があります。

## Role Variables

無し

## Dependencies

無し

## Example

* Playbook
    ```
    ---
    - hosts: local
      become: yes
      roles:
        - setup_paragen
    ```
* Inventory
    ```
    [local]
    localhost

    [local:vars]
    ansible_python_interpreter=/usr/bin/python3
    ansible_become_pass=<sudoパスワード>
    ```
    (*) AnsibleをPython2で動作させる場合、ansible_python_interpreterの定義は不要

* Command
    ```
    ansible-playbook -c local -i <Inventory> <Playbook>
    ```

## License

Apache License 2.0

## Author Information

None

