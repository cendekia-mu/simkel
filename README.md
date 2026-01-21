# Aplikasi LKPJ
Tujuan dari aplikasi LKPJ adalah untuk mengelola data lkpj dengan output berupa 
dokumen pdf.


## Pemasangan

1. Pasang opensipkd-base terlebih dahulu::
```
    $ git clone https://git.opensipkd.com/aa.gusti/opensipkd-base.git
    $ ~/env/bin/pip install opensipkd-base/
```
2. Lalu pasang lkpj.

    Unduh source-nya::

        $ git clone https://git.opensipkd.com/aa.gusti/lkpj.git

    Pasang::

        $ ~/env/bin/pip install lkpj/ 

    Tambahkan  konfigurasi::
    ```
    [main]
    pyramid.includes =
        ...
        lkpj

    [alembic_lkpj]
    script_location = lkpj:alembic
    sqlalchemy.url = postgresql://user:password@server:port/db
    ```

    Inisialisasi database::

        $ ~/env/bin/alembic -c live.ini -n alembic_lkpj upgrade head

3. Jalankan web server::

    $ ~/env/bin/pserve live.ini

Di web browser buka `http://server:port/lkpj <http://server:port/lkpj>`_
 
