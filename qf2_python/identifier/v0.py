#!/usr/bin/env python

import datetime

def my_exec(x, target, verbose):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].interface(target, verbose)

def get_interface(target, r, verbose):

    bootloader_hash = str()
    x = r[11:43]
    x.reverse()
    for i in x: bootloader_hash += '{:02x}'.format(i)

    runtime_hash = str()
    x = r[51:83]
    x.reverse()
    for i in x: runtime_hash += '{:02x}'.format(i)

    if verbose == True:

        if r[1] == 0:
            print('Board type: BMB7 r1')
        elif r[1] == 1:
            print('Board type: QF2-pre')
        else:
            raise Exception('ERROR - unrecognized board type (', r[1], ')')

        if r[2] == 0:
            print('Active firmware: BOOTLOADER')
        elif r[2] == 1:
            print('Active firmware: RUNTIME')
        else:
            raise Exception('ERROR - unrecognized firmware type (', r[2], ')')

        print('')
            
        j = 0
        for i in range(0, 8):
            j = j + (int(r[3+i]) << (i*8))
        print('Bootloader build timestamp:'+str(j)+'('+str(datetime.datetime.utcfromtimestamp(j))+')')
        print('Bootloader firmware SHA256: '+bootloader_hash)
        print('')

        j = 0
        for i in range(0, 8):
            j = j + (int(r[43+i]) << (i*8))
        print('Runtime build timestamp:'+str(j)+'('+str(datetime.datetime.utcfromtimestamp(j))+')')
        print('Runtime firmware SHA256: '+runtime_hash)
        print('')

    # Break down board identification information to identify correct interface
    if r[1] == 0:
        if r[2] == 0:
            # BMB7 r1 bootloader
            # Decide on packet version interface to use and import the associated module
            instance = my_exec('import qf2_python.bmb7r1_bootloaders.v_'+str(bootloader_hash)+' as x', target, verbose)
        else:
            # BMB7 r1 runtime
            # Decide on packet version interface to use and import the associated module
            instance = my_exec('import qf2_python.bmb7r1_runtimes.v_'+str(runtime_hash)+' as x', target, verbose)
    else:
        if r[2] == 0:
            # QF2-pre bootloader
            # Decide on packet version interface to use and import the associated module
            instance = my_exec('import qf2_python.qf2_pre_bootloaders.v_'+str(bootloader_hash)+' as x', target, verbose)
        else:
            # QF2-pre runtime
            # Decide on packet version interface to use and import the associated module
            instance = my_exec('import qf2_python.qf2_pre_runtimes.v_'+str(runtime_hash)+' as x', target, verbose)

    return instance
