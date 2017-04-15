import requests

# Archomp implements a client to coordinate with the archive
# compressor API provided by orijtech.com. It takes in key value pairs
# describing URLs , and then compresses them together into a zip
# and streams back the .zip body.
# Sample usage:
#   riter, err = client.compress([
#     {"url": "https://orijtech.com/favicon.ico"},
#     {"url": "https://twitter.com/orijtech", "name": "orijtech_frozen_page"},
#     {"url": "https://google.com", "name": "google at %s"%(time.ctime())},
#   ])
#
#   if err is not None:
#     raise err
#   
#   with open('zipped.zip', 'wb') as fzip:
#      for i, rchunk in enumerate(riter):
#        n = fzip.write(rchunk)
#	 print('chunk %d: %d bytes'%(i, n))


class Error(Exception):
  pass

#### Error definitions start ####
errEmptyURL = Error('expecting atleast one non-empty URL')
errNonBlankParams = Error('expecting non-blank params')
#### Error definitions end ####

class Client(object):
  __BaseURL = 'https://archomp.orijtech.com/v1'

  def __init__(self, apiKey=''):
    self.__apiKey = apiKey

  def compress(self, keyvalueList):
    """
    compress takes a list of key-value pairs describing URLs as files
    and requests the archomp API server to compress them and stream
    back the bytes.
    Returns: (iterable_streamer, Error)
      on error: iterable_streamer is None and Error is set
      on success: iterable_streamer returns chunks, Error is None
    """
    if not keyvalueList:
      return errNonBlankParams, None

    alreadySeenURLs = dict()
    nonBlankURLCount = 0
    vettedOptions = []
    for kvp in keyvalueList:
      if not kvp:
        continue

      url = kvp.get('url', None)
      if url is None:
        continue

      trimmedURL = str(url).strip()
      if trimmedURL == '':
        continue

      lastSeenIndex = alreadySeenURLs.get(trimmedURL, None)
      if lastSeenIndex is not None:
        replaceItemOfIndex(vettedOptions, kvp, lastSeenIndex)
        continue

      # Otherwise now count this as a non-blank URL
      nonBlankURLCount += 1

      # Then append it to the vettedOptions and memoize
      vettedOptions.append(kvp)
      alreadySeenURLs[trimmedURL] = len(vettedOptions)

    if nonBlankURLCount < 1:
      return None, errEmptyURLs

    # Next let's make that request
    header = {}
    if self.__apiKey != '':
      header['ARCHOMP_API_KEY'] = self.__apiKey

    header['Content-Type'] = 'application/json'

    req = {'files': vettedOptions}
    res = requests.post(self.__BaseURL, json=req, headers=header, stream=True)
    if res.status_code != 200:
      return None, Error(res.text)

    return res.iter_content(chunk_size=1024 * 256), None

def replaceItemOfIndex(itemsList, value, index):
  """
  The goal here is to replace the item at index
  """
  itemsList[index] = value
