# Struktur Data

## Database 
  SimkelBase
  SimkelDBSession

## User(base.User)
Catatan: Lihat di opensipkd-base

## UserArea(base.UserArea)
Catatan: Lihat di opensipkd-base

## Partner(base.Partner)
Catatan: Lihat di opensipkd-base

## PartnerDocs(base.PartnerDocs)
Catatan: extend dari opensipkd-base

### Tabel: partner_docs
Masih optional 
| Kolom      | Tipe Data   | Keterangan                      |
| ---------- | ----------- | ------------------------------- |
| id         | Integer     | Primary Key                     |
| partner_id | Integer     | FK ke Penduduk.id, NOT NULL     |
| jdoc_id    | Integer     | FK ke JenisDokumen.id, NOT NULL |
| doc_name   | String(128) |                                 |
| status     | Integer     | NOT NULL, default '0'           |

## Departemen(base.models.Departemen)
Catatan: Lihat di opensipkd-base

## Pegawai(base.models.Pegawai)
Catatan: Lihat di opensipkd-base

## Posisi(base.models.PosisiPegawai)
Catatan: Lihat di opensipkd-base

## JenisDokumen

### Tabel: simkel_jdoc
| Kolom | Tipe Data | Keterangan       |
| ----- | --------- | ---------------- |
| id    | Integer   | Primary Key      |
| kode  | String    | (dari NamaModel) |
| nama  | String    | (dari NamaModel) |

## JenisPermohonan(NamaModel)
### Tabel: simkel_jpel
| Kolom   | Tipe Data   | Keterangan                    |
| ------- | ----------- | ----------------------------- |
| id      | Integer     | Primary Key                   |
| kode    | String      | (dari NamaModel)              |
|         |             | digunakan untuk kode sk/surat |
| nama    | String      | (dari NamaModel)              |
| file_nm | String(128) | Report/Format Output          |

## PermohonanField
Digunakan utntuk menambah field-field tertentu sesuai dengan kebutuhan field 
jenis pelayanan dimana akan disimpan datanya dalam tabel permohonan di field
Additional.

### Tabel: simkel_jpel_field
| Kolom   | Tipe Data | Keterangan                         |
| ------- | --------- | ---------------------------------- |
| id      | Integer   | Primary Key                        |
| jpel_id | Integer   | FK ke JenisPermohonan.id, NOT NULL |
| nama    | String    | (dari NamaModel)                   |
| value   | String    | NOT NULL (1 Integer, 2 String)     |

## AlurPermohonan(StandarModel)
### Tabel: simkel_flow
| Kolom         | Tipe Data | Keterangan                         |
| ------------- | --------- | ---------------------------------- |
| id            | Integer   | Primary Key                        |
| jenis_id      | Integer   | FK ke JenisPermohonan.id, NOT NULL |
| no_urut       | Integer   | Urutan dari setiap jenis pelayanan |
| departemen_id |           | FK Departemen.id                   |
|               |           | Mencatat organisasi aktif          |

## Permohonan
### Tabel: simkel_permohonan
| Kolom          | Tipe Data   | Keterangan                         |
| -------------- | ----------- | ---------------------------------- |
| partner_id     | Integer     | FK ke Partner.id, NOT NULL         |
| jenis_id       | Integer     | FK ke JenisPermohonan.id, NOT NULL |
| tgl_permohonan | DateTime    | NOT NULL                           |
| status         | Integer     | NOT NULL, default '0'              |
| additional     | JSON        |                                    |
| reason         | String(128) |                                    |
| create_uid     | Integer     |                                    |
| update_uid     | Integer     |                                    |
| created        | DateTime    |                                    |
| updated        | DateTime    |                                    |


## Penetapan

### Tabel: simkel_sk
| Kolom         | Tipe Data  | Keterangan                            |
| ------------- | ---------- | ------------------------------------- |
| id            | Integer    | Primary Key                           |
| kode          | String     | (dari KodeModel)                      |
| permohonan_id | Integer    | FK ke Permohonan.id, NOT NULL, UNIQUE |
| tgl_ttd       | DateTime   | NOT NULL                              |
| ttd_id        | Integer    | FK ke Penduduk.id, NOT NULL           |
| ttd_id2       | Integer    | FK ke Penduduk.id                     |
| kelurahan     | String(64) |                                       |
| kecamatan     | String(64) |                                       |
| kota          | String(64) |                                       |
| jabatan       | String(64) |                                       |
| jabatan_2     | String(64) |                                       |



## LogApproval

### Tabel: simkel_log_approval
| Kolom         | Tipe Data | Keterangan                    |
| ------------- | --------- | ----------------------------- |
| id            | Integer   | Primary Key                   |
| create_uid    | Integer   |                               |
| created       | DateTime  |                               |
| id_permohonan | Integer   | FK ke Permohonan.id, NOT NULL |
| status        | Integer   |                               |

## GroupLevel

### Tabel: simkel_group_level
| Kolom       | Tipe Data | Keterangan                  |
| ----------- | --------- | --------------------------- |
| id          | Integer   | FK ke Group.id, Primary Key |
| level_id    | Integer   |                             |
| input_level | Integer   |                             |

## GroupLayanan

### Tabel: simkel_group_layanan
| Kolom    | Tipe Data | Keterangan                         |
| -------- | --------- | ---------------------------------- |
| id       | Integer   | Primary Key                        |
| group_id | Integer   | FK ke Group.id, NOT NULL           |
| jpel_id  | Integer   | FK ke JenisPermohonan.id, NOT NULL |


