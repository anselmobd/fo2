import urllib.request
from smb.SMBHandler import SMBHandler


def send_file_smb(
        filename_orig, full_path_dest, filename_dest='', full_path_orig=''):
    '''
    Copy a local file to an remote SMB share folder and file.
    '''
    if filename_dest == '':
        filename_dest = filename_orig
    if full_path_orig == '':
        full_path_orig = '.'

    director = urllib.request.build_opener(SMBHandler)

    orig = '{}/{}'.format(full_path_orig, filename_orig)
    orig_file = open(orig, 'br+')

    dest = '{}/{}'.format(full_path_dest, filename_dest)
    fh = director.open(dest, data=orig_file)

    fh.close()


def send_files_smb(
        filenames_orig, full_path_dest, filename_dest='', full_path_orig=''):
    '''
    Receiving a list of files, call send_file_smb to each file.
    '''
    for filename in filenames_orig:
        send_file_smb(
            filename, full_path,
            filename_dest=filename_dest,
            full_path_orig=full_path_orig)


if __name__ == "__main__":
    # sample use
    full_path = 'smb://{}/{}/{}'.format(
        'servidor', 'documents', 'personal/Anselmo')
    arquivos = ['test1.txt', 'test2.txt']

    send_files_smb(arquivos, full_path)
