# Aplikasi SIKEL
Tujuan dari aplikasi SimKEL adalah untuk mengelola data permohonan masyarakat dengan output berupa 
dokumen pdf.


## A. Pemasangan

### Virtual Environment

Buat Virtual Envirenment baru atau gunakanyang sudah ada ::

### Install Production
1. Instal opensipkd-base
```
    $ pip install git+https://git.opensipkd.com/aa.gusti/opensipkd-base.git 
    atau
    $ pip install git+https://github.com/cendekia-mu/opensipkd-base.git 
```    
2. Install opensipkd-simkel 
```
    $ pip install git+https://github.com/cendekia-mu/simkel.git
```

### Install Development
1. Instal opensipkd-base
```
    $ git clone git+https://git.opensipkd.com/aa.gusti/opensipkd-base.git 
    atau
    $ git clone git+https://github.com/cendekia-mu/opensipkd-base.git 
```    
2. Install opensipkd-simkel 
```
    $ git clone git+https://github.com/cendekia-mu/simkel.git
```

3. Install::
```    
    $ ./env/bin/pip install opensipkd-base/
    $ ./env/bin/pip install simkel/
```    

### Tambahkan  konfigurasi::
    ```
    [main]
    pyramid.includes =
        ...
        simkel

    [alembic_simkel]
    script_location = simkel:alembic
    sqlalchemy.url = postgresql://user:password@server:port/db
    ```

### Inisialisasi database::

        $ ~/env/bin/alembic -c live.ini -n alembic_simkel upgrade head

## B. Jalankan web server::

    $ ~/env/bin/pserve live.ini

Di web browser buka `http://server:port/simkel <http://server:port/simkel>`_
 
