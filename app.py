import os
import subprocess
import web
from azure.storage.common import CloudStorageAccount
from azure.storage.blob import BlobPrefix

storage_account='hvsc'
storage_key='dgvR+Z3qoY0sRYjHfOkWDMG7oSrBjLoBgVE4DhAkaRtSjORjBajJc+ddWS4z47N9RV6JWg9UO5Bh0R5Xkek9Gw=='
storage_container='hvsc'

# Use sidplayfp on macOS, sidplay2 on Linux
if subprocess.check_output('uname').startswith('Darwin'):
  sid_player='sidplayfp'
else:
  sid_player='sidplay2'

urls = (
  "/", "main",
  "/dir/(.*)", "dir",
  "/play/(.+)", "play",
  "/stream/(.+)", "stream"
)

app = web.application(urls, globals())
render = web.template.render('templates', globals={'os': os})

storage_client = CloudStorageAccount(storage_account, storage_key)
blob_service = storage_client.create_block_blob_service()

class main:
  def GET(self):
    return "Hello world!"

class dir:
  def GET(self, dir):
    global blob_service

    # Workaround
    # https://github.com/Azure/azure-storage-python/issues/451

    if dir == '':
      bloblist = blob_service.list_blobs(storage_container, delimiter='/')
    else:
      bloblist = blob_service.list_blobs(storage_container, prefix=dir, delimiter='/')

    dirs = []
    files = []

    for f in bloblist:
      if isinstance(f, BlobPrefix):
        dirs.append(f.name)
      else:
        files.append(f.name)
    
    dirs.sort()
    files.sort()
    
    return render.dir(dirs, files)

class play:
  def GET(self, file):
    return render.play(file)

class stream:
  def GET(self, file):
    web.header('Content-type','audio/x-wav')
    sid_file = os.path.basename(file)
    wav_file = os.path.splitext(sid_file)[0] + ".wav"
    if not os.path.isfile(wav_file):
      # Download file from Blob Storage
      blob_service.get_blob_to_path(storage_container, file, sid_file)
      # Convert SID to WAV
      print "generating " + wav_file
      retval = subprocess.call([sid_player, sid_player, '-w' + wav_file, sid_file])
    return open(wav_file, 'rb').read()

if __name__ == "__main__":
  app.run()
