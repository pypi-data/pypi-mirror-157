import sys
import os
import shutil
import urllib.request
import requests
from latin.bglobals import *
import latin.c_colat1 as c_colat1
import latin.c_colat2 as c_colat2
import latin.c_colat3 as c_colat3
import latin.c_colat4 as c_colat4
import latin.e_pedocerto as e_pedocerto
from latin.e_pedocerto import pros, vow_marked
if not public:
    import latin.i_scrape_old as i_scrape_old
    from latin.i_scrape_old import old_entry
import latin.j_lasla as j_lasla
import latin.j_lasla2 as j_lasla2
import latin.m_stems as m_stems
import latin.o_memorize as o_memorize
import latin.v_reading as v_reading


def elim_useless_files():
    to_del = []
    for l in os.listdir(fold):
        file = f'{fold}{l}'
        if file not in files_used:
            dest = f'{bfold}{l}'
            shutil.copy(file, dest)
            to_del.append(file)
    for x in to_del:
        os.remove(x)
    return


def temp():
    s = 'https://storage.googleapis.com/download/storage/v1/b/deduction4/o/on%20cicero.txt?generation=1656578017964238&alt=media'
    urllib.request.urlopen(s)
    file = f'{fold}hey.txt'
    r = requests.get(s, stream=True, verify=False)
    if r.status_code == 200:
        r.raw.decode_content = 1
        with open(file, 'wb') as f:
            f.write(r.content)
    else:
        p ('failed to download data files')


    return



def begin():
    ins = c_colat1.get_co_lemmas1()
    ins.begin()
    ins = c_colat2.bottom_most()
    ins.begin()
    ins.kind = 'p'
    ins.begin(1)
    ins = c_colat3.colatinus()
    ins.begin()
    ins = c_colat4.bottom_most_a4()
    if public:
        ins.begin_fc(0,'rs')
    else:
        ins.begin_fc()
    ins = e_pedocerto.pedecerto()
    ins.begin()
    ins = e_pedocerto.long_by_pos()
    ins.begin3()
    ins = e_pedocerto.check_vowels()
    ins.begin_f()
    if not public:
        ins = i_scrape_old.bottom_most()
        ins.begin()
    ins = j_lasla.convert2txt()
    ins.kind = ''
    ins.begin_ct()
    ins = j_lasla2.bottom_most_la()
    ins.begin_mcl(1)
    ins = m_stems.bottom()
    ins.begin_st()
    ins = o_memorize.bottom_most()
    ins.begin('all', 'start')
    ins = v_reading.punctuate_lasla()
    ins.begin()


begin()
first = 0
if first:
    elim_useless_files()
