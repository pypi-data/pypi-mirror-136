# file-retention
CLI para retenção de arquivos com base em qualquer data 

Como instalar:
~~~
python3 -m pip install --upgrade pip
python3 -m pip install file_retention
~~~

Como utilizar:

Primeiro é necessário executar com o comando install para 
criar os diretórios e arquivos de configuração necessários
~~~
python3 -m file_retention install
~~~

Tirar um snapshot dos arquivos recursivamente:
~~~
python3 -m file_retention snapshot /tmp/create_files/ -e ini
~~~

Deletar os arquivos:
~~~
python3 -m file_retention delete -r 15 -y
~~~


Enviar e-mail:
~~~
python3 -m file_retention mail ~/.file_retention/mail.yml -r 15
~~~

Para mais informaões:
~~~
python3 -m file_retention --help
python3 -m file_retention snapshot --help
python3 -m file_retention mail --help
python3 -m file_retention delete --help
~~~
