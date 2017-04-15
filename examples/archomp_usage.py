import os
import sys
import time

sys.path.append('..')

import archomp.v1 as archomp

def main():
  client = archomp.Client()
  riter, err = client.compress([
     {"url": "https://orijtech.com/favicon.ico"},
     {"url": "https://twitter.com/orijtech", "name": "orijtech_frozen_page"},
     {"url": "https://google.com", "name": "Google_homepage-at-%s"%(time.ctime())},
  ])

  if err is not None:
    raise err

  try:
    zipname ='zipped.zip'
    with open(zipname, 'wb') as fzip:
      for i, rchunk in enumerate(riter):
        n = fzip.write(rchunk)
        if n is None:
          continue

        sys.stdout.write('chunk %d wrote %d bytes\r'%(i, n))

    print('\nWrote %s to disk!'%(zipname))

  except Exception as ex:
    raise ex

  finally:
    riter.close()
  

if __name__ == '__main__':
  main()
