import hashlib

path =  r"video.mp4"

with open(path, 'rb') as opened_file:
    content = opened_file.read()
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha224 = hashlib.sha224()
    sha256 = hashlib.sha256()
    sha484 = hashlib.sha384()
    sha512 = hashlib.sha512()
    
    md5.update(content)
    sha1.update(content)
    sha224.update(content)
    sha256.update(content)
    sha484.update(content)
    sha512.update(content)
    
    print('Result')
    print()
    print('{}: {}'.format(md5.name, md5.hexdigest()))
    print('{}: {}'.format(sha1.name, sha1.hexdigest()))
    print('{}: {}'.format(sha224.name, sha224.hexdigest()))
    print('{}: {}'.format(sha256.name, sha256.hexdigest()))
    print('{}: {}'.format(sha484.name, sha484.hexdigest()))
    print('{}: {}'.format(sha512.name, sha512.hexdigest()))
    